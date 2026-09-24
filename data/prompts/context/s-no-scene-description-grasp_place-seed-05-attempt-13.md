## Search State

- **Seed**: 5
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0276 | 0.40 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.1737 | 0.37 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0695 | 0.43 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1135 | 0.39 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1235 | 0.37 | ✅ accepted |

**Proposal policy**: task_score is 0.40 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.028) — your mutation base

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

- **Composite score**: -0.028
- **task_score** (E): 0.398
- **fitness_score**: 0.672  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.700

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_object | 1.00 | 1.00 | 0.1404 |
| descend_to_grasp | 1.00 | 1.00 | 0.1205 |
| grasp_object | 1.00 | 1.00 | 0.0129 |
| lift_object | 1.00 | 1.00 | 0.1254 |
| approach_goal | 0.67 | 1.00 | 0.1743 |
| release_object | 1.00 | 1.00 | 0.0215 |
| retract_after_place | 1.00 | 1.00 | 0.1194 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.165) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, 0.016, 0.165)→(0.510, 0.018, 0.045) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.510, 0.018, 0.045)→(0.501, 0.017, 0.035) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 42.667 | 0.147 | 0.193 |
| lift_object | lift | 1.00 / step_budget | (0.501, 0.017, 0.035)→(0.498, 0.017, 0.160) | (0.516, 0.018, 0.026)→(0.509, 0.018, 0.140) | 0.236→0.203 | 1.00 / 22.333 | 0.108 | 0.562 |
| approach_goal | approach | 0.67 / step_budget | (0.498, 0.017, 0.160)→(0.588, 0.156, 0.159) | (0.509, 0.018, 0.140)→(0.602, 0.165, 0.032) | 0.203→0.137 | 1.00 / 9.667 | 91003.212 | 1.146 |
| release_object | release | 1.00 / step_budget | (0.588, 0.156, 0.159)→(0.582, 0.155, 0.179) | (0.602, 0.165, 0.032)→(0.596, 0.167, 0.019) | 0.137→0.150 | 1.00 / 4.000 | 0.131 | 0.476 |
| retract_after_place | retract | 1.00 / step_budget | (0.582, 0.155, 0.179)→(0.580, 0.154, 0.299) | (0.596, 0.167, 0.019)→(0.596, 0.167, 0.019) | 0.150→0.150 | 1.00 / 4.000 | 0.123 | 0.131 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.564
- phase_score: 0.671
- phase_breakdown.reach_grasp_score: 0.851
- phase_breakdown.lift_object_score: 0.589
- phase_breakdown.place_at_goal_score: 0.815
- phase_breakdown.reach_above_object_score: 0.124
- grasp_place_fitness: 0.756

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.756
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.564
- **Median Q (composite search score)**: -0.015
- **K-run variance**: 0.0054
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.329


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53333,"average_solve_count":180.0,"average_success_count":180.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_height":0.19949,"approach_above_object.approach_speed":0.12315,"approach_goal.goal_z_offset":0.0096,"approach_goal.transport_speed":0.20676,"descend_to_grasp.descend_offset_z":0.01002,"descend_to_grasp.descend_speed":0.04511,"lift_object.lift_height":0.14807,"lift_object.lift_speed":0.10394,"release_object.release_time":0.87023,"retract_after_place.retract_height":0.13063,"retract_after_place.retract_speed":0.13212},"optimized_scores":{"best_composite_score":0.05591,"best_fitness_score":0.75591,"best_task_score":0.56396},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":337.0,"contact_point_centroid":[0.5787,0.17124,-0.00326],"force_p95":0.6961,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.77629,"mean_force":0.20581,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58785,0.17156,0.11862]},{"body_a":"world","body_b":"grasp_target","contact_count":157.0,"contact_point_centroid":[0.52714,0.02901,-0.00123],"force_p95":0.34446,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.649,"mean_force":0.09384,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51455,0.02945,0.03588]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11639.0,"contact_point_centroid":[0.56098,0.0871,0.13551],"force_p95":0.11689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36931,"mean_force":0.08065,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55445,0.10533,0.13611]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10796.0,"contact_point_centroid":[0.51508,0.04837,0.09545],"force_p95":0.10916,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30758,"mean_force":0.07544,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51203,0.02929,0.09315]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13461.0,"contact_point_centroid":[0.51564,0.01074,0.09221],"force_p95":0.10011,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29321,"mean_force":0.0624,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51202,0.02929,0.09119]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10811.0,"contact_point_centroid":[0.56075,0.12667,0.13523],"force_p95":0.11977,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27196,"mean_force":0.08562,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55592,0.10786,0.13514]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03077,-0.0021],"force_p95":0.15293,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21113,"mean_force":0.1306,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51756,0.02965,0.03556]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":542.0,"contact_point_centroid":[0.59689,0.15501,0.10235],"force_p95":0.12859,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1964,"mean_force":0.09023,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59245,0.17304,0.10689]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":541.0,"contact_point_centroid":[0.59533,0.19148,0.1027],"force_p95":0.13011,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19164,"mean_force":0.09151,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59245,0.17304,0.10689]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5276.0,"contact_point_centroid":[0.51741,0.01054,0.03608],"force_p95":0.06745,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16851,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.5163,0.02957,0.03413]},{"body_a":"world","body_b":"grasp_target","contact_count":2288.0,"contact_point_centroid":[0.57721,0.17121,-0.00199],"force_p95":0.12504,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14772,"mean_force":0.1227,"phase_index":6.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.5845,0.17049,0.18353]},{"body_a":"world","body_b":"grasp_target","contact_count":1068.0,"contact_point_centroid":[0.5305,0.03079,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.51032,0.01266,0.26651]},{"body_a":"world","body_b":"grasp_target","contact_count":2504.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52261,0.02803,0.13811]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4215.0,"contact_point_centroid":[0.51686,0.04889,0.03695],"force_p95":0.08159,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08432,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51631,0.02957,0.03414]}],"total_contact_groups":14},"final_pose_error":0.01714,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57721,0.17121,0.02602],"final_tcp_position":[0.58499,0.17058,0.24472],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.77629,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":268.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1068.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.52289,0.0261,0.23388],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20805,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":626.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2504.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.52501,0.03014,0.04412],"tcp_start":[0.52289,0.0261,0.23388],"tcp_to_object_dist_end":0.01893,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53044,0.03014,0.02563],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18409,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15117,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11291.0,"raw_peak_contact_force":0.21113,"tcp_end":[0.51627,0.02956,0.0341],"tcp_start":[0.52501,0.03014,0.04412],"tcp_to_object_dist_end":0.01652,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":819.0,"n_steps_budget":900.0,"object_pos_end":[0.52537,0.03022,0.14921],"object_pos_start":[0.53044,0.03014,0.02563],"object_to_goal_dist_end":0.17177,"object_to_goal_dist_start":0.18409,"object_z_max":0.14909,"peak_contact_force":0.10981,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24414.0,"raw_peak_contact_force":0.649,"subtask_id":"lift_object","tcp_end":[0.51245,0.02931,0.16934],"tcp_start":[0.51627,0.02956,0.0341],"tcp_to_object_dist_end":0.02393,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":998.0,"n_steps_budget":1000.0,"object_pos_end":[0.59761,0.17399,0.07681],"object_pos_start":[0.52537,0.03022,0.14921],"object_to_goal_dist_end":0.03186,"object_to_goal_dist_start":0.17177,"object_z_max":0.14924,"peak_contact_force":0.1288,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22450.0,"raw_peak_contact_force":0.36931,"subtask_id":"place_at_goal","tcp_end":[0.59461,0.17351,0.11064],"tcp_start":[0.51245,0.02931,0.16934],"tcp_to_object_dist_end":0.03396,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5767,0.17117,0.02636],"object_pos_start":[0.59761,0.17399,0.07681],"object_to_goal_dist_end":0.08573,"object_to_goal_dist_start":0.03186,"object_z_max":0.07681,"peak_contact_force":0.14745,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1420.0,"raw_peak_contact_force":0.77629,"tcp_end":[0.58772,0.17151,0.131],"tcp_start":[0.59461,0.17351,0.11064],"tcp_to_object_dist_end":0.10521,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":572.0,"n_steps_budget":630.0,"object_pos_end":[0.57721,0.17121,0.02602],"object_pos_start":[0.5767,0.17117,0.02636],"object_to_goal_dist_end":0.08592,"object_to_goal_dist_start":0.08573,"object_z_max":0.02636,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2288.0,"raw_peak_contact_force":0.14772,"tcp_end":[0.58499,0.17058,0.24472],"tcp_start":[0.58772,0.17151,0.131],"tcp_to_object_dist_end":0.21884,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5dcdc1a4e2a8d4c3bb30f9ac92fb306bea0b16a8f449f4d02b0333754e50f910`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93846,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_height":0.05148,"approach_above_object.approach_speed":0.16544,"approach_goal.goal_z_offset":-0.01813,"approach_goal.transport_speed":0.21839,"descend_to_grasp.descend_offset_z":0.01104,"descend_to_grasp.descend_speed":0.06188,"lift_object.lift_height":0.13018,"lift_object.lift_speed":0.06404,"release_object.release_time":0.72649,"retract_after_place.retract_height":0.11164,"retract_after_place.retract_speed":0.09331},"optimized_scores":{"best_composite_score":-0.12328,"best_fitness_score":0.57672,"best_task_score":0.20839},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":194.0,"contact_point_centroid":[0.57573,0.14594,-0.00712],"force_p95":1.35146,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.64436,"mean_force":0.42318,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55559,0.13079,0.19833]},{"body_a":"world","body_b":"grasp_target","contact_count":169.0,"contact_point_centroid":[0.50045,-0.01534,-0.00112],"force_p95":0.31411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50741,"mean_force":0.09261,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4878,-0.0153,0.03769]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8925.0,"contact_point_centroid":[0.52027,0.0311,0.16464],"force_p95":0.12749,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29939,"mean_force":0.089,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51467,0.04993,0.16409]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18883.0,"contact_point_centroid":[0.48741,0.00355,0.08519],"force_p95":0.09123,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28727,"mean_force":0.05416,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48515,-0.01528,0.08393]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16260.0,"contact_point_centroid":[0.48675,-0.03438,0.08691],"force_p95":0.10236,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27883,"mean_force":0.06156,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48514,-0.01528,0.08491]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10817.0,"contact_point_centroid":[0.52177,0.06962,0.16409],"force_p95":0.09847,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20484,"mean_force":0.07453,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51538,0.05137,0.16467]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01576,-0.00203],"force_p95":0.13373,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15725,"mean_force":0.12543,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49076,-0.01533,0.03737]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57786,0.15015,-0.00191],"force_p95":0.13466,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13895,"mean_force":0.1204,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55426,0.13463,0.20216]},{"body_a":"world","body_b":"grasp_target","contact_count":2332.0,"contact_point_centroid":[0.50382,-0.01567,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.49862,-0.0072,0.19483]},{"body_a":"world","body_b":"grasp_target","contact_count":2652.0,"contact_point_centroid":[0.57786,0.15016,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":6.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.55051,0.13355,0.26941]},{"body_a":"world","body_b":"grasp_target","contact_count":620.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49759,-0.01499,0.06762]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5325.0,"contact_point_centroid":[0.49045,0.00374,0.03811],"force_p95":0.06639,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09733,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48954,-0.01531,0.03607]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4150.0,"contact_point_centroid":[0.48917,-0.03459,0.03881],"force_p95":0.07878,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09377,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48954,-0.01531,0.03608]},{"body_a":"left_finger","body_b":"right_finger","contact_count":8.0,"contact_point_centroid":[0.55853,0.13512,0.20212],"force_p95":0.01637,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01637,"mean_force":0.01613,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55779,0.13512,0.20015]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.55747,0.1354,0.20002],"force_p95":0.01442,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01503,"mean_force":0.01114,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55671,0.13538,0.19781]}],"total_contact_groups":15},"final_pose_error":0.01365,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.57786,0.15016,0.01602],"final_tcp_position":[0.55097,0.13361,0.32036],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273008.96538,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":584.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2332.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.49921,-0.01462,0.09022],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06437,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":155.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":620.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.498,-0.01537,0.04517],"tcp_start":[0.49921,-0.01462,0.09022],"tcp_to_object_dist_end":0.02002,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5037,-0.01573,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31241,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13371,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11275.0,"raw_peak_contact_force":0.15725,"tcp_end":[0.48951,-0.01531,0.03604],"tcp_start":[0.498,-0.01537,0.04517],"tcp_to_object_dist_end":0.01746,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49512,-0.01573,0.12051],"object_pos_start":[0.5037,-0.01573,0.02587],"object_to_goal_dist_end":0.25689,"object_to_goal_dist_start":0.31241,"object_z_max":0.12038,"peak_contact_force":0.10565,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35312.0,"raw_peak_contact_force":0.50741,"subtask_id":"lift_object","tcp_end":[0.48531,-0.01527,0.14101],"tcp_start":[0.48951,-0.01531,0.03604],"tcp_to_object_dist_end":0.02274,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57744,0.14803,0.01613],"object_pos_start":[0.49512,-0.01573,0.12051],"object_to_goal_dist_end":0.2355,"object_to_goal_dist_start":0.25689,"object_z_max":0.1574,"peak_contact_force":273008.96538,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":19944.0,"raw_peak_contact_force":1.64436,"subtask_id":"place_at_goal","tcp_end":[0.55789,0.13534,0.20024],"tcp_start":[0.48531,-0.01527,0.14101],"tcp_to_object_dist_end":0.18557,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57786,0.15016,0.01602],"object_pos_start":[0.57744,0.14803,0.01613],"object_to_goal_dist_end":0.23525,"object_to_goal_dist_start":0.2355,"object_z_max":0.01705,"peak_contact_force":0.12264,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.13895,"tcp_end":[0.55289,0.13422,0.22222],"tcp_start":[0.55789,0.13534,0.20024],"tcp_to_object_dist_end":0.20832,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.57786,0.15016,0.01602],"object_pos_start":[0.57786,0.15016,0.01602],"object_to_goal_dist_end":0.23525,"object_to_goal_dist_start":0.23525,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2652.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.55097,0.13361,0.32036],"tcp_start":[0.55289,0.13422,0.22222],"tcp_to_object_dist_end":0.30598,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `53da4dc33bcb1151bde99c46f4ec5d44dda63d23acc62ec623c12d4d0fb32574`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0219,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_height":0.13404,"approach_above_object.approach_speed":0.10342,"approach_goal.goal_z_offset":0.02906,"approach_goal.transport_speed":0.24497,"descend_to_grasp.descend_offset_z":0.01053,"descend_to_grasp.descend_speed":0.10719,"lift_object.lift_height":0.1479,"lift_object.lift_speed":0.09606,"release_object.release_time":0.49878,"retract_after_place.retract_height":0.16232,"retract_after_place.retract_speed":0.11333},"optimized_scores":{"best_composite_score":-0.01548,"best_fitness_score":0.68452,"best_task_score":0.42251},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":68.0,"contact_point_centroid":[0.62672,0.17618,-0.00693],"force_p95":1.41367,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.4239,"mean_force":0.73494,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.61137,0.15888,0.16519]},{"body_a":"world","body_b":"grasp_target","contact_count":150.0,"contact_point_centroid":[0.50954,0.03773,-0.00123],"force_p95":0.35701,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52981,"mean_force":0.08904,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49697,0.03809,0.0372]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.63219,0.17875,-0.00258],"force_p95":0.17992,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51273,"mean_force":0.12662,"phase_index":5.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60802,0.1588,0.16529]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10483.0,"contact_point_centroid":[0.55239,0.07396,0.16457],"force_p95":0.13316,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32706,"mean_force":0.08209,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54528,0.09203,0.16589]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11656.0,"contact_point_centroid":[0.49715,0.05702,0.09746],"force_p95":0.10953,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30579,"mean_force":0.07422,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49442,0.03789,0.09515]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14774.0,"contact_point_centroid":[0.49796,0.01936,0.09373],"force_p95":0.1002,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28616,"mean_force":0.06042,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4944,0.03789,0.09283]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9859.0,"contact_point_centroid":[0.55542,0.11608,0.16557],"force_p95":0.11982,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22297,"mean_force":0.08548,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55039,0.09723,0.1658]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03969,-0.00213],"force_p95":0.1586,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21024,"mean_force":0.13203,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49988,0.03833,0.03667]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5033.0,"contact_point_centroid":[0.50031,0.01922,0.03682],"force_p95":0.0739,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17859,"mean_force":0.04304,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49865,0.03823,0.03532]},{"body_a":"world","body_b":"grasp_target","contact_count":1676.0,"contact_point_centroid":[0.51251,0.03972,-0.00192],"force_p95":0.13424,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.50273,0.01731,0.23574]},{"body_a":"world","body_b":"grasp_target","contact_count":3312.0,"contact_point_centroid":[0.63219,0.17858,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12265,"mean_force":0.12263,"phase_index":6.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.604,0.1575,0.25423]},{"body_a":"world","body_b":"grasp_target","contact_count":1556.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50612,0.03716,0.10754]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4219.0,"contact_point_centroid":[0.49892,0.05753,0.03807],"force_p95":0.08369,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08863,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49865,0.03823,0.03533]}],"total_contact_groups":13},"final_pose_error":0.01615,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.63219,0.17858,0.01602],"final_tcp_position":[0.60497,0.15768,0.33092],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.4239,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":420.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1676.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.50766,0.03563,0.17145],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14557,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":389.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1556.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.5072,0.03891,0.04477],"tcp_start":[0.50766,0.03563,0.17145],"tcp_to_object_dist_end":0.0195,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5125,0.03891,0.02556],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21299,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15622,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11052.0,"raw_peak_contact_force":0.21024,"tcp_end":[0.49862,0.03822,0.03529],"tcp_start":[0.5072,0.03891,0.04477],"tcp_to_object_dist_end":0.01697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":873.0,"n_steps_budget":960.0,"object_pos_end":[0.50696,0.03897,0.14968],"object_pos_start":[0.5125,0.03891,0.02556],"object_to_goal_dist_end":0.18001,"object_to_goal_dist_start":0.21299,"object_z_max":0.14958,"peak_contact_force":0.10846,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26580.0,"raw_peak_contact_force":0.52981,"subtask_id":"lift_object","tcp_end":[0.49485,0.03792,0.17112],"tcp_start":[0.49862,0.03822,0.03529],"tcp_to_object_dist_end":0.02464,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63144,0.17274,0.00188],"object_pos_start":[0.50696,0.03897,0.14968],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.18001,"object_z_max":0.14972,"peak_contact_force":0.54263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20410.0,"raw_peak_contact_force":1.4239,"subtask_id":"place_at_goal","tcp_end":[0.61228,0.15989,0.16514],"tcp_start":[0.49485,0.03792,0.17112],"tcp_to_object_dist_end":0.16488,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63219,0.17857,0.01602],"object_pos_start":[0.63144,0.17274,0.00188],"object_to_goal_dist_end":0.12923,"object_to_goal_dist_start":0.1432,"object_z_max":0.01662,"peak_contact_force":0.12264,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":800.0,"raw_peak_contact_force":0.51273,"tcp_end":[0.60642,0.15829,0.18467],"tcp_start":[0.61228,0.15989,0.16514],"tcp_to_object_dist_end":0.17181,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":828.0,"n_steps_budget":900.0,"object_pos_end":[0.63219,0.17858,0.01602],"object_pos_start":[0.63219,0.17857,0.01602],"object_to_goal_dist_end":0.12923,"object_to_goal_dist_start":0.12923,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3312.0,"raw_peak_contact_force":0.12265,"tcp_end":[0.60497,0.15768,0.33092],"tcp_start":[0.60642,0.15829,0.18467],"tcp_to_object_dist_end":0.31677,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```