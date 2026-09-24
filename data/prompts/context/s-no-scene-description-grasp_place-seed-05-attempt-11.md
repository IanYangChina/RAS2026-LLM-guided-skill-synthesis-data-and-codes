## Search State

- **Seed**: 5
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0695 | 0.43 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1135 | 0.39 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.1235 | 0.37 | ✅ accepted |
| 8 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |
| 7 | push → release → pull → release → release → grasp → retract → approach | impedance_motion | linear_cartesian | arc_cartesian | — | linear_cartesian | — | linear_cartesian | linear_cartesian | impedance_control | admittance_control | impedance_control | position_control | admittance_control | position_control | position_control | position_control | time_limit | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | -0.3167 | 0.22 | ❌ rejected |

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

- **Composite score**: 0.070
- **task_score** (E): 0.434
- **fitness_score**: 0.690  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.620

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_object | 1.00 | 1.00 | 0.1323 |
| descend_to_grasp | 1.00 | 1.00 | 0.1265 |
| grasp_object | 1.00 | 1.00 | 0.0129 |
| lift_object | 1.00 | 1.00 | 0.1050 |
| approach_goal | 0.33 | 1.00 | 0.1320 |
| descend_to_place | 1.00 | 1.00 | 0.0741 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.172) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, 0.016, 0.172)→(0.510, 0.018, 0.046) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.510, 0.018, 0.046)→(0.502, 0.017, 0.036) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 42.667 | 0.146 | 0.192 |
| lift_object | lift | 1.00 / step_budget | (0.502, 0.017, 0.036)→(0.498, 0.017, 0.141) | (0.516, 0.018, 0.026)→(0.509, 0.018, 0.121) | 0.236→0.202 | 1.00 / 25.000 | 0.105 | 0.523 |
| approach_goal | approach | 0.33 / step_budget | (0.498, 0.017, 0.141)→(0.566, 0.119, 0.174) | (0.509, 0.018, 0.121)→(0.571, 0.119, 0.141) | 0.202→0.077 | 1.00 / 18.333 | 0.124 | 0.216 |
| descend_to_place | descend | 1.00 / step_budget | (0.566, 0.119, 0.174)→(0.594, 0.166, 0.153) | (0.571, 0.119, 0.141)→(0.589, 0.147, 0.029) | 0.077→0.146 | 1.00 / 10.667 | 6503.103 | 1.131 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.696
- phase_score: 0.319
- phase_breakdown.reach_grasp_score: 0.891
- phase_breakdown.lift_object_score: 0.662
- phase_breakdown.place_at_goal_score: 0.000
- phase_breakdown.reach_above_object_score: 0.349
- grasp_place_fitness: 0.818

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.818
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.696
- **Median Q (composite search score)**: 0.065
- **K-run variance**: 0.0106
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: descend_to_grasp.descend_offset_z
- **Final σ (mean)**: 0.312


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94545,"average_solve_count":110.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_height":0.14557,"approach_above_object.approach_speed":0.14491,"approach_goal.goal_approach_z":0.03833,"approach_goal.transport_speed":0.17033,"descend_to_grasp.descend_offset_z":0.01432,"descend_to_grasp.descend_speed":0.14584,"descend_to_place.place_speed":0.12976,"descend_to_place.place_z_offset":-0.01584,"lift_object.lift_height":0.11366,"lift_object.lift_speed":0.08264},"optimized_scores":{"best_composite_score":0.19801,"best_fitness_score":0.81801,"best_task_score":0.69594},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":184.0,"contact_point_centroid":[0.52678,0.0292,-0.00122],"force_p95":0.28275,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51128,"mean_force":0.08805,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51441,0.02945,0.04024]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10742.0,"contact_point_centroid":[0.51461,0.0484,0.0854],"force_p95":0.1074,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31815,"mean_force":0.0727,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51191,0.02929,0.08299]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13517.0,"contact_point_centroid":[0.51504,0.01069,0.08264],"force_p95":0.09879,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29403,"mean_force":0.0595,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51191,0.02929,0.08155]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11316.0,"contact_point_centroid":[0.55207,0.07314,0.13559],"force_p95":0.12123,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27615,"mean_force":0.08237,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54577,0.09131,0.13678]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1437.0,"contact_point_centroid":[0.59117,0.18202,0.10754],"force_p95":0.14635,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25735,"mean_force":0.12226,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58782,0.16364,0.11261]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1701.0,"contact_point_centroid":[0.59214,0.14561,0.10833],"force_p95":0.12939,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23376,"mean_force":0.10404,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5876,0.16327,0.11349]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53054,0.03079,-0.0021],"force_p95":0.15159,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20679,"mean_force":0.13032,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51757,0.02966,0.03997]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10447.0,"contact_point_centroid":[0.55145,0.11186,0.13629],"force_p95":0.12417,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20428,"mean_force":0.08793,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54682,0.09309,0.13677]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5287.0,"contact_point_centroid":[0.51742,0.01054,0.0405],"force_p95":0.0679,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14549,"mean_force":0.04107,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51633,0.02957,0.03855]},{"body_a":"world","body_b":"grasp_target","contact_count":1548.0,"contact_point_centroid":[0.5305,0.03079,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12294,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.51076,0.0134,0.24081]},{"body_a":"world","body_b":"grasp_target","contact_count":1540.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52313,0.02873,0.11484]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4210.0,"contact_point_centroid":[0.51687,0.04889,0.04136],"force_p95":0.08194,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08426,"mean_force":0.05175,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.51633,0.02958,0.03855]}],"total_contact_groups":12},"final_pose_error":0.00992,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5972,0.17286,0.05419],"final_tcp_position":[0.59353,0.17272,0.09245],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":9760.30694,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":388.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1548.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.52384,0.02748,0.18213],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15628,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":385.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1540.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.52498,0.03014,0.04855],"tcp_start":[0.52384,0.02748,0.18213],"tcp_to_object_dist_end":0.0232,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53046,0.03022,0.02563],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18401,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14996,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11297.0,"raw_peak_contact_force":0.20679,"tcp_end":[0.5163,0.02957,0.03851],"tcp_start":[0.52498,0.03014,0.04855],"tcp_to_object_dist_end":0.01915,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.52381,0.02996,0.11832],"object_pos_start":[0.53046,0.03022,0.02563],"object_to_goal_dist_end":0.16803,"object_to_goal_dist_start":0.18401,"object_z_max":0.11823,"peak_contact_force":0.09869,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24443.0,"raw_peak_contact_force":0.51128,"subtask_id":"lift_object","tcp_end":[0.51214,0.0293,0.14079],"tcp_start":[0.5163,0.02957,0.03851],"tcp_to_object_dist_end":0.02533,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58698,0.15517,0.10111],"object_pos_start":[0.52381,0.02996,0.11832],"object_to_goal_dist_end":0.02844,"object_to_goal_dist_start":0.16803,"object_z_max":0.11834,"peak_contact_force":0.13408,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21763.0,"raw_peak_contact_force":0.27615,"subtask_id":"place_at_goal","tcp_end":[0.58376,0.15441,0.13777],"tcp_start":[0.51214,0.0293,0.14079],"tcp_to_object_dist_end":0.03681,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":197.0,"n_steps_budget":1000.0,"object_pos_end":[0.5972,0.17286,0.05419],"object_pos_start":[0.58698,0.15517,0.10111],"object_to_goal_dist_end":0.05437,"object_to_goal_dist_start":0.02844,"object_z_max":0.10111,"peak_contact_force":9760.30694,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3138.0,"raw_peak_contact_force":0.25735,"subtask_id":"place_at_goal","tcp_end":[0.59353,0.17272,0.09245],"tcp_start":[0.58376,0.15441,0.13777],"tcp_to_object_dist_end":0.03843,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5dcdc1a4e2a8d4c3bb30f9ac92fb306bea0b16a8f449f4d02b0333754e50f910`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94215,"average_solve_count":121.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_height":0.13003,"approach_above_object.approach_speed":0.18405,"approach_goal.goal_approach_z":0.05241,"approach_goal.transport_speed":0.0761,"descend_to_grasp.descend_offset_z":0.01,"descend_to_grasp.descend_speed":0.10284,"descend_to_place.place_speed":0.13498,"descend_to_place.place_z_offset":-0.00442,"lift_object.lift_height":0.12059,"lift_object.lift_speed":0.1051},"optimized_scores":{"best_composite_score":-0.05446,"best_fitness_score":0.56554,"best_task_score":0.18309},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3167.0,"contact_point_centroid":[0.5441,0.09177,-0.00231],"force_p95":0.12525,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.6755,"mean_force":0.13666,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54923,0.12111,0.21197]},{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.49991,-0.01539,-0.00118],"force_p95":0.31222,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52243,"mean_force":0.08847,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48851,-0.01539,0.03676]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11460.0,"contact_point_centroid":[0.48857,0.00341,0.08285],"force_p95":0.09659,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29351,"mean_force":0.05831,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48591,-0.01537,0.08139]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9722.0,"contact_point_centroid":[0.48803,-0.03445,0.08471],"force_p95":0.10472,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28279,"mean_force":0.06694,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48589,-0.01537,0.08235]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1204.0,"contact_point_centroid":[0.5283,0.0868,0.19123],"force_p95":0.13407,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27551,"mean_force":0.09298,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5228,0.06889,0.19532]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1022.0,"contact_point_centroid":[0.52724,0.04919,0.19221],"force_p95":0.18426,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2455,"mean_force":0.1073,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.52236,0.06767,0.19524]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01576,-0.00203],"force_p95":0.1325,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16002,"mean_force":0.12523,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49133,-0.01541,0.03649]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11311.0,"contact_point_centroid":[0.50787,0.00589,0.16959],"force_p95":0.10736,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15494,"mean_force":0.08096,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50243,0.02462,0.16886]},{"body_a":"world","body_b":"grasp_target","contact_count":1504.0,"contact_point_centroid":[0.50382,-0.01567,-0.00191],"force_p95":0.13505,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.49899,-0.0068,0.23476]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11764.0,"contact_point_centroid":[0.50893,0.04341,0.16911],"force_p95":0.10658,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13266,"mean_force":0.07872,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.50263,0.025,0.16916]},{"body_a":"world","body_b":"grasp_target","contact_count":1544.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49786,-0.01473,0.10606]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5329.0,"contact_point_centroid":[0.49085,0.00366,0.03712],"force_p95":0.06675,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09514,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49011,-0.0154,0.03519]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4146.0,"contact_point_centroid":[0.48954,-0.03467,0.03777],"force_p95":0.07905,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0932,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49011,-0.0154,0.03519]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3153.0,"contact_point_centroid":[0.55171,0.12395,0.21518],"force_p95":0.01118,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01631,"mean_force":0.01046,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55075,0.12395,0.21301]}],"total_contact_groups":14},"final_pose_error":0.03957,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.54413,0.09177,0.01602],"final_tcp_position":[0.56877,0.1575,0.22527],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9748.87984,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":377.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1504.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.49974,-0.01404,0.16876],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":386.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1544.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.49861,-0.01547,0.04433],"tcp_start":[0.49974,-0.01404,0.16876],"tcp_to_object_dist_end":0.01904,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.01579,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31245,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13256,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11275.0,"raw_peak_contact_force":0.16002,"tcp_end":[0.49008,-0.0154,0.03516],"tcp_start":[0.49861,-0.01547,0.04433],"tcp_to_object_dist_end":0.01648,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":642.0,"n_steps_budget":720.0,"object_pos_end":[0.49942,-0.01586,0.12493],"object_pos_start":[0.50369,-0.01579,0.02588],"object_to_goal_dist_end":0.25331,"object_to_goal_dist_start":0.31245,"object_z_max":0.12481,"peak_contact_force":0.10467,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21324.0,"raw_peak_contact_force":0.52243,"subtask_id":"lift_object","tcp_end":[0.4861,-0.01537,0.14328],"tcp_start":[0.49008,-0.0154,0.03516],"tcp_to_object_dist_end":0.02268,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52688,0.05939,0.16902],"object_pos_start":[0.49942,-0.01586,0.12493],"object_to_goal_dist_end":0.16204,"object_to_goal_dist_start":0.25331,"object_z_max":0.16896,"peak_contact_force":0.10202,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23075.0,"raw_peak_contact_force":0.15494,"subtask_id":"place_at_goal","tcp_end":[0.52025,0.06015,0.19582],"tcp_start":[0.4861,-0.01537,0.14328],"tcp_to_object_dist_end":0.02762,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54413,0.09177,0.01602],"object_pos_start":[0.52688,0.05939,0.16902],"object_to_goal_dist_end":0.25467,"object_to_goal_dist_start":0.16204,"object_z_max":0.16902,"peak_contact_force":9748.87984,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8546.0,"raw_peak_contact_force":1.6755,"subtask_id":"place_at_goal","tcp_end":[0.56877,0.1575,0.22527],"tcp_start":[0.52025,0.06015,0.19582],"tcp_to_object_dist_end":0.22071,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `53da4dc33bcb1151bde99c46f4ec5d44dda63d23acc62ec623c12d4d0fb32574`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80741,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_object.approach_height":0.12842,"approach_above_object.approach_speed":0.1083,"approach_goal.goal_approach_z":0.06755,"approach_goal.transport_speed":0.18509,"descend_to_grasp.descend_offset_z":0.01029,"descend_to_grasp.descend_speed":0.09279,"descend_to_place.place_speed":0.17829,"descend_to_place.place_z_offset":-0.00098,"lift_object.lift_height":0.14849,"lift_object.lift_speed":0.06417},"optimized_scores":{"best_composite_score":0.06497,"best_fitness_score":0.68497,"best_task_score":0.42294},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":612.0,"contact_point_centroid":[0.62563,0.17607,-0.00343],"force_p95":0.69452,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.46154,"mean_force":0.19469,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61314,0.1617,0.14991]},{"body_a":"world","body_b":"grasp_target","contact_count":184.0,"contact_point_centroid":[0.50877,0.03761,-0.00123],"force_p95":0.2981,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53473,"mean_force":0.09375,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49678,0.03807,0.03683]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15674.0,"contact_point_centroid":[0.49557,0.05708,0.08531],"force_p95":0.10855,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30074,"mean_force":0.06412,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49423,0.03787,0.08309]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20246.0,"contact_point_centroid":[0.49656,0.01919,0.08625],"force_p95":0.08353,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28428,"mean_force":0.05056,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49424,0.03787,0.08506]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":411.0,"contact_point_centroid":[0.60349,0.1275,0.17676],"force_p95":0.1935,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24098,"mean_force":0.13319,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59722,0.14521,0.18146]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":553.0,"contact_point_centroid":[0.60176,0.16348,0.17578],"force_p95":0.15319,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22404,"mean_force":0.0979,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59761,0.14569,0.18024]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12492.0,"contact_point_centroid":[0.54717,0.07007,0.15982],"force_p95":0.11668,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21722,"mean_force":0.07692,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54133,0.08835,0.16073]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03969,-0.00213],"force_p95":0.15879,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21055,"mean_force":0.13207,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49989,0.03832,0.0364]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11912.0,"contact_point_centroid":[0.54919,0.11077,0.16281],"force_p95":0.11066,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20093,"mean_force":0.07905,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5448,0.09186,0.1625]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5032.0,"contact_point_centroid":[0.50032,0.01922,0.03655],"force_p95":0.07392,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17831,"mean_force":0.04305,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49866,0.03822,0.03505]},{"body_a":"world","body_b":"grasp_target","contact_count":1732.0,"contact_point_centroid":[0.51251,0.03972,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.50273,0.01739,0.23298]},{"body_a":"world","body_b":"grasp_target","contact_count":1516.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50609,0.03721,0.10471]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4219.0,"contact_point_centroid":[0.49892,0.05753,0.0378],"force_p95":0.08366,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0889,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49866,0.03822,0.03506]},{"body_a":"left_finger","body_b":"right_finger","contact_count":357.0,"contact_point_centroid":[0.61737,0.16474,0.14716],"force_p95":0.01391,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01517,"mean_force":0.01089,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61633,0.16471,0.14513]}],"total_contact_groups":14},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.6261,0.17609,0.016],"final_tcp_position":[0.61964,0.16788,0.14015],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.46154,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":434.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1732.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.50763,0.03572,0.16602],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14014,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":379.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1516.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.50722,0.03891,0.0445],"tcp_start":[0.50763,0.03572,0.16602],"tcp_to_object_dist_end":0.01924,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5125,0.03891,0.02556],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21299,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15639,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11051.0,"raw_peak_contact_force":0.21055,"tcp_end":[0.49863,0.03822,0.03502],"tcp_start":[0.50722,0.03891,0.0445],"tcp_to_object_dist_end":0.0168,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50424,0.03869,0.11975],"object_pos_start":[0.5125,0.03891,0.02556],"object_to_goal_dist_end":0.18374,"object_to_goal_dist_start":0.21299,"object_z_max":0.11963,"peak_contact_force":0.11063,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36104.0,"raw_peak_contact_force":0.53473,"subtask_id":"lift_object","tcp_end":[0.49439,0.03789,0.13927],"tcp_start":[0.49863,0.03822,0.03502],"tcp_to_object_dist_end":0.02188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59984,0.14354,0.15326],"object_pos_start":[0.50424,0.03869,0.11975],"object_to_goal_dist_end":0.04094,"object_to_goal_dist_start":0.18374,"object_z_max":0.15324,"peak_contact_force":0.13459,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24404.0,"raw_peak_contact_force":0.21722,"subtask_id":"place_at_goal","tcp_end":[0.59539,0.14268,0.18861],"tcp_start":[0.49439,0.03789,0.13927],"tcp_to_object_dist_end":0.03564,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":285.0,"n_steps_budget":1000.0,"object_pos_end":[0.6261,0.17609,0.016],"object_pos_start":[0.59984,0.14354,0.15326],"object_to_goal_dist_end":0.12908,"object_to_goal_dist_start":0.04094,"object_z_max":0.15326,"peak_contact_force":0.12313,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1933.0,"raw_peak_contact_force":1.46154,"subtask_id":"place_at_goal","tcp_end":[0.61964,0.16788,0.14015],"tcp_start":[0.59539,0.14268,0.18861],"tcp_to_object_dist_end":0.12459,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```