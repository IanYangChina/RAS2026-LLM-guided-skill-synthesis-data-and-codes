## Search State

- **Seed**: 5
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.1737 | 0.37 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0695 | 0.43 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1135 | 0.39 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1235 | 0.37 | ✅ accepted |
| 8 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |

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

## Current Skill (Q=-0.174) — your mutation base

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
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    place_z_offset:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: place_at_goal

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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: -0.174
- **task_score** (E): 0.372
- **fitness_score**: 0.656  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.830

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_object | 1.00 | 1.00 | 0.1501 |
| descend_to_grasp | 1.00 | 1.00 | 0.1067 |
| grasp_object | 1.00 | 1.00 | 0.0128 |
| lift_object | 1.00 | 1.00 | 0.1115 |
| approach_goal | 0.67 | 1.00 | 0.0900 |
| descend_to_place | 0.33 | 1.00 | 0.0809 |
| release_object | 1.00 | 1.00 | 0.0205 |
| retract_after_place | 0.67 | 1.00 | 0.0903 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.154) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, 0.016, 0.154)→(0.510, 0.018, 0.048) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.510, 0.018, 0.048)→(0.502, 0.017, 0.038) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 42.667 | 0.147 | 0.192 |
| lift_object | lift | 1.00 / step_budget | (0.502, 0.017, 0.038)→(0.498, 0.017, 0.150) | (0.516, 0.018, 0.026)→(0.508, 0.018, 0.128) | 0.236→0.201 | 1.00 / 28.333 | 0.094 | 0.493 |
| approach_goal | approach | 0.67 / step_budget | (0.570, 0.123, 0.189)→(0.611, 0.186, 0.233) | (0.508, 0.018, 0.128)→(0.570, 0.126, 0.095) | 0.201→0.113 | 1.00 / 8.667 | 91001.701 | 1.343 |
| descend_to_place | descend | 0.33 / step_budget | (0.611, 0.186, 0.233)→(0.638, 0.181, 0.309) | (0.578, 0.140, 0.016)→(0.578, 0.140, 0.016) | 0.166→0.166 | 1.00 / 9.000 | 0.123 | 296.200 |
| release_object | release | 1.00 / step_budget | (0.638, 0.181, 0.309)→(0.637, 0.180, 0.329) | (0.578, 0.140, 0.016)→(0.578, 0.140, 0.016) | 0.166→0.166 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_after_place | retract | 0.67 / step_budget | (0.637, 0.180, 0.329)→(0.654, 0.176, 0.412) | (0.578, 0.140, 0.016)→(0.578, 0.140, 0.016) | 0.166→0.166 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.537
- phase_score: 0.317
- phase_breakdown.reach_grasp_score: 0.870
- phase_breakdown.lift_object_score: 0.691
- phase_breakdown.place_at_goal_score: 0.000
- phase_breakdown.reach_above_object_score: 0.319
- grasp_place_fitness: 0.741

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.741
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.537
- **Median Q (composite search score)**: -0.150
- **K-run variance**: 0.0065
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.310


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":8.0,"average_failure_rate":0.04878,"average_mean_iterations":14.4939,"average_solve_count":164.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_height":0.15018,"approach_above_object.approach_speed":0.13512,"approach_goal.goal_approach_z":0.07171,"approach_goal.transport_speed":0.19891,"descend_to_grasp.descend_offset_z":0.01171,"descend_to_grasp.descend_speed":0.12727,"descend_to_place.place_speed":0.16169,"descend_to_place.place_z_offset":0.02268,"lift_object.lift_height":0.12933,"lift_object.lift_speed":0.10073,"release_object.release_time":0.61148,"retract_after_place.retract_height":0.12792,"retract_after_place.retract_speed":0.08075},"optimized_scores":{"best_composite_score":-0.08931,"best_fitness_score":0.74069,"best_task_score":0.53655},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":17.0,"contact_point_centroid":[0.68961,0.33071,-0.00227],"force_p95":781.24072,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":888.59987,"mean_force":304.11524,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61569,0.26805,0.02731]},{"body_a":"world","body_b":"grasp_target","contact_count":690.0,"contact_point_centroid":[0.60415,0.16336,-0.00335],"force_p95":0.63521,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.14935,"mean_force":0.17591,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.60481,0.18414,0.16963]},{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.52753,0.02891,-0.0012],"force_p95":0.37489,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53034,"mean_force":0.08945,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51456,0.02947,0.03772]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9786.0,"contact_point_centroid":[0.51481,0.04839,0.08977],"force_p95":0.10817,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31149,"mean_force":0.07387,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51194,0.0293,0.08737]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12230.0,"contact_point_centroid":[0.51524,0.01072,0.08633],"force_p95":0.10068,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29049,"mean_force":0.0609,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51194,0.0293,0.08526]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15776.0,"contact_point_centroid":[0.56655,0.09723,0.15845],"force_p95":0.11766,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22279,"mean_force":0.08269,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56057,0.11534,0.16036]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14210.0,"contact_point_centroid":[0.56648,0.13664,0.15934],"force_p95":0.12497,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20979,"mean_force":0.09115,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56209,0.1179,0.16075]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03078,-0.0021],"force_p95":0.15223,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20922,"mean_force":0.13045,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5175,0.02966,0.03732]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5278.0,"contact_point_centroid":[0.51737,0.01055,0.03786],"force_p95":0.06767,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1484,"mean_force":0.04111,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51625,0.02958,0.0359]},{"body_a":"world","body_b":"grasp_target","contact_count":1504.0,"contact_point_centroid":[0.5305,0.03079,-0.00191],"force_p95":0.13505,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.51075,0.01336,0.24303]},{"body_a":"world","body_b":"grasp_target","contact_count":1676.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52306,0.0287,0.11552]},{"body_a":"world","body_b":"grasp_target","contact_count":2880.0,"contact_point_centroid":[0.60412,0.16315,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.68145,0.18903,0.31814]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.60412,0.16315,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.69021,0.16964,0.40217]},{"body_a":"world","body_b":"grasp_target","contact_count":3264.0,"contact_point_centroid":[0.60412,0.16315,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.72511,0.1618,0.43315]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4212.0,"contact_point_centroid":[0.51682,0.0489,0.0387],"force_p95":0.08175,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08424,"mean_force":0.05178,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51625,0.02958,0.0359]},{"body_a":"left_finger","body_b":"right_finger","contact_count":422.0,"contact_point_centroid":[0.6064,0.18507,0.17223],"force_p95":0.01423,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01647,"mean_force":0.0111,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.60566,0.18506,0.17001]}],"total_contact_groups":18},"final_pose_error":0.09602,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60412,0.16315,0.01602],"final_tcp_position":[0.74263,0.15835,0.46776],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":888.59987,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":377.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1504.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.52381,0.02741,0.18656],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16072,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":419.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1676.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.52494,0.03015,0.04589],"tcp_start":[0.52381,0.02741,0.18656],"tcp_to_object_dist_end":0.02065,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53045,0.03018,0.02563],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18405,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15051,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11290.0,"raw_peak_contact_force":0.20922,"tcp_end":[0.51622,0.02958,0.03586],"tcp_start":[0.52494,0.03015,0.04589],"tcp_to_object_dist_end":0.01754,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.5251,0.02997,0.1324],"object_pos_start":[0.53045,0.03018,0.02563],"object_to_goal_dist_end":0.16887,"object_to_goal_dist_start":0.18405,"object_z_max":0.13229,"peak_contact_force":0.09912,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22161.0,"raw_peak_contact_force":0.53034,"subtask_id":"lift_object","tcp_end":[0.51223,0.02931,0.15257],"tcp_start":[0.51622,0.02958,0.03586],"tcp_to_object_dist_end":0.02394,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1662.0,"n_steps_budget":1000.0,"object_pos_end":[0.59381,0.16573,0.13367],"object_pos_start":[0.5251,0.02997,0.1324],"object_to_goal_dist_end":0.02964,"object_to_goal_dist_start":0.16887,"object_z_max":0.13367,"peak_contact_force":0.12259,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31098.0,"raw_peak_contact_force":1.14935,"subtask_id":"place_at_goal","tcp_end":[0.60669,0.18621,0.17048],"tcp_start":[0.59017,0.16494,0.16934],"tcp_to_object_dist_end":0.04405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":720.0,"n_steps_budget":1000.0,"object_pos_end":[0.60412,0.16315,0.01602],"object_pos_start":[0.60412,0.16315,0.01602],"object_to_goal_dist_end":0.09339,"object_to_goal_dist_start":0.09339,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6010.0,"raw_peak_contact_force":888.59987,"subtask_id":"place_at_goal","tcp_end":[0.68787,0.17004,0.39869],"tcp_start":[0.60669,0.18621,0.17048],"tcp_to_object_dist_end":0.39179,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60412,0.16315,0.01602],"object_pos_start":[0.60412,0.16315,0.01602],"object_to_goal_dist_end":0.09339,"object_to_goal_dist_start":0.09339,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.69185,0.16958,0.42057],"tcp_start":[0.68787,0.17004,0.39869],"tcp_to_object_dist_end":0.414,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":816.0,"n_steps_budget":990.0,"object_pos_end":[0.60412,0.16315,0.01602],"object_pos_start":[0.60412,0.16315,0.01602],"object_to_goal_dist_end":0.09339,"object_to_goal_dist_start":0.09339,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3264.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.74263,0.15835,0.46776],"tcp_start":[0.69185,0.16958,0.42057],"tcp_to_object_dist_end":0.47252,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5dcdc1a4e2a8d4c3bb30f9ac92fb306bea0b16a8f449f4d02b0333754e50f910`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":20.0,"average_failure_rate":0.12422,"average_mean_iterations":28.43478,"average_solve_count":161.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_height":0.07159,"approach_above_object.approach_speed":0.14281,"approach_goal.goal_approach_z":0.11817,"approach_goal.transport_speed":0.09855,"descend_to_grasp.descend_offset_z":0.01696,"descend_to_grasp.descend_speed":0.09271,"descend_to_place.place_speed":0.12351,"descend_to_place.place_z_offset":0.0154,"lift_object.lift_height":0.13508,"lift_object.lift_speed":0.1076,"release_object.release_time":0.80355,"retract_after_place.retract_height":0.10645,"retract_after_place.retract_speed":0.10814},"optimized_scores":{"best_composite_score":-0.28185,"best_fitness_score":0.54815,"best_task_score":0.16225},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":5495.0,"contact_point_centroid":[0.51505,0.06337,-0.00219],"force_p95":0.12364,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.70362,"mean_force":0.13186,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54044,0.09732,0.26517]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.50035,-0.0154,-0.00116],"force_p95":0.25263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44146,"mean_force":0.07938,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48825,-0.01533,0.04353]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5795.0,"contact_point_centroid":[0.49939,0.02252,0.17867],"force_p95":0.11443,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30242,"mean_force":0.07559,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49238,0.00415,0.17893]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12503.0,"contact_point_centroid":[0.48867,0.00343,0.09496],"force_p95":0.09777,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28418,"mean_force":0.06045,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4857,-0.01531,0.09358]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10607.0,"contact_point_centroid":[0.48814,-0.03436,0.0974],"force_p95":0.10444,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27151,"mean_force":0.06931,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48569,-0.01531,0.09514]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5188.0,"contact_point_centroid":[0.49838,-0.015,0.17931],"force_p95":0.12237,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23023,"mean_force":0.07965,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49224,0.00386,0.17865]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01577,-0.00203],"force_p95":0.1331,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15665,"mean_force":0.12546,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49105,-0.01535,0.04322]},{"body_a":"world","body_b":"grasp_target","contact_count":2184.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.49868,-0.00712,0.20509]},{"body_a":"world","body_b":"grasp_target","contact_count":768.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49767,-0.01495,0.08041]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51507,0.06342,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59219,0.19178,0.35374]},{"body_a":"world","body_b":"grasp_target","contact_count":1248.0,"contact_point_centroid":[0.51507,0.06342,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.59239,0.19139,0.41566]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5329.0,"contact_point_centroid":[0.49066,0.00372,0.04391],"force_p95":0.06667,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0961,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48984,-0.01534,0.04192]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4146.0,"contact_point_centroid":[0.48935,-0.03461,0.04459],"force_p95":0.07897,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09212,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48984,-0.01534,0.04192]},{"body_a":"left_finger","body_b":"right_finger","contact_count":5723.0,"contact_point_centroid":[0.54239,0.0994,0.26925],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01653,"mean_force":0.01041,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54151,0.09939,0.26706]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.59366,0.19232,0.35284],"force_p95":0.01091,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01092,"mean_force":0.01003,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59283,0.1923,0.35034]}],"total_contact_groups":15},"final_pose_error":0.02,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.51507,0.06342,0.01602],"final_tcp_position":[0.59343,0.1917,0.45966],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9749.03281,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":547.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2184.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.49936,-0.01452,0.11026],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08436,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":192.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":768.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.49823,-0.01541,0.05105],"tcp_start":[0.49936,-0.01452,0.11026],"tcp_to_object_dist_end":0.02565,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50371,-0.01578,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31244,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13308,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11275.0,"raw_peak_contact_force":0.15665,"tcp_end":[0.48981,-0.01534,0.04189],"tcp_start":[0.49823,-0.01541,0.05105],"tcp_to_object_dist_end":0.02122,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":731.0,"n_steps_budget":810.0,"object_pos_end":[0.49731,-0.01584,0.13938],"object_pos_start":[0.50371,-0.01578,0.02587],"object_to_goal_dist_end":0.24735,"object_to_goal_dist_start":0.31244,"object_z_max":0.13926,"peak_contact_force":0.10295,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23254.0,"raw_peak_contact_force":0.44146,"subtask_id":"lift_object","tcp_end":[0.48602,-0.01531,0.16452],"tcp_start":[0.48981,-0.01534,0.04189],"tcp_to_object_dist_end":0.02757,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1916.0,"n_steps_budget":1000.0,"object_pos_end":[0.51507,0.06342,0.01602],"object_pos_start":[0.49731,-0.01584,0.13938],"object_to_goal_dist_end":0.27279,"object_to_goal_dist_start":0.24735,"object_z_max":0.16331,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22201.0,"raw_peak_contact_force":1.70362,"subtask_id":"place_at_goal","tcp_end":[0.59332,0.19232,0.35335],"tcp_start":[0.51898,0.05708,0.2306],"tcp_to_object_dist_end":0.3695,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.51507,0.06342,0.01602],"object_pos_start":[0.51507,0.06342,0.01602],"object_to_goal_dist_end":0.27279,"object_to_goal_dist_start":0.27279,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"place_at_goal","tcp_end":[0.59332,0.19232,0.35335],"tcp_start":[0.59332,0.19232,0.35335],"tcp_to_object_dist_end":0.3695,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51507,0.06342,0.01602],"object_pos_start":[0.51507,0.06342,0.01602],"object_to_goal_dist_end":0.27279,"object_to_goal_dist_start":0.27279,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59203,0.19153,0.37316],"tcp_start":[0.59332,0.19232,0.35335],"tcp_to_object_dist_end":0.38715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":312.0,"n_steps_budget":630.0,"object_pos_end":[0.51507,0.06342,0.01602],"object_pos_start":[0.51507,0.06342,0.01602],"object_to_goal_dist_end":0.27279,"object_to_goal_dist_start":0.27279,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1248.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59343,0.1917,0.45966],"tcp_start":[0.59203,0.19153,0.37316],"tcp_to_object_dist_end":0.46842,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `53da4dc33bcb1151bde99c46f4ec5d44dda63d23acc62ec623c12d4d0fb32574`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":20.0,"average_failure_rate":0.12579,"average_mean_iterations":28.4717,"average_solve_count":159.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_height":0.1288,"approach_above_object.approach_speed":0.19998,"approach_goal.goal_approach_z":0.04073,"approach_goal.transport_speed":0.19358,"descend_to_grasp.descend_offset_z":0.01199,"descend_to_grasp.descend_speed":0.12639,"descend_to_place.place_speed":0.11869,"descend_to_place.place_z_offset":0.01943,"lift_object.lift_height":0.11231,"lift_object.lift_speed":0.05861,"release_object.release_time":0.72918,"retract_after_place.retract_height":0.13388,"retract_after_place.retract_speed":0.14856},"optimized_scores":{"best_composite_score":-0.14988,"best_fitness_score":0.68012,"best_task_score":0.41656},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1486.0,"contact_point_centroid":[0.61635,0.19433,-0.00262],"force_p95":0.31734,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.17724,"mean_force":0.14846,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.62475,0.17301,0.17222]},{"body_a":"world","body_b":"grasp_target","contact_count":202.0,"contact_point_centroid":[0.50779,0.0374,-0.00124],"force_p95":0.32429,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50683,"mean_force":0.09837,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49665,0.03805,0.0386]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.49465,0.05706,0.08652],"force_p95":0.08352,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29522,"mean_force":0.05845,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4942,0.03786,0.08377]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20154.0,"contact_point_centroid":[0.55325,0.07918,0.14848],"force_p95":0.13265,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2925,"mean_force":0.06553,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55057,0.098,0.1488]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21692.0,"contact_point_centroid":[0.55649,0.12246,0.15124],"force_p95":0.10765,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28644,"mean_force":0.05941,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55615,0.10369,0.15069]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20778.0,"contact_point_centroid":[0.49607,0.01893,0.08437],"force_p95":0.07785,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2794,"mean_force":0.04926,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4942,0.03786,0.08286]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.0397,-0.00213],"force_p95":0.15839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20933,"mean_force":0.132,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49984,0.03831,0.03821]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5036.0,"contact_point_centroid":[0.50028,0.01921,0.03837],"force_p95":0.07396,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18015,"mean_force":0.04304,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49862,0.03821,0.03686]},{"body_a":"world","body_b":"grasp_target","contact_count":1588.0,"contact_point_centroid":[0.51251,0.03972,-0.00191],"force_p95":0.13466,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.50282,0.01738,0.23323]},{"body_a":"world","body_b":"grasp_target","contact_count":1456.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50609,0.0372,0.10582]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.61629,0.19455,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62807,0.17847,0.17503]},{"body_a":"world","body_b":"grasp_target","contact_count":1732.0,"contact_point_centroid":[0.61629,0.19455,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.62452,0.17719,0.25045]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4216.0,"contact_point_centroid":[0.49889,0.05752,0.03962],"force_p95":0.0837,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08752,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49862,0.03821,0.03687]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1284.0,"contact_point_centroid":[0.627,0.17431,0.17497],"force_p95":0.012,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01635,"mean_force":0.01066,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.62615,0.17429,0.17284]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.6314,0.17938,0.17442],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.00994,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.63074,0.17937,0.17226]}],"total_contact_groups":15},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61629,0.19455,0.01602],"final_tcp_position":[0.62516,0.1773,0.30807],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":273004.85886,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":398.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1588.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.50766,0.03571,0.16641],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14053,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":364.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1456.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.50714,0.0389,0.04631],"tcp_start":[0.50766,0.03571,0.16641],"tcp_to_object_dist_end":0.021,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51251,0.03894,0.02556],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21297,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15603,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11052.0,"raw_peak_contact_force":0.20933,"tcp_end":[0.49859,0.03821,0.03683],"tcp_start":[0.50714,0.0389,0.04631],"tcp_to_object_dist_end":0.01793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5015,0.03865,0.11269],"object_pos_start":[0.51251,0.03894,0.02556],"object_to_goal_dist_end":0.18671,"object_to_goal_dist_start":0.21297,"object_z_max":0.11259,"peak_contact_force":0.07934,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37980.0,"raw_peak_contact_force":0.50683,"subtask_id":"lift_object","tcp_end":[0.49436,0.03787,0.13175],"tcp_start":[0.49859,0.03821,0.03683],"tcp_to_object_dist_end":0.02037,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1788.0,"n_steps_budget":1000.0,"object_pos_end":[0.60138,0.14903,0.13497],"object_pos_start":[0.5015,0.03865,0.11269],"object_to_goal_dist_end":0.03659,"object_to_goal_dist_start":0.18671,"object_z_max":0.13497,"peak_contact_force":273004.85886,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":44616.0,"raw_peak_contact_force":1.17724,"subtask_id":"place_at_goal","tcp_end":[0.63202,0.17971,0.17543],"tcp_start":[0.6002,0.14772,0.16786],"tcp_to_object_dist_end":0.0593,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.61629,0.19455,0.01602],"object_pos_start":[0.61629,0.19455,0.01602],"object_to_goal_dist_end":0.13136,"object_to_goal_dist_start":0.13136,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"place_at_goal","tcp_end":[0.63202,0.17971,0.17543],"tcp_start":[0.63202,0.17971,0.17543],"tcp_to_object_dist_end":0.16087,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61629,0.19455,0.01602],"object_pos_start":[0.61629,0.19455,0.01602],"object_to_goal_dist_end":0.13136,"object_to_goal_dist_start":0.13136,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62657,0.17794,0.19404],"tcp_start":[0.63202,0.17971,0.17543],"tcp_to_object_dist_end":0.17908,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":433.0,"n_steps_budget":600.0,"object_pos_end":[0.61629,0.19455,0.01602],"object_pos_start":[0.61629,0.19455,0.01602],"object_to_goal_dist_end":0.13136,"object_to_goal_dist_start":0.13136,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1732.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62516,0.1773,0.30807],"tcp_start":[0.62657,0.17794,0.19404],"tcp_to_object_dist_end":0.29269,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```