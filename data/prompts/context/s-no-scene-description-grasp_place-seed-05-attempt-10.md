## Search State

- **Seed**: 5
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1135 | 0.39 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1235 | 0.37 | ✅ accepted |
| 8 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 7 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 6 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |

**Proposal policy**: task_score is 0.39 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.114) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_above_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.15
- id: reach_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.02
  weight: 0.15
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.2
- id: place_at_goal
  target_entity: object
  metric: goal_progress
  weight: 0.5
phases:
- id: approach_above_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: none
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
      - 0.03
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: reach_above_object
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: tcp
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    descend_offset_z:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: reach_grasp
- id: grasp_object
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
    orientation:
      mode: none
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
- id: lift_object
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
      distance: 0.12
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: lift_object
- id: approach_goal
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
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    goal_approach_z:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.06
      - 0.25
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: place_at_goal
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
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_offset_z:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    place_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: place_at_goal
- id: release_object
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: none
  retries:
    max_attempts: 0
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
- id: retract_from_place
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
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    retract_speed:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=tcp, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - descend_offset_z: status=consumed; consumers=target.offset.z (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.12, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - goal_approach_z: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_offset_z: status=consumed; consumers=target.offset.z (replace)
    - place_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **retract_from_place** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - retract_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: -0.114
- **task_score** (E): 0.386
- **fitness_score**: 0.666  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.780

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_object | 1.00 | 1.00 | 0.1251 |
| descend_to_grasp | 1.00 | 1.00 | 0.1351 |
| grasp_object | 1.00 | 1.00 | 0.0129 |
| lift_object | 0.67 | 1.00 | 0.1202 |
| approach_goal | 0.67 | 0.67 | 0.1664 |
| descend_to_place | 1.00 | 1.00 | 0.0451 |
| release_object | 1.00 | 1.00 | 0.0206 |
| retract_from_place | 1.00 | 1.00 | 0.0916 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.180) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, 0.016, 0.180)→(0.510, 0.018, 0.045) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.510, 0.018, 0.045)→(0.502, 0.017, 0.035) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.237 | 1.00 / 42.667 | 0.147 | 0.194 |
| lift_object | lift | 0.67 / step_budget | (0.502, 0.017, 0.035)→(0.498, 0.017, 0.155) | (0.516, 0.018, 0.026)→(0.509, 0.018, 0.136) | 0.237→0.203 | 1.00 / 27.000 | 0.100 | 0.535 |
| approach_goal | approach | 0.67 / step_budget | (0.498, 0.017, 0.155)→(0.583, 0.147, 0.193) | (0.509, 0.018, 0.136)→(0.592, 0.150, 0.092) | 0.203→0.099 | 0.67 / 8.333 | 0.087 | 0.784 |
| descend_to_place | descend | 1.00 / step_budget | (0.583, 0.147, 0.193)→(0.600, 0.176, 0.190) | (0.592, 0.150, 0.092)→(0.603, 0.164, 0.021) | 0.099→0.150 | 1.00 / 5.667 | 0.352 | 0.832 |
| release_object | release | 1.00 / step_budget | (0.600, 0.176, 0.190)→(0.595, 0.174, 0.210) | (0.603, 0.164, 0.021)→(0.606, 0.165, 0.016) | 0.150→0.155 | 1.00 / 4.000 | 0.123 | 0.519 |
| retract_from_place | retract | 1.00 / step_budget | (0.595, 0.174, 0.210)→(0.593, 0.174, 0.301) | (0.606, 0.165, 0.016)→(0.606, 0.165, 0.016) | 0.155→0.155 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.536
- phase_score: 0.319
- phase_breakdown.reach_grasp_score: 0.851
- phase_breakdown.lift_object_score: 0.661
- phase_breakdown.place_at_goal_score: 0.000
- phase_breakdown.reach_above_object_score: 0.393
- grasp_place_fitness: 0.742

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.742
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.536
- **Median Q (composite search score)**: -0.096
- **K-run variance**: 0.0049
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.305


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `181fdad61feb8a6d3dd6561c82dc2730a5598964bf30fa08b43615687239c379`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `eed1fc17ff57094d5189888f0dc8540ea7c165c4c73333e7487a550c7ded377e`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.87582,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_height":0.13957,"approach_above_object.approach_speed":0.08994,"approach_goal.goal_approach_z":0.07102,"approach_goal.transport_speed":0.18714,"descend_to_grasp.descend_offset_z":0.01005,"descend_to_grasp.descend_speed":0.11705,"descend_to_place.place_offset_z":0.02329,"descend_to_place.place_speed":0.11671,"lift_object.lift_height":0.13803,"lift_object.lift_speed":0.09997,"retract_from_place.retract_height":0.12693,"retract_from_place.retract_speed":0.09572},"optimized_scores":{"best_composite_score":-0.03812,"best_fitness_score":0.74188,"best_task_score":0.53636},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":779.0,"contact_point_centroid":[0.61457,0.18701,-0.003],"force_p95":0.55472,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.31133,"mean_force":0.17025,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58936,0.17188,0.136]},{"body_a":"world","body_b":"grasp_target","contact_count":1.0,"contact_point_centroid":[0.58462,0.1717,-0.0002],"force_p95":0.81132,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.81132,"mean_force":0.81132,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59423,0.17319,0.13589]},{"body_a":"world","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.52753,0.02918,-0.0012],"force_p95":0.38543,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55255,"mean_force":0.09205,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51449,0.02946,0.03607]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10412.0,"contact_point_centroid":[0.51489,0.04838,0.09189],"force_p95":0.10862,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31309,"mean_force":0.07485,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51188,0.02929,0.08955]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13016.0,"contact_point_centroid":[0.51539,0.01073,0.08859],"force_p95":0.10004,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29254,"mean_force":0.06174,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51188,0.02929,0.08755]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11496.0,"contact_point_centroid":[0.55613,0.07853,0.1613],"force_p95":0.12921,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25744,"mean_force":0.08156,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54936,0.09674,0.16203]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":412.0,"contact_point_centroid":[0.59663,0.14896,0.15655],"force_p95":0.1873,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22534,"mean_force":0.13181,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59065,0.16678,0.16131]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03077,-0.0021],"force_p95":0.15268,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2107,"mean_force":0.13054,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51744,0.02966,0.03567]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":561.0,"contact_point_centroid":[0.59496,0.18479,0.15527],"force_p95":0.13666,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19104,"mean_force":0.09615,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59078,0.16708,0.15988]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11142.0,"contact_point_centroid":[0.55819,0.12173,0.16263],"force_p95":0.11389,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18787,"mean_force":0.08291,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55305,0.10293,0.16267]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5277.0,"contact_point_centroid":[0.51733,0.01055,0.03623],"force_p95":0.06751,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16897,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51619,0.02958,0.03425]},{"body_a":"world","body_b":"grasp_target","contact_count":1700.0,"contact_point_centroid":[0.5305,0.03079,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.5107,0.01347,0.2378]},{"body_a":"world","body_b":"grasp_target","contact_count":1584.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52307,0.02879,0.10956]},{"body_a":"world","body_b":"grasp_target","contact_count":3012.0,"contact_point_centroid":[0.61517,0.18687,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_from_place","phase_type":"retract","tcp_position_centroid":[0.58466,0.17034,0.2095]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4214.0,"contact_point_centroid":[0.51679,0.0489,0.03705],"force_p95":0.08163,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08424,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5162,0.02958,0.03426]}],"total_contact_groups":15},"final_pose_error":0.01474,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.61517,0.18687,0.01602],"final_tcp_position":[0.58522,0.17044,0.26803],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.31133,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":426.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1700.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.52391,0.02761,0.17618],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15034,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":396.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1584.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.52491,0.03015,0.04425],"tcp_start":[0.52391,0.02761,0.17618],"tcp_to_object_dist_end":0.01908,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53044,0.03015,0.02563],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18408,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.1509,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11291.0,"raw_peak_contact_force":0.2107,"tcp_end":[0.51616,0.02957,0.03422],"tcp_start":[0.52491,0.03015,0.04425],"tcp_to_object_dist_end":0.01667,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.52526,0.03024,0.14003],"object_pos_start":[0.53044,0.03015,0.02563],"object_to_goal_dist_end":0.16983,"object_to_goal_dist_start":0.18408,"object_z_max":0.13992,"peak_contact_force":0.11061,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23575.0,"raw_peak_contact_force":0.55255,"subtask_id":"lift_object","tcp_end":[0.51224,0.02932,0.15967],"tcp_start":[0.51616,0.02957,0.03422],"tcp_to_object_dist_end":0.02358,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59388,0.16598,0.13406],"object_pos_start":[0.52526,0.03024,0.14003],"object_to_goal_dist_end":0.02986,"object_to_goal_dist_start":0.16983,"object_z_max":0.14006,"peak_contact_force":0.13559,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22638.0,"raw_peak_contact_force":0.25744,"subtask_id":"place_at_goal","tcp_end":[0.5903,0.1652,0.16932],"tcp_start":[0.51224,0.02932,0.15967],"tcp_to_object_dist_end":0.03546,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":117.0,"n_steps_budget":1000.0,"object_pos_end":[0.60618,0.18299,0.03058],"object_pos_start":[0.59388,0.16598,0.13406],"object_to_goal_dist_end":0.07778,"object_to_goal_dist_start":0.02986,"object_z_max":0.13406,"peak_contact_force":0.81132,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":974.0,"raw_peak_contact_force":0.81132,"subtask_id":"place_at_goal","tcp_end":[0.59428,0.17327,0.13563],"tcp_start":[0.5903,0.1652,0.16932],"tcp_to_object_dist_end":0.10617,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61517,0.18686,0.01602],"object_pos_start":[0.60618,0.18299,0.03058],"object_to_goal_dist_end":0.09344,"object_to_goal_dist_start":0.07778,"object_z_max":0.03058,"peak_contact_force":0.12262,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":779.0,"raw_peak_contact_force":1.31133,"tcp_end":[0.58771,0.17133,0.1556],"tcp_start":[0.59428,0.17327,0.13563],"tcp_to_object_dist_end":0.1431,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.61517,0.18687,0.01602],"object_pos_start":[0.61517,0.18686,0.01602],"object_to_goal_dist_end":0.09344,"object_to_goal_dist_start":0.09344,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_from_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3012.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58522,0.17044,0.26803],"tcp_start":[0.58771,0.17133,0.1556],"tcp_to_object_dist_end":0.25432,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5dcdc1a4e2a8d4c3bb30f9ac92fb306bea0b16a8f449f4d02b0333754e50f910`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36041,"average_solve_count":197.0,"average_success_count":197.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_height":0.14113,"approach_above_object.approach_speed":0.05303,"approach_goal.goal_approach_z":0.03609,"approach_goal.transport_speed":0.22014,"descend_to_grasp.descend_offset_z":0.01032,"descend_to_grasp.descend_speed":0.10428,"descend_to_place.place_offset_z":0.02144,"descend_to_place.place_speed":0.13679,"lift_object.lift_height":0.19991,"lift_object.lift_speed":0.05939,"retract_from_place.retract_height":0.11468,"retract_from_place.retract_speed":0.04149},"optimized_scores":{"best_composite_score":-0.20645,"best_fitness_score":0.57355,"best_task_score":0.19981},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":371.0,"contact_point_centroid":[0.56769,0.12317,-0.00501],"force_p95":0.9362,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.80365,"mean_force":0.24601,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5486,0.11601,0.22435]},{"body_a":"world","body_b":"grasp_target","contact_count":185.0,"contact_point_centroid":[0.49933,-0.01541,-0.00114],"force_p95":0.33498,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50917,"mean_force":0.09495,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48828,-0.01539,0.03725]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20817.0,"contact_point_centroid":[0.48705,0.00366,0.08432],"force_p95":0.07301,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28596,"mean_force":0.04918,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48575,-0.01536,0.08258]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17978.0,"contact_point_centroid":[0.48638,-0.03455,0.08494],"force_p95":0.07934,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27578,"mean_force":0.05553,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48573,-0.01536,0.08226]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9875.0,"contact_point_centroid":[0.51126,0.01577,0.16591],"force_p95":0.11839,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24513,"mean_force":0.07767,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50758,0.03469,0.16481]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01576,-0.00203],"force_p95":0.13251,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16014,"mean_force":0.12525,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49137,-0.01541,0.03695]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11902.0,"contact_point_centroid":[0.51388,0.05644,0.16734],"force_p95":0.09547,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14394,"mean_force":0.06487,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50922,0.03798,0.1672]},{"body_a":"world","body_b":"grasp_target","contact_count":1596.0,"contact_point_centroid":[0.50382,-0.01567,-0.00191],"force_p95":0.13463,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.49886,-0.00669,0.24041]},{"body_a":"world","body_b":"grasp_target","contact_count":3976.0,"contact_point_centroid":[0.56778,0.12329,-0.00199],"force_p95":0.12285,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12624,"mean_force":0.12269,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56783,0.15639,0.24333]},{"body_a":"world","body_b":"grasp_target","contact_count":1668.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49791,-0.01466,0.11173]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56778,0.12329,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58057,0.18363,0.26088]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.56778,0.12329,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_from_place","phase_type":"retract","tcp_position_centroid":[0.57795,0.18249,0.31322]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5313.0,"contact_point_centroid":[0.49091,0.00366,0.03757],"force_p95":0.06675,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0952,"mean_force":0.04121,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49015,-0.0154,0.03565]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4146.0,"contact_point_centroid":[0.48957,-0.03467,0.03823],"force_p95":0.07904,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09319,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49015,-0.0154,0.03565]},{"body_a":"left_finger","body_b":"right_finger","contact_count":173.0,"contact_point_centroid":[0.55155,0.11951,0.2293],"force_p95":0.0142,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01671,"mean_force":0.01154,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55039,0.1195,0.22692]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4306.0,"contact_point_centroid":[0.56871,0.15639,0.24544],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01031,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56782,0.15637,0.24332]}],"total_contact_groups":17},"final_pose_error":0.04791,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.56778,0.12329,0.01602],"final_tcp_position":[0.57833,0.18255,0.34725],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.80365,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":400.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1596.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.49978,-0.0139,0.17982],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15386,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":417.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1668.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.49866,-0.01546,0.0448],"tcp_start":[0.49978,-0.0139,0.17982],"tcp_to_object_dist_end":0.01948,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.01579,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31245,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13256,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11259.0,"raw_peak_contact_force":0.16014,"tcp_end":[0.49012,-0.0154,0.03562],"tcp_start":[0.49866,-0.01546,0.0448],"tcp_to_object_dist_end":0.01671,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49342,-0.01584,0.11505],"object_pos_start":[0.50369,-0.01579,0.02588],"object_to_goal_dist_end":0.26033,"object_to_goal_dist_start":0.31245,"object_z_max":0.11494,"peak_contact_force":0.07997,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38980.0,"raw_peak_contact_force":0.50917,"subtask_id":"lift_object","tcp_end":[0.48591,-0.01536,0.13259],"tcp_start":[0.49012,-0.0154,0.03562],"tcp_to_object_dist_end":0.01909,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56774,0.12319,0.01645],"object_pos_start":[0.49342,-0.01584,0.11505],"object_to_goal_dist_end":0.24117,"object_to_goal_dist_start":0.26033,"object_z_max":0.17996,"peak_contact_force":0.12547,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22321.0,"raw_peak_contact_force":1.80365,"subtask_id":"place_at_goal","tcp_end":[0.55207,0.12277,0.22931],"tcp_start":[0.48591,-0.01536,0.13259],"tcp_to_object_dist_end":0.21344,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":994.0,"n_steps_budget":1000.0,"object_pos_end":[0.56778,0.12329,0.01602],"object_pos_start":[0.56774,0.12319,0.01645],"object_to_goal_dist_end":0.24156,"object_to_goal_dist_start":0.24117,"object_z_max":0.01645,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8282.0,"raw_peak_contact_force":0.12624,"subtask_id":"place_at_goal","tcp_end":[0.58324,0.18462,0.26005],"tcp_start":[0.55207,0.12277,0.22931],"tcp_to_object_dist_end":0.2521,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56778,0.12329,0.01602],"object_pos_start":[0.56778,0.12329,0.01602],"object_to_goal_dist_end":0.24156,"object_to_goal_dist_start":0.24156,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57966,0.18322,0.28046],"tcp_start":[0.58324,0.18462,0.26005],"tcp_to_object_dist_end":0.2714,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56778,0.12329,0.01602],"object_pos_start":[0.56778,0.12329,0.01602],"object_to_goal_dist_end":0.24156,"object_to_goal_dist_start":0.24156,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_from_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57833,0.18255,0.34725],"tcp_start":[0.57966,0.18322,0.28046],"tcp_to_object_dist_end":0.33666,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `53da4dc33bcb1151bde99c46f4ec5d44dda63d23acc62ec623c12d4d0fb32574`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86538,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_height":0.14532,"approach_above_object.approach_speed":0.11836,"approach_goal.goal_approach_z":0.0469,"approach_goal.transport_speed":0.19396,"descend_to_grasp.descend_offset_z":0.01032,"descend_to_grasp.descend_speed":0.07648,"descend_to_place.place_offset_z":0.03846,"descend_to_place.place_speed":0.126,"lift_object.lift_height":0.15114,"lift_object.lift_speed":0.11495,"retract_from_place.retract_height":0.11052,"retract_from_place.retract_speed":0.09402},"optimized_scores":{"best_composite_score":-0.09599,"best_fitness_score":0.68401,"best_task_score":0.42108},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2500.0,"contact_point_centroid":[0.63468,0.18411,-0.00238],"force_p95":0.12972,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.55768,"mean_force":0.14319,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61709,0.16545,0.17384]},{"body_a":"world","body_b":"grasp_target","contact_count":165.0,"contact_point_centroid":[0.50887,0.03751,-0.00131],"force_p95":0.3038,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54372,"mean_force":0.09306,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49686,0.03808,0.03671]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10180.0,"contact_point_centroid":[0.49731,0.05702,0.09668],"force_p95":0.10985,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30696,"mean_force":0.07545,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4945,0.03789,0.0944]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12712.0,"contact_point_centroid":[0.49825,0.01937,0.0928],"force_p95":0.10242,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29261,"mean_force":0.06255,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49448,0.03789,0.09182]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11225.0,"contact_point_centroid":[0.55306,0.07473,0.17287],"force_p95":0.13264,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29028,"mean_force":0.08175,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54611,0.09278,0.1743]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03969,-0.00213],"force_p95":0.15877,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21048,"mean_force":0.13206,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49986,0.03832,0.0364]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10295.0,"contact_point_centroid":[0.55527,0.1159,0.1744],"force_p95":0.1208,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19979,"mean_force":0.08752,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55033,0.09705,0.17475]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5032.0,"contact_point_centroid":[0.5003,0.01922,0.03655],"force_p95":0.07389,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17823,"mean_force":0.04305,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49863,0.03823,0.03506]},{"body_a":"world","body_b":"grasp_target","contact_count":1528.0,"contact_point_centroid":[0.51251,0.03972,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.50276,0.01708,0.24151]},{"body_a":"world","body_b":"grasp_target","contact_count":1752.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50602,0.03698,0.1131]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.63473,0.18429,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61896,0.16942,0.17411]},{"body_a":"world","body_b":"grasp_target","contact_count":2652.0,"contact_point_centroid":[0.63473,0.18429,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_from_place","phase_type":"retract","tcp_position_centroid":[0.61486,0.16805,0.23835]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4219.0,"contact_point_centroid":[0.49891,0.05753,0.03781],"force_p95":0.08363,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08885,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49864,0.03823,0.03506]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2446.0,"contact_point_centroid":[0.61853,0.16604,0.17596],"force_p95":0.0114,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0152,"mean_force":0.01047,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61771,0.16603,0.17377]},{"body_a":"left_finger","body_b":"right_finger","contact_count":230.0,"contact_point_centroid":[0.6224,0.17029,0.17307],"force_p95":0.01089,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01091,"mean_force":0.00976,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62163,0.17028,0.17103]}],"total_contact_groups":15},"final_pose_error":0.01527,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.63473,0.18429,0.01602],"final_tcp_position":[0.61539,0.16814,0.28868],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.55768,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":383.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1528.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.50763,0.03527,0.18279],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15691,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":438.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1752.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.50719,0.03891,0.0445],"tcp_start":[0.50763,0.03527,0.18279],"tcp_to_object_dist_end":0.01925,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5125,0.03891,0.02556],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21299,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15636,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11051.0,"raw_peak_contact_force":0.21048,"tcp_end":[0.4986,0.03822,0.03502],"tcp_start":[0.50719,0.03891,0.0445],"tcp_to_object_dist_end":0.01683,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":772.0,"n_steps_budget":840.0,"object_pos_end":[0.50772,0.03897,0.15173],"object_pos_start":[0.5125,0.03891,0.02556],"object_to_goal_dist_end":0.17956,"object_to_goal_dist_start":0.21299,"object_z_max":0.1516,"peak_contact_force":0.10862,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23057.0,"raw_peak_contact_force":0.54372,"subtask_id":"lift_object","tcp_end":[0.49491,0.03792,0.17299],"tcp_start":[0.4986,0.03822,0.03502],"tcp_to_object_dist_end":0.02485,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61493,0.16039,0.12593],"object_pos_start":[0.50772,0.03897,0.15173],"object_to_goal_dist_end":0.02591,"object_to_goal_dist_start":0.17956,"object_z_max":0.15179,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21520.0,"raw_peak_contact_force":0.29028,"subtask_id":"place_at_goal","tcp_end":[0.6064,0.1538,0.18089],"tcp_start":[0.49491,0.03792,0.17299],"tcp_to_object_dist_end":0.05601,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":686.0,"n_steps_budget":1000.0,"object_pos_end":[0.63473,0.18429,0.01602],"object_pos_start":[0.61493,0.16039,0.12593],"object_to_goal_dist_end":0.12974,"object_to_goal_dist_start":0.02591,"object_z_max":0.12593,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4946.0,"raw_peak_contact_force":1.55768,"subtask_id":"place_at_goal","tcp_end":[0.62295,0.17065,0.17419],"tcp_start":[0.6064,0.1538,0.18089],"tcp_to_object_dist_end":0.15919,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63473,0.18429,0.01602],"object_pos_start":[0.63473,0.18429,0.01602],"object_to_goal_dist_end":0.12974,"object_to_goal_dist_start":0.12974,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1030.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61743,0.16891,0.19327],"tcp_start":[0.62295,0.17065,0.17419],"tcp_to_object_dist_end":0.17876,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.63473,0.18429,0.01602],"object_pos_start":[0.63473,0.18429,0.01602],"object_to_goal_dist_end":0.12974,"object_to_goal_dist_start":0.12974,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_from_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2652.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61539,0.16814,0.28868],"tcp_start":[0.61743,0.16891,0.19327],"tcp_to_object_dist_end":0.27382,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```