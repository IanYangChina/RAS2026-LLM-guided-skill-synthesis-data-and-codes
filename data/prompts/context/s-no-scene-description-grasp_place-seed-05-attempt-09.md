## Search State

- **Seed**: 5
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1235 | 0.37 | ✅ accepted |
| 8 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 7 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 6 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 5 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |

**Proposal policy**: task_score is 0.37 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.123) — your mutation base

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
      - 0.02
      - 0.15
      default: 0.05
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
      - 0.02
      - 0.1
      default: 0.04
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
      - 0.02
      - 0.1
      default: 0.05
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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    goal_approach_z:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.02
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
      - 0.02
      - 0.1
      default: 0.04
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
      - 0.02
      - 0.1
      default: 0.05
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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.01
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

- **Composite score**: -0.123
- **task_score** (E): 0.371
- **fitness_score**: 0.657  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.780

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_object | 1.00 | 1.00 | 0.1266 |
| descend_to_grasp | 1.00 | 1.00 | 0.1311 |
| grasp_object | 1.00 | 1.00 | 0.0128 |
| lift_object | 0.67 | 1.00 | 0.1007 |
| approach_goal | 0.00 | 1.00 | 0.0734 |
| descend_to_place | 0.33 | 1.00 | 0.0746 |
| release_object | 1.00 | 1.00 | 0.0223 |
| retract_from_place | 0.67 | 1.00 | 0.0820 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.178) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, 0.016, 0.178)→(0.510, 0.018, 0.047) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 10.830 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.510, 0.018, 0.047)→(0.502, 0.017, 0.038) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 42.667 | 0.146 | 0.192 |
| lift_object | lift | 0.67 / step_budget | (0.502, 0.017, 0.038)→(0.498, 0.017, 0.138) | (0.516, 0.018, 0.026)→(0.506, 0.018, 0.118) | 0.236→0.203 | 1.00 / 32.333 | 0.087 | 0.518 |
| approach_goal | approach | 0.00 / step_budget | (0.498, 0.017, 0.138)→(0.531, 0.073, 0.170) | (0.506, 0.018, 0.118)→(0.536, 0.073, 0.144) | 0.203→0.136 | 1.00 / 28.333 | 0.102 | 0.130 |
| descend_to_place | descend | 0.33 / step_budget | (0.531, 0.073, 0.170)→(0.571, 0.133, 0.171) | (0.536, 0.073, 0.144)→(0.576, 0.129, 0.082) | 0.136→0.112 | 1.00 / 16.333 | 0.115 | 0.677 |
| release_object | release | 1.00 / step_budget | (0.571, 0.133, 0.171)→(0.565, 0.131, 0.192) | (0.576, 0.129, 0.082)→(0.572, 0.127, 0.023) | 0.112→0.158 | 1.00 / 2.667 | 0.145 | 0.773 |
| retract_from_place | retract | 0.67 / step_budget | (0.565, 0.131, 0.192)→(0.563, 0.131, 0.274) | (0.572, 0.127, 0.023)→(0.574, 0.128, 0.019) | 0.158→0.162 | 1.00 / 4.000 | 0.123 | 0.299 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.528
- phase_score: 0.631
- phase_breakdown.reach_grasp_score: 0.850
- phase_breakdown.lift_object_score: 0.569
- phase_breakdown.place_at_goal_score: 0.706
- phase_breakdown.reach_above_object_score: 0.246
- grasp_place_fitness: 0.738

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.738
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.528
- **Median Q (composite search score)**: -0.111
- **K-run variance**: 0.0051
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: approach_goal.goal_approach_z
- **Final σ (mean)**: 0.372


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.8505,"average_solve_count":301.0,"average_success_count":301.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_height":0.16378,"approach_above_object.approach_speed":0.08112,"approach_goal.goal_approach_z":0.09009,"approach_goal.transport_speed":0.02463,"descend_to_grasp.descend_offset_z":0.01007,"descend_to_grasp.descend_speed":0.02365,"descend_to_place.place_offset_z":0.03001,"descend_to_place.place_speed":0.05956,"lift_object.lift_height":0.17373,"lift_object.lift_speed":0.05877,"retract_from_place.retract_height":0.09072,"retract_from_place.retract_speed":0.05768},"optimized_scores":{"best_composite_score":-0.04238,"best_fitness_score":0.73762,"best_task_score":0.52751},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":163.0,"contact_point_centroid":[0.57534,0.15085,-0.00701],"force_p95":0.97526,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.04377,"mean_force":0.40779,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57414,0.14964,0.14265]},{"body_a":"world","body_b":"grasp_target","contact_count":3415.0,"contact_point_centroid":[0.60291,0.15166,-0.00204],"force_p95":0.12307,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58087,"mean_force":0.12553,"phase_index":7.0,"phase_name":"retract_from_place","phase_type":"retract","tcp_position_centroid":[0.57067,0.14867,0.1931]},{"body_a":"world","body_b":"grasp_target","contact_count":212.0,"contact_point_centroid":[0.52497,0.02913,-0.0012],"force_p95":0.36047,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55503,"mean_force":0.10476,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51418,0.02945,0.03584]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.5124,0.04848,0.0834],"force_p95":0.08238,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30881,"mean_force":0.05853,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51174,0.02929,0.08068]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20658.0,"contact_point_centroid":[0.5134,0.01034,0.08128],"force_p95":0.07705,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28828,"mean_force":0.0496,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51175,0.02929,0.07968]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03077,-0.0021],"force_p95":0.15257,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21053,"mean_force":0.1305,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51751,0.02967,0.03557]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5277.0,"contact_point_centroid":[0.51738,0.01055,0.03611],"force_p95":0.06755,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.169,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51626,0.02958,0.03415]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":830.0,"contact_point_centroid":[0.58477,0.13245,0.12967],"force_p95":0.09229,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14035,"mean_force":0.06069,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57856,0.15092,0.13017]},{"body_a":"world","body_b":"grasp_target","contact_count":1448.0,"contact_point_centroid":[0.5305,0.03079,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.51052,0.01316,0.24966]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":778.0,"contact_point_centroid":[0.58342,0.16999,0.12955],"force_p95":0.09629,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13825,"mean_force":0.06515,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57853,0.15091,0.13012]},{"body_a":"world","body_b":"grasp_target","contact_count":2140.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52281,0.02854,0.12138]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12863.0,"contact_point_centroid":[0.56802,0.14432,0.13858],"force_p95":0.10654,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12211,"mean_force":0.07317,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56385,0.12527,0.13778]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15071.0,"contact_point_centroid":[0.56851,0.10603,0.13805],"force_p95":0.08842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11427,"mean_force":0.06286,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56332,0.12445,0.13791]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15804.0,"contact_point_centroid":[0.52863,0.08015,0.13953],"force_p95":0.08842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11016,"mean_force":0.06058,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52724,0.06102,0.13776]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18709.0,"contact_point_centroid":[0.52988,0.0423,0.1384],"force_p95":0.07925,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09542,"mean_force":0.05171,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52726,0.06106,0.13778]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4213.0,"contact_point_centroid":[0.51683,0.0489,0.03696],"force_p95":0.08167,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08425,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51626,0.02959,0.03416]}],"total_contact_groups":16},"final_pose_error":0.0125,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60337,0.15168,0.01602],"final_tcp_position":[0.571,0.14872,0.23323],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.04377,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":363.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1448.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.52359,0.02712,0.19977],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17393,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":535.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2140.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.52495,0.03016,0.04412],"tcp_start":[0.52359,0.02712,0.19977],"tcp_to_object_dist_end":0.01894,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53044,0.03016,0.02563],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18407,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15083,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11290.0,"raw_peak_contact_force":0.21053,"tcp_end":[0.51623,0.02958,0.03412],"tcp_start":[0.52495,0.03016,0.04412],"tcp_to_object_dist_end":0.01656,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51979,0.02995,0.11216],"object_pos_start":[0.53044,0.03016,0.02563],"object_to_goal_dist_end":0.16968,"object_to_goal_dist_start":0.18407,"object_z_max":0.11206,"peak_contact_force":0.07912,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37870.0,"raw_peak_contact_force":0.55503,"subtask_id":"lift_object","tcp_end":[0.5119,0.0293,0.12883],"tcp_start":[0.51623,0.02958,0.03412],"tcp_to_object_dist_end":0.01845,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54764,0.08883,0.1272],"object_pos_start":[0.51979,0.02995,0.11216],"object_to_goal_dist_end":0.10642,"object_to_goal_dist_start":0.16968,"object_z_max":0.12718,"peak_contact_force":0.08749,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34513.0,"raw_peak_contact_force":0.11016,"subtask_id":"place_at_goal","tcp_end":[0.54359,0.08831,0.14974],"tcp_start":[0.5119,0.0293,0.12883],"tcp_to_object_dist_end":0.02291,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58602,0.15156,0.10499],"object_pos_start":[0.54764,0.08883,0.1272],"object_to_goal_dist_end":0.03131,"object_to_goal_dist_start":0.10642,"object_z_max":0.1272,"peak_contact_force":0.0964,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":27934.0,"raw_peak_contact_force":0.12211,"subtask_id":"place_at_goal","tcp_end":[0.58042,0.15132,0.13349],"tcp_start":[0.54359,0.08831,0.14974],"tcp_to_object_dist_end":0.02904,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59017,0.14996,0.02621],"object_pos_start":[0.58602,0.15156,0.10499],"object_to_goal_dist_end":0.08747,"object_to_goal_dist_start":0.03131,"object_z_max":0.10499,"peak_contact_force":0.16902,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1771.0,"raw_peak_contact_force":1.04377,"tcp_end":[0.57403,0.14961,0.1546],"tcp_start":[0.58042,0.15132,0.13349],"tcp_to_object_dist_end":0.1294,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":866.0,"n_steps_budget":990.0,"object_pos_end":[0.60337,0.15168,0.01602],"object_pos_start":[0.59017,0.14996,0.02621],"object_to_goal_dist_end":0.09594,"object_to_goal_dist_start":0.08747,"object_z_max":0.02621,"peak_contact_force":0.12263,"phase_name":"retract_from_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3415.0,"raw_peak_contact_force":0.58087,"tcp_end":[0.571,0.14872,0.23323],"tcp_start":[0.57403,0.14961,0.1546],"tcp_to_object_dist_end":0.21963,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5dcdc1a4e2a8d4c3bb30f9ac92fb306bea0b16a8f449f4d02b0333754e50f910`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.98026,"average_solve_count":304.0,"average_success_count":304.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_height":0.12438,"approach_above_object.approach_speed":0.02851,"approach_goal.goal_approach_z":0.05,"approach_goal.transport_speed":0.03005,"descend_to_grasp.descend_offset_z":0.01425,"descend_to_grasp.descend_speed":0.07142,"descend_to_place.place_offset_z":0.01766,"descend_to_place.place_speed":0.02842,"lift_object.lift_height":0.12494,"lift_object.lift_speed":0.09952,"retract_from_place.retract_height":0.09828,"retract_from_place.retract_speed":0.04742},"optimized_scores":{"best_composite_score":-0.21678,"best_fitness_score":0.56322,"best_task_score":0.18664},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2133.0,"contact_point_centroid":[0.54957,0.09724,-0.00247],"force_p95":0.17029,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.74685,"mean_force":0.14384,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5362,0.09619,0.21144]},{"body_a":"world","body_b":"grasp_target","contact_count":140.0,"contact_point_centroid":[0.5011,-0.01539,-0.0011],"force_p95":0.35476,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51483,"mean_force":0.08072,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48854,-0.01538,0.04126]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12758.0,"contact_point_centroid":[0.48862,0.00343,0.08946],"force_p95":0.09637,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28503,"mean_force":0.05854,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4859,-0.01535,0.08804]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10925.0,"contact_point_centroid":[0.48807,-0.03442,0.0912],"force_p95":0.10402,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27706,"mean_force":0.06666,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48589,-0.01535,0.0889]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4861.0,"contact_point_centroid":[0.52711,0.08398,0.19466],"force_p95":0.10617,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26508,"mean_force":0.07406,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.52052,0.06581,0.19663]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4135.0,"contact_point_centroid":[0.52596,0.04613,0.19524],"force_p95":0.12868,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19487,"mean_force":0.08325,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.52013,0.06496,0.1963]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01577,-0.00203],"force_p95":0.13245,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16074,"mean_force":0.12532,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49133,-0.0154,0.0408]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12217.0,"contact_point_centroid":[0.50616,0.00208,0.17372],"force_p95":0.09969,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15731,"mean_force":0.07535,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50062,0.02088,0.17307]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12577.0,"contact_point_centroid":[0.50712,0.03961,0.17319],"force_p95":0.09629,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14009,"mean_force":0.0738,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50075,0.02111,0.17325]},{"body_a":"world","body_b":"grasp_target","contact_count":1868.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.49875,-0.0068,0.23212]},{"body_a":"world","body_b":"grasp_target","contact_count":1472.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49774,-0.01475,0.10549]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54964,0.09724,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.53995,0.109,0.22066]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54964,0.09724,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_from_place","phase_type":"retract","tcp_position_centroid":[0.5363,0.10814,0.27937]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5330.0,"contact_point_centroid":[0.49086,0.00367,0.04143],"force_p95":0.06678,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09557,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49012,-0.01539,0.0395]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4146.0,"contact_point_centroid":[0.48954,-0.03466,0.04209],"force_p95":0.07909,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09275,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49012,-0.01539,0.0395]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2112.0,"contact_point_centroid":[0.53784,0.09749,0.21427],"force_p95":0.01121,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01634,"mean_force":0.01039,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.53689,0.09749,0.2121]}],"total_contact_groups":17},"final_pose_error":0.02093,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.54964,0.09724,0.01602],"final_tcp_position":[0.53664,0.10817,0.3184],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":32.24495,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":468.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1868.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.49968,-0.01409,0.16315],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1372,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":368.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":32.24495,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1472.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.49857,-0.01546,0.04865],"tcp_start":[0.49968,-0.01409,0.16315],"tcp_to_object_dist_end":0.02324,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5037,-0.0158,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31245,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13247,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11276.0,"raw_peak_contact_force":0.16074,"tcp_end":[0.49009,-0.01539,0.03947],"tcp_start":[0.49857,-0.01546,0.04865],"tcp_to_object_dist_end":0.01924,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.49792,-0.01588,0.12994],"object_pos_start":[0.5037,-0.0158,0.02587],"object_to_goal_dist_end":0.25145,"object_to_goal_dist_start":0.31245,"object_z_max":0.12983,"peak_contact_force":0.10345,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23823.0,"raw_peak_contact_force":0.51483,"subtask_id":"lift_object","tcp_end":[0.48616,-0.01535,0.1525],"tcp_start":[0.49009,-0.01539,0.03947],"tcp_to_object_dist_end":0.02545,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52197,0.05038,0.1644],"object_pos_start":[0.49792,-0.01588,0.12994],"object_to_goal_dist_end":0.17325,"object_to_goal_dist_start":0.25145,"object_z_max":0.16437,"peak_contact_force":0.09888,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24794.0,"raw_peak_contact_force":0.15731,"subtask_id":"place_at_goal","tcp_end":[0.51567,0.05097,0.19416],"tcp_start":[0.48616,-0.01535,0.1525],"tcp_to_object_dist_end":0.03043,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54964,0.09724,0.01602],"object_pos_start":[0.52197,0.05038,0.1644],"object_to_goal_dist_end":0.25179,"object_to_goal_dist_start":0.17325,"object_z_max":0.16849,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":13241.0,"raw_peak_contact_force":1.74685,"subtask_id":"place_at_goal","tcp_end":[0.54337,0.1097,0.21835],"tcp_start":[0.51567,0.05097,0.19416],"tcp_to_object_dist_end":0.20281,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54964,0.09724,0.01602],"object_pos_start":[0.54964,0.09724,0.01602],"object_to_goal_dist_end":0.25179,"object_to_goal_dist_start":0.25179,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53869,0.10869,0.24094],"tcp_start":[0.54337,0.1097,0.21835],"tcp_to_object_dist_end":0.22548,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54964,0.09724,0.01602],"object_pos_start":[0.54964,0.09724,0.01602],"object_to_goal_dist_end":0.25179,"object_to_goal_dist_start":0.25179,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_from_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53664,0.10817,0.3184],"tcp_start":[0.53869,0.10869,0.24094],"tcp_to_object_dist_end":0.30285,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `53da4dc33bcb1151bde99c46f4ec5d44dda63d23acc62ec623c12d4d0fb32574`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29703,"average_solve_count":202.0,"average_success_count":202.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_height":0.13442,"approach_above_object.approach_speed":0.09796,"approach_goal.goal_approach_z":0.11219,"approach_goal.transport_speed":0.05357,"descend_to_grasp.descend_offset_z":0.01454,"descend_to_grasp.descend_speed":0.06858,"descend_to_place.place_offset_z":0.02391,"descend_to_place.place_speed":0.07186,"lift_object.lift_height":0.12569,"lift_object.lift_speed":0.05751,"retract_from_place.retract_height":0.1749,"retract_from_place.retract_speed":0.05571},"optimized_scores":{"best_composite_score":-0.11126,"best_fitness_score":0.66874,"best_task_score":0.3987},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":205.0,"contact_point_centroid":[0.57519,0.13543,-0.00596],"force_p95":1.07171,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.15142,"mean_force":0.32765,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58268,0.13592,0.16965]},{"body_a":"world","body_b":"grasp_target","contact_count":203.0,"contact_point_centroid":[0.50776,0.03755,-0.00124],"force_p95":0.30119,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48528,"mean_force":0.09405,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49672,0.03806,0.04117]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.49471,0.05707,0.08875],"force_p95":0.0836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29203,"mean_force":0.05842,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49429,0.03787,0.086]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20797.0,"contact_point_centroid":[0.49613,0.01893,0.08664],"force_p95":0.07782,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27587,"mean_force":0.04919,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49428,0.03787,0.08511]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03972,-0.00212],"force_p95":0.15736,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20598,"mean_force":0.13179,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49991,0.03832,0.04077]},{"body_a":"world","body_b":"grasp_target","contact_count":3987.0,"contact_point_centroid":[0.56879,0.13512,-0.00199],"force_p95":0.12759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19285,"mean_force":0.12297,"phase_index":7.0,"phase_name":"retract_from_place","phase_type":"retract","tcp_position_centroid":[0.57964,0.1351,0.2245]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5044.0,"contact_point_centroid":[0.50033,0.01921,0.04093],"force_p95":0.07346,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18037,"mean_force":0.04302,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49869,0.03822,0.03943]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13135.0,"contact_point_centroid":[0.56378,0.09158,0.15846],"force_p95":0.12025,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16286,"mean_force":0.07064,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56017,0.10964,0.16052]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10051.0,"contact_point_centroid":[0.56425,0.1299,0.15806],"force_p95":0.12947,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14978,"mean_force":0.09152,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56164,0.11109,0.16048]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":545.0,"contact_point_centroid":[0.59122,0.11913,0.15149],"force_p95":0.12799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1445,"mean_force":0.08865,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58666,0.137,0.15634]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":531.0,"contact_point_centroid":[0.58899,0.15554,0.15154],"force_p95":0.1382,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13969,"mean_force":0.09061,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58658,0.13698,0.1562]},{"body_a":"world","body_b":"grasp_target","contact_count":1684.0,"contact_point_centroid":[0.51251,0.03972,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.5027,0.01729,0.23595]},{"body_a":"world","body_b":"grasp_target","contact_count":1604.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50601,0.03714,0.10987]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17348.0,"contact_point_centroid":[0.51506,0.08021,0.15126],"force_p95":0.08621,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12227,"mean_force":0.05627,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51388,0.06098,0.14942]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20780.0,"contact_point_centroid":[0.51734,0.04274,0.15121],"force_p95":0.07087,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09812,"mean_force":0.0462,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51447,0.06157,0.14994]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4213.0,"contact_point_centroid":[0.49893,0.05752,0.04217],"force_p95":0.08399,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08665,"mean_force":0.05177,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49869,0.03822,0.03943]}],"total_contact_groups":16},"final_pose_error":0.08513,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.56871,0.13512,0.02602],"final_tcp_position":[0.58008,0.13516,0.27054],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.15142,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":422.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1684.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.50767,0.03561,0.17186],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14597,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":401.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1604.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.50717,0.0389,0.04886],"tcp_start":[0.50767,0.03561,0.17186],"tcp_to_object_dist_end":0.02347,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51251,0.03899,0.02556],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21293,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.1551,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11057.0,"raw_peak_contact_force":0.20598,"tcp_end":[0.49866,0.03822,0.03939],"tcp_start":[0.50717,0.0389,0.04886],"tcp_to_object_dist_end":0.01959,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50098,0.03865,0.11231],"object_pos_start":[0.51251,0.03899,0.02556],"object_to_goal_dist_end":0.18713,"object_to_goal_dist_start":0.21293,"object_z_max":0.11221,"peak_contact_force":0.07925,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38000.0,"raw_peak_contact_force":0.48528,"subtask_id":"lift_object","tcp_end":[0.49445,0.03788,0.13361],"tcp_start":[0.49866,0.03822,0.03939],"tcp_to_object_dist_end":0.02229,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53714,0.08081,0.14038],"object_pos_start":[0.50098,0.03865,0.11231],"object_to_goal_dist_end":0.12888,"object_to_goal_dist_start":0.18713,"object_z_max":0.14034,"peak_contact_force":0.11828,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38128.0,"raw_peak_contact_force":0.12227,"subtask_id":"place_at_goal","tcp_end":[0.53323,0.08048,0.16667],"tcp_start":[0.49445,0.03788,0.13361],"tcp_to_object_dist_end":0.02658,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59229,0.13707,0.12514],"object_pos_start":[0.53714,0.08081,0.14038],"object_to_goal_dist_end":0.05383,"object_to_goal_dist_start":0.12888,"object_z_max":0.14038,"peak_contact_force":0.12691,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":23186.0,"raw_peak_contact_force":0.16286,"subtask_id":"place_at_goal","tcp_end":[0.58852,0.13739,0.15993],"tcp_start":[0.53323,0.08048,0.16667],"tcp_to_object_dist_end":0.035,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57513,0.13526,0.02665],"object_pos_start":[0.59229,0.13707,0.12514],"object_to_goal_dist_end":0.13472,"object_to_goal_dist_start":0.05383,"object_z_max":0.12514,"peak_contact_force":0.14353,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1281.0,"raw_peak_contact_force":1.15142,"tcp_end":[0.58261,0.1359,0.18073],"tcp_start":[0.58852,0.13739,0.15993],"tcp_to_object_dist_end":0.15426,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56871,0.13512,0.02602],"object_pos_start":[0.57513,0.13526,0.02665],"object_to_goal_dist_end":0.13793,"object_to_goal_dist_start":0.13472,"object_z_max":0.02675,"peak_contact_force":0.12263,"phase_name":"retract_from_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3987.0,"raw_peak_contact_force":0.19285,"tcp_end":[0.58008,0.13516,0.27054],"tcp_start":[0.58261,0.1359,0.18073],"tcp_to_object_dist_end":0.24479,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```