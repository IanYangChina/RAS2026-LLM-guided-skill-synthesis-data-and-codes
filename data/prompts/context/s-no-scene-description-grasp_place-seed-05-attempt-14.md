## Search State

- **Seed**: 5
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1136 | 0.39 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0276 | 0.40 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.1737 | 0.37 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0695 | 0.43 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1135 | 0.39 | ✅ accepted |

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

- **Composite score**: -0.114
- **task_score** (E): 0.388
- **fitness_score**: 0.666  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.780

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_object | 1.00 | 1.00 | 0.1567 |
| descend_to_grasp | 1.00 | 1.00 | 0.1019 |
| grasp_object | 1.00 | 1.00 | 0.0129 |
| lift_object | 1.00 | 1.00 | 0.1093 |
| approach_goal | 0.67 | 1.00 | 0.1595 |
| descend_to_place | 1.00 | 1.00 | 0.0662 |
| release_object | 1.00 | 1.00 | 0.0208 |
| retract_after_place | 1.00 | 1.00 | 0.1199 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.017, 0.147) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, 0.017, 0.147)→(0.510, 0.018, 0.046) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.510, 0.018, 0.046)→(0.502, 0.017, 0.036) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.237 | 1.00 / 43.000 | 0.147 | 0.197 |
| lift_object | lift | 1.00 / step_budget | (0.502, 0.017, 0.036)→(0.497, 0.017, 0.145) | (0.516, 0.018, 0.026)→(0.509, 0.018, 0.125) | 0.237→0.204 | 1.00 / 22.667 | 0.107 | 0.538 |
| approach_goal | approach | 0.67 / step_budget | (0.497, 0.017, 0.145)→(0.577, 0.139, 0.193) | (0.509, 0.018, 0.125)→(0.578, 0.129, 0.095) | 0.204→0.111 | 1.00 / 13.667 | 3249.736 | 0.638 |
| descend_to_place | descend | 1.00 / step_budget | (0.577, 0.139, 0.193)→(0.600, 0.176, 0.156) | (0.578, 0.129, 0.095)→(0.588, 0.142, 0.032) | 0.111→0.144 | 1.00 / 11.000 | 94251.257 | 0.581 |
| release_object | release | 1.00 / step_budget | (0.600, 0.176, 0.156)→(0.594, 0.174, 0.176) | (0.588, 0.142, 0.032)→(0.581, 0.142, 0.019) | 0.144→0.159 | 1.00 / 4.000 | 0.131 | 0.329 |
| retract_after_place | retract | 1.00 / step_budget | (0.594, 0.174, 0.176)→(0.592, 0.173, 0.296) | (0.581, 0.142, 0.019)→(0.582, 0.142, 0.019) | 0.159→0.159 | 1.00 / 4.000 | 0.123 | 0.131 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.565
- phase_score: 0.321
- phase_breakdown.reach_grasp_score: 0.850
- phase_breakdown.lift_object_score: 0.690
- phase_breakdown.place_at_goal_score: 0.001
- phase_breakdown.reach_above_object_score: 0.368
- grasp_place_fitness: 0.756

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.756
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.565
- **Median Q (composite search score)**: -0.095
- **K-run variance**: 0.0067
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.361


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56338,"average_solve_count":213.0,"average_success_count":213.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_height":0.14273,"approach_above_object.approach_speed":0.11634,"approach_goal.goal_approach_z":0.07288,"approach_goal.transport_speed":0.21969,"descend_to_grasp.descend_offset_z":0.01013,"descend_to_grasp.descend_speed":0.03181,"descend_to_place.place_speed":0.13921,"descend_to_place.place_z_offset":-0.01264,"lift_object.lift_height":0.14295,"lift_object.lift_speed":0.07018,"retract_after_place.retract_height":0.13409,"retract_after_place.retract_speed":0.15699},"optimized_scores":{"best_composite_score":-0.02367,"best_fitness_score":0.75633,"best_task_score":0.56511},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":362.0,"contact_point_centroid":[0.57983,0.17303,-0.0029],"force_p95":0.5687,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74291,"mean_force":0.18826,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58766,0.17244,0.10822]},{"body_a":"world","body_b":"grasp_target","contact_count":182.0,"contact_point_centroid":[0.52642,0.0289,-0.00123],"force_p95":0.32709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56571,"mean_force":0.09836,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5143,0.02945,0.03584]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":487.0,"contact_point_centroid":[0.59487,0.19242,0.09179],"force_p95":0.13993,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39946,"mean_force":0.10256,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5922,0.17389,0.09707]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":541.0,"contact_point_centroid":[0.59624,0.15608,0.09174],"force_p95":0.1262,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34876,"mean_force":0.09203,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59227,0.17391,0.09717]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14475.0,"contact_point_centroid":[0.51398,0.04842,0.08689],"force_p95":0.10804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31581,"mean_force":0.06933,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51173,0.02929,0.08469]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18622.0,"contact_point_centroid":[0.5143,0.01069,0.08663],"force_p95":0.09272,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29712,"mean_force":0.05502,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51174,0.02929,0.08565]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1781.0,"contact_point_centroid":[0.596,0.15154,0.13026],"force_p95":0.15753,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22034,"mean_force":0.10746,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59144,0.16925,0.13491]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11239.0,"contact_point_centroid":[0.55594,0.11929,0.15783],"force_p95":0.117,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21214,"mean_force":0.08274,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5514,0.1004,0.15752]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1476.0,"contact_point_centroid":[0.59461,0.18737,0.13215],"force_p95":0.17476,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21078,"mean_force":0.12803,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59135,0.16903,0.13659]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03077,-0.0021],"force_p95":0.15262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21064,"mean_force":0.13052,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51746,0.02966,0.03559]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12792.0,"contact_point_centroid":[0.55516,0.07825,0.15644],"force_p95":0.11685,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19957,"mean_force":0.07375,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54908,0.09654,0.15676]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5277.0,"contact_point_centroid":[0.51734,0.01055,0.03615],"force_p95":0.06753,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16893,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5162,0.02958,0.03417]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.57777,0.17319,-0.00199],"force_p95":0.12478,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14668,"mean_force":0.12269,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.58423,0.17134,0.17552]},{"body_a":"world","body_b":"grasp_target","contact_count":1624.0,"contact_point_centroid":[0.5305,0.03079,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.51065,0.01341,0.23946]},{"body_a":"world","body_b":"grasp_target","contact_count":1820.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52286,0.02874,0.1113]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4214.0,"contact_point_centroid":[0.51679,0.0489,0.03697],"force_p95":0.08165,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08423,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51621,0.02958,0.03418]}],"total_contact_groups":16},"final_pose_error":0.01752,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57777,0.17319,0.02602],"final_tcp_position":[0.58472,0.17142,0.23822],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.74291,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":407.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1624.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.5238,0.02753,0.17936],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15352,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":455.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1820.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.52491,0.03015,0.04416],"tcp_start":[0.5238,0.02753,0.17936],"tcp_to_object_dist_end":0.01899,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53044,0.03015,0.02563],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18408,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15085,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11291.0,"raw_peak_contact_force":0.21064,"tcp_end":[0.51617,0.02958,0.03414],"tcp_start":[0.52491,0.03015,0.04416],"tcp_to_object_dist_end":0.01662,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52314,0.02985,0.12883],"object_pos_start":[0.53044,0.03015,0.02563],"object_to_goal_dist_end":0.1694,"object_to_goal_dist_start":0.18408,"object_z_max":0.12874,"peak_contact_force":0.1064,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33279.0,"raw_peak_contact_force":0.56571,"subtask_id":"lift_object","tcp_end":[0.51205,0.02931,0.14853],"tcp_start":[0.51617,0.02958,0.03414],"tcp_to_object_dist_end":0.02261,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59372,0.16536,0.13565],"object_pos_start":[0.52314,0.02985,0.12883],"object_to_goal_dist_end":0.03155,"object_to_goal_dist_start":0.1694,"object_z_max":0.13565,"peak_contact_force":0.12422,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24031.0,"raw_peak_contact_force":0.21214,"subtask_id":"place_at_goal","tcp_end":[0.59005,0.16476,0.17004],"tcp_start":[0.51205,0.02931,0.14853],"tcp_to_object_dist_end":0.03459,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":204.0,"n_steps_budget":1000.0,"object_pos_end":[0.59826,0.17501,0.06518],"object_pos_start":[0.59372,0.16536,0.13565],"object_to_goal_dist_end":0.04318,"object_to_goal_dist_start":0.03155,"object_z_max":0.13565,"peak_contact_force":0.14307,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3257.0,"raw_peak_contact_force":0.22034,"subtask_id":"place_at_goal","tcp_end":[0.59481,0.17455,0.10155],"tcp_start":[0.59005,0.16476,0.17004],"tcp_to_object_dist_end":0.03654,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57686,0.17324,0.02618],"object_pos_start":[0.59826,0.17501,0.06518],"object_to_goal_dist_end":0.08571,"object_to_goal_dist_start":0.04318,"object_z_max":0.06518,"peak_contact_force":0.14715,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1390.0,"raw_peak_contact_force":0.74291,"tcp_end":[0.58748,0.17238,0.1214],"tcp_start":[0.59481,0.17455,0.10155],"tcp_to_object_dist_end":0.09581,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.57777,0.17319,0.02602],"object_pos_start":[0.57686,0.17324,0.02618],"object_to_goal_dist_end":0.08561,"object_to_goal_dist_start":0.08571,"object_z_max":0.02618,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.14668,"subtask_id":"place_at_goal","tcp_end":[0.58472,0.17142,0.23822],"tcp_start":[0.58748,0.17238,0.1214],"tcp_to_object_dist_end":0.21232,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5dcdc1a4e2a8d4c3bb30f9ac92fb306bea0b16a8f449f4d02b0333754e50f910`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64571,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_height":0.10746,"approach_above_object.approach_speed":0.05342,"approach_goal.goal_approach_z":0.06713,"approach_goal.transport_speed":0.21306,"descend_to_grasp.descend_offset_z":0.01355,"descend_to_grasp.descend_speed":0.09831,"descend_to_place.place_speed":0.13985,"descend_to_place.place_z_offset":-0.02077,"lift_object.lift_height":0.1043,"lift_object.lift_speed":0.08977,"retract_after_place.retract_height":0.16029,"retract_after_place.retract_speed":0.13448},"optimized_scores":{"best_composite_score":-0.22159,"best_fitness_score":0.55841,"best_task_score":0.17537},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1834.0,"contact_point_centroid":[0.54061,0.07577,-0.00254],"force_p95":0.21609,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.48979,"mean_force":0.15349,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53065,0.08047,0.21242]},{"body_a":"world","body_b":"grasp_target","contact_count":156.0,"contact_point_centroid":[0.50103,-0.01544,-0.00111],"force_p95":0.3106,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49347,"mean_force":0.08342,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48838,-0.01538,0.04031]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4268.0,"contact_point_centroid":[0.50135,-0.0072,0.15214],"force_p95":0.14174,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34081,"mean_force":0.09349,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49602,0.0116,0.15127]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12240.0,"contact_point_centroid":[0.48822,0.00346,0.08073],"force_p95":0.09371,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29572,"mean_force":0.05629,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48579,-0.01535,0.07919]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10397.0,"contact_point_centroid":[0.48768,-0.03445,0.08215],"force_p95":0.10373,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28658,"mean_force":0.06462,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48577,-0.01535,0.07971]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5418.0,"contact_point_centroid":[0.50347,0.03218,0.15289],"force_p95":0.10008,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19433,"mean_force":0.0749,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49718,0.01402,0.15334]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01576,-0.00203],"force_p95":0.13248,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16069,"mean_force":0.1253,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4913,-0.0154,0.03996]},{"body_a":"world","body_b":"grasp_target","contact_count":2040.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.49868,-0.00694,0.22329]},{"body_a":"world","body_b":"grasp_target","contact_count":1232.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49776,-0.01484,0.09661]},{"body_a":"world","body_b":"grasp_target","contact_count":2828.0,"contact_point_centroid":[0.54087,0.07701,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56491,0.15063,0.22488]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54087,0.07701,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57891,0.18251,0.22025]},{"body_a":"world","body_b":"grasp_target","contact_count":2768.0,"contact_point_centroid":[0.54087,0.07701,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.57611,0.18133,0.30702]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5330.0,"contact_point_centroid":[0.49084,0.00367,0.0406],"force_p95":0.06678,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09556,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49008,-0.01539,0.03866]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4146.0,"contact_point_centroid":[0.48952,-0.03466,0.04125],"force_p95":0.07909,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09289,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49009,-0.01539,0.03866]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1839.0,"contact_point_centroid":[0.53252,0.08267,0.21655],"force_p95":0.01172,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01645,"mean_force":0.01047,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53177,0.08266,0.21438]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.58202,0.18336,0.21857],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.01006,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58109,0.18335,0.21655]}],"total_contact_groups":17},"final_pose_error":0.01677,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.54087,0.07701,0.01602],"final_tcp_position":[0.57715,0.18156,0.38341],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9749.07046,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":511.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2040.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.49955,-0.01427,0.14611],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12017,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":308.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1232.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.49854,-0.01546,0.0478],"tcp_start":[0.49955,-0.01427,0.14611],"tcp_to_object_dist_end":0.02241,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5037,-0.0158,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31245,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13251,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11276.0,"raw_peak_contact_force":0.16069,"tcp_end":[0.49005,-0.01539,0.03863],"tcp_start":[0.49854,-0.01546,0.0478],"tcp_to_object_dist_end":0.01868,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.49813,-0.01583,0.11084],"object_pos_start":[0.5037,-0.0158,0.02588],"object_to_goal_dist_end":0.26086,"object_to_goal_dist_start":0.31245,"object_z_max":0.11075,"peak_contact_force":0.10374,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22793.0,"raw_peak_contact_force":0.49347,"subtask_id":"lift_object","tcp_end":[0.48591,-0.01535,0.13168],"tcp_start":[0.49005,-0.01539,0.03863],"tcp_to_object_dist_end":0.02416,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54087,0.07701,0.01602],"object_pos_start":[0.49813,-0.01583,0.11084],"object_to_goal_dist_end":0.26112,"object_to_goal_dist_start":0.26086,"object_z_max":0.14736,"peak_contact_force":9748.9533,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13359.0,"raw_peak_contact_force":1.48979,"subtask_id":"place_at_goal","tcp_end":[0.54502,0.1086,0.23755],"tcp_start":[0.48591,-0.01535,0.13168],"tcp_to_object_dist_end":0.22381,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":707.0,"n_steps_budget":1000.0,"object_pos_end":[0.54087,0.07701,0.01602],"object_pos_start":[0.54087,0.07701,0.01602],"object_to_goal_dist_end":0.26112,"object_to_goal_dist_start":0.26112,"object_z_max":0.01602,"peak_contact_force":9749.07046,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5894.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.58223,0.18362,0.21941],"tcp_start":[0.54502,0.1086,0.23755],"tcp_to_object_dist_end":0.23333,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54087,0.07701,0.01602],"object_pos_start":[0.54087,0.07701,0.01602],"object_to_goal_dist_end":0.26112,"object_to_goal_dist_start":0.26112,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57771,0.18202,0.23987],"tcp_start":[0.58223,0.18362,0.21941],"tcp_to_object_dist_end":0.24999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":692.0,"n_steps_budget":750.0,"object_pos_end":[0.54087,0.07701,0.01602],"object_pos_start":[0.54087,0.07701,0.01602],"object_to_goal_dist_end":0.26112,"object_to_goal_dist_start":0.26112,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2768.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.57715,0.18156,0.38341],"tcp_start":[0.57771,0.18202,0.23987],"tcp_to_object_dist_end":0.3837,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `53da4dc33bcb1151bde99c46f4ec5d44dda63d23acc62ec623c12d4d0fb32574`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.03571,"average_solve_count":140.0,"average_success_count":140.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_height":0.07863,"approach_above_object.approach_speed":0.16395,"approach_goal.goal_approach_z":0.0398,"approach_goal.transport_speed":0.17678,"descend_to_grasp.descend_offset_z":0.01058,"descend_to_grasp.descend_speed":0.10162,"descend_to_place.place_speed":0.07825,"descend_to_place.place_z_offset":0.01133,"lift_object.lift_height":0.13159,"lift_object.lift_speed":0.08712,"retract_after_place.retract_height":0.11485,"retract_after_place.retract_speed":0.1028},"optimized_scores":{"best_composite_score":-0.09547,"best_fitness_score":0.68453,"best_task_score":0.42304},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2416.0,"contact_point_centroid":[0.62573,0.17524,-0.00232],"force_p95":0.13641,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.40124,"mean_force":0.13971,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61389,0.16256,0.15178]},{"body_a":"world","body_b":"grasp_target","contact_count":174.0,"contact_point_centroid":[0.50917,0.03772,-0.00124],"force_p95":0.31958,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55356,"mean_force":0.08795,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49648,0.03797,0.03698]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11529.0,"contact_point_centroid":[0.4969,0.05691,0.0906],"force_p95":0.10942,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31635,"mean_force":0.07489,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49403,0.03778,0.08827]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14743.0,"contact_point_centroid":[0.49761,0.01927,0.0866],"force_p95":0.10015,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29533,"mean_force":0.06047,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49401,0.03778,0.08571]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":419.0,"contact_point_centroid":[0.60417,0.12836,0.16084],"force_p95":0.18059,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22275,"mean_force":0.12585,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59789,0.146,0.16633]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51258,0.03969,-0.00214],"force_p95":0.16149,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22094,"mean_force":0.13284,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49958,0.03822,0.0365]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11443.0,"contact_point_centroid":[0.54912,0.0712,0.15909],"force_p95":0.13293,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21076,"mean_force":0.08198,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54228,0.08929,0.16038]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10789.0,"contact_point_centroid":[0.5511,0.1122,0.1608],"force_p95":0.11614,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19566,"mean_force":0.08562,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54629,0.09335,0.16113]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5254.0,"contact_point_centroid":[0.49973,0.01911,0.03687],"force_p95":0.06856,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18548,"mean_force":0.04126,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49835,0.03813,0.03516]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":516.0,"contact_point_centroid":[0.60219,0.1644,0.16041],"force_p95":0.14372,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18425,"mean_force":0.09428,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59837,0.14662,0.16543]},{"body_a":"world","body_b":"grasp_target","contact_count":2112.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.50271,0.01797,0.20803]},{"body_a":"world","body_b":"grasp_target","contact_count":916.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50592,0.03759,0.08029]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.62589,0.17522,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61775,0.16886,0.14768]},{"body_a":"world","body_b":"grasp_target","contact_count":2532.0,"contact_point_centroid":[0.62589,0.17522,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.61317,0.16739,0.214]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4234.0,"contact_point_centroid":[0.49873,0.05746,0.03798],"force_p95":0.08307,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09081,"mean_force":0.05175,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49835,0.03813,0.03517]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2275.0,"contact_point_centroid":[0.61582,0.16361,0.15334],"force_p95":0.0112,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01609,"mean_force":0.01051,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61502,0.16359,0.15121]}],"total_contact_groups":17},"final_pose_error":0.0158,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62589,0.17522,0.01602],"final_tcp_position":[0.61366,0.16747,0.26612],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":273004.5563,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":529.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2112.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.50747,0.03657,0.11666],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09083,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":229.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":916.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.50689,0.03881,0.04458],"tcp_start":[0.50747,0.03657,0.11666],"tcp_to_object_dist_end":0.01942,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51249,0.03885,0.02552],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21305,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15883,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11288.0,"raw_peak_contact_force":0.22094,"tcp_end":[0.49832,0.03812,0.03513],"tcp_start":[0.50689,0.03881,0.04458],"tcp_to_object_dist_end":0.01714,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":873.0,"n_steps_budget":960.0,"object_pos_end":[0.50633,0.03887,0.13415],"object_pos_start":[0.51249,0.03885,0.02552],"object_to_goal_dist_end":0.18078,"object_to_goal_dist_start":0.21305,"object_z_max":0.13406,"peak_contact_force":0.10967,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26446.0,"raw_peak_contact_force":0.55356,"subtask_id":"lift_object","tcp_end":[0.49437,0.03781,0.15538],"tcp_start":[0.49832,0.03812,0.03513],"tcp_to_object_dist_end":0.02439,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.6002,0.14471,0.13339],"object_pos_start":[0.50633,0.03887,0.13415],"object_to_goal_dist_end":0.04072,"object_to_goal_dist_start":0.18078,"object_z_max":0.13417,"peak_contact_force":0.13044,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22232.0,"raw_peak_contact_force":0.21076,"subtask_id":"place_at_goal","tcp_end":[0.59597,0.14353,0.17045],"tcp_start":[0.49437,0.03781,0.15538],"tcp_to_object_dist_end":0.03732,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":730.0,"n_steps_budget":1000.0,"object_pos_end":[0.62589,0.17522,0.01602],"object_pos_start":[0.6002,0.14471,0.13339],"object_to_goal_dist_end":0.12904,"object_to_goal_dist_start":0.04072,"object_z_max":0.13339,"peak_contact_force":273004.5563,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5626.0,"raw_peak_contact_force":1.40124,"subtask_id":"place_at_goal","tcp_end":[0.62215,0.17017,0.14773],"tcp_start":[0.59597,0.14353,0.17045],"tcp_to_object_dist_end":0.13186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62589,0.17522,0.01602],"object_pos_start":[0.62589,0.17522,0.01602],"object_to_goal_dist_end":0.12904,"object_to_goal_dist_start":0.12904,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61604,0.16831,0.16687],"tcp_start":[0.62215,0.17017,0.14773],"tcp_to_object_dist_end":0.15133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.62589,0.17522,0.01602],"object_pos_start":[0.62589,0.17522,0.01602],"object_to_goal_dist_end":0.12904,"object_to_goal_dist_start":0.12904,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2532.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_at_goal","tcp_end":[0.61366,0.16747,0.26612],"tcp_start":[0.61604,0.16831,0.16687],"tcp_to_object_dist_end":0.25052,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```