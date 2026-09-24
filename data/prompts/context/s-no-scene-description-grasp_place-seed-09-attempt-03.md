## Search State

- **Seed**: 9
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.0380 | 0.20 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.1077 | 0.17 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | -0.0077 | 0.17 | ✅ accepted |
| 0 | rotate → pull → push → descend → descend → grasp → approach | impedance_motion | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | linear_cartesian | impedance_control | impedance_control | impedance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | pose_tolerance | 6 | -0.1649 | 0.13 | ✅ accepted |

**Proposal policy**: task_score is 0.20 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.038) — your mutation base

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

- **Composite score**: 0.038
- **task_score** (E): 0.199
- **fitness_score**: 0.468  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1099 |
| descend_to_grasp | 1.00 | 1.00 | 0.1321 |
| grasp | 1.00 | 1.00 | 0.0129 |
| lift | 1.00 | 1.00 | 0.0854 |
| transport | 0.67 | 1.00 | 0.2657 |
| descend_to_place | 1.00 | 1.00 | 0.1008 |
| release | 1.00 | 1.00 | 0.0195 |
| retract | 1.00 | 1.00 | 0.0849 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.014, 0.197) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.014, 0.197)→(0.510, -0.016, 0.065) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, -0.016, 0.065)→(0.502, -0.016, 0.055) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 26.333 | 0.140 | 0.181 |
| lift | lift | 1.00 / step_budget | (0.502, -0.016, 0.055)→(0.498, -0.016, 0.140) | (0.515, -0.017, 0.026)→(0.503, -0.011, 0.090) | 0.270→0.243 | 1.00 / 15.333 | 91001.628 | 0.402 |
| transport | approach | 0.67 / step_budget | (0.498, -0.016, 0.140)→(0.608, 0.165, 0.296) | (0.503, -0.011, 0.090)→(0.524, 0.026, 0.019) | 0.243→0.243 | 1.00 / 8.333 | 91000.417 | 1.048 |
| descend_to_place | descend | 1.00 / step_budget | (0.608, 0.165, 0.296)→(0.613, 0.177, 0.197) | (0.524, 0.026, 0.019)→(0.524, 0.026, 0.019) | 0.243→0.243 | 1.00 / 8.667 | 182005.792 | 0.123 |
| release | release | 1.00 / step_budget | (0.613, 0.177, 0.197)→(0.607, 0.175, 0.215) | (0.524, 0.026, 0.019)→(0.524, 0.026, 0.019) | 0.243→0.243 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.607, 0.175, 0.215)→(0.605, 0.174, 0.300) | (0.524, 0.026, 0.019)→(0.524, 0.026, 0.019) | 0.243→0.243 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.216
- phase_score: 0.536
- phase_breakdown.lift_object_score: 0.588
- phase_breakdown.reach_object_score: 0.270
- phase_breakdown.place_object_score: 0.554
- grasp_place_fitness: 0.560

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.560
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.216
- **Median Q (composite search score)**: 0.106
- **K-run variance**: 0.0128
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.358


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48163,"average_solve_count":245.0,"average_success_count":245.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.09875,"descend_to_grasp.descend_speed":0.07773,"descend_to_place.descend_speed":0.10513,"lift.lift_height":0.11333,"transport.speed":0.04677},"optimized_scores":{"best_composite_score":0.10566,"best_fitness_score":0.53566,"best_task_score":0.16666},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2814.0,"contact_point_centroid":[0.5583,0.04627,-0.00236],"force_p95":0.12683,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.55674,"mean_force":0.13957,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56844,0.12072,0.26317]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6179.0,"contact_point_centroid":[0.52209,-0.00201,0.09712],"force_p95":0.13269,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30313,"mean_force":0.09718,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51857,-0.02033,0.10062]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.53423,-0.01997,-0.00116],"force_p95":0.23077,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29645,"mean_force":0.05584,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52108,-0.02039,0.05587]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6340.0,"contact_point_centroid":[0.52197,-0.03862,0.09781],"force_p95":0.13207,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28465,"mean_force":0.09519,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51859,-0.02033,0.10144]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1669.0,"contact_point_centroid":[0.53047,0.0211,0.16458],"force_p95":0.14813,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22188,"mean_force":0.11069,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52464,0.00283,0.16941]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53705,-0.02125,-0.00207],"force_p95":0.14379,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18854,"mean_force":0.12781,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52387,-0.02045,0.0555]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1957.0,"contact_point_centroid":[0.53021,-0.01449,0.16532],"force_p95":0.12299,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16301,"mean_force":0.09387,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52487,0.00351,0.16992]},{"body_a":"world","body_b":"grasp_target","contact_count":856.0,"contact_point_centroid":[0.53702,-0.02132,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1232,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51266,-0.00823,0.24941]},{"body_a":"world","body_b":"grasp_target","contact_count":1000.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.5283,-0.01888,0.13109]},{"body_a":"world","body_b":"grasp_target","contact_count":660.0,"contact_point_centroid":[0.55834,0.04635,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59995,0.20478,0.27886]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55834,0.04635,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.601,0.21719,0.23252]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.55834,0.04635,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.5979,0.21573,0.29212]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2664.0,"contact_point_centroid":[0.52371,-0.00168,0.05121],"force_p95":0.09832,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10656,"mean_force":0.07621,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5227,-0.02042,0.05413]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2969.0,"contact_point_centroid":[0.52336,-0.03913,0.05104],"force_p95":0.09354,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09362,"mean_force":0.06971,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5227,-0.02042,0.05413]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2769.0,"contact_point_centroid":[0.57094,0.12641,0.27003],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01624,"mean_force":0.01055,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.57061,0.12641,0.26777]},{"body_a":"left_finger","body_b":"right_finger","contact_count":713.0,"contact_point_centroid":[0.60042,0.20485,0.28098],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01273,"mean_force":0.01033,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59997,0.20484,0.27865]}],"total_contact_groups":17},"final_pose_error":0.01511,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.55834,0.04635,0.01602],"final_tcp_position":[0.59831,0.21582,0.337],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273011.08125,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":215.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":856.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.52735,-0.01727,0.19653],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17083,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":250.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53132,-0.02057,0.06467],"tcp_start":[0.52735,-0.01727,0.19653],"tcp_to_object_dist_end":0.03907,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53697,-0.0207,0.02576],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3164,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14141,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7433.0,"raw_peak_contact_force":0.18854,"tcp_end":[0.52267,-0.02042,0.05409],"tcp_start":[0.53132,-0.02057,0.06467],"tcp_to_object_dist_end":0.03173,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.52486,-0.02037,0.1183],"object_pos_start":[0.53697,-0.0207,0.02576],"object_to_goal_dist_end":0.27714,"object_to_goal_dist_start":0.3164,"object_z_max":0.11819,"peak_contact_force":0.11313,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12663.0,"raw_peak_contact_force":0.30313,"subtask_id":"lift_object","tcp_end":[0.51872,-0.02033,0.1549],"tcp_start":[0.52267,-0.02042,0.05409],"tcp_to_object_dist_end":0.03711,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55834,0.04635,0.01602],"object_pos_start":[0.52486,-0.02037,0.1183],"object_to_goal_dist_end":0.26877,"object_to_goal_dist_start":0.27714,"object_z_max":0.14792,"peak_contact_force":273001.00512,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9209.0,"raw_peak_contact_force":1.55674,"tcp_end":[0.59601,0.19286,0.32121],"tcp_start":[0.51872,-0.02033,0.1549],"tcp_to_object_dist_end":0.34063,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":165.0,"n_steps_budget":1000.0,"object_pos_end":[0.55834,0.04635,0.01602],"object_pos_start":[0.55834,0.04635,0.01602],"object_to_goal_dist_end":0.26877,"object_to_goal_dist_start":0.26877,"object_z_max":0.01602,"peak_contact_force":273011.08125,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1373.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.60461,0.21841,0.23357],"tcp_start":[0.59601,0.19286,0.32121],"tcp_to_object_dist_end":0.2812,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55834,0.04635,0.01602],"object_pos_start":[0.55834,0.04635,0.01602],"object_to_goal_dist_end":0.26877,"object_to_goal_dist_start":0.26877,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59989,0.21664,0.252],"tcp_start":[0.60461,0.21841,0.23357],"tcp_to_object_dist_end":0.29395,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.55834,0.04635,0.01602],"object_pos_start":[0.55834,0.04635,0.01602],"object_to_goal_dist_end":0.26877,"object_to_goal_dist_start":0.26877,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59831,0.21582,0.337],"tcp_start":[0.59989,0.21664,0.252],"tcp_to_object_dist_end":0.36516,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.2116,"average_solve_count":293.0,"average_success_count":293.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.04623,"descend_to_grasp.descend_speed":0.10021,"descend_to_place.descend_speed":0.04343,"lift.lift_height":0.11997,"transport.speed":0.05726},"optimized_scores":{"best_composite_score":0.13002,"best_fitness_score":0.56002,"best_task_score":0.21551},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2933.0,"contact_point_centroid":[0.56198,0.01552,-0.00233],"force_p95":0.17065,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.46368,"mean_force":0.14231,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.58759,0.08697,0.25261]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6379.0,"contact_point_centroid":[0.53067,-0.00952,0.09999],"force_p95":0.13369,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29539,"mean_force":0.09851,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52683,-0.02783,0.10351]},{"body_a":"world","body_b":"grasp_target","contact_count":153.0,"contact_point_centroid":[0.54289,-0.02745,-0.00121],"force_p95":0.23098,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28714,"mean_force":0.059,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5293,-0.02792,0.05564]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6610.0,"contact_point_centroid":[0.53044,-0.0461,0.10074],"force_p95":0.13453,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27905,"mean_force":0.09572,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52684,-0.02783,0.10438]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":727.0,"contact_point_centroid":[0.5367,-0.00019,0.16154],"force_p95":0.1525,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23382,"mean_force":0.11609,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.53041,-0.01843,0.16616]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54565,-0.02914,-0.0021],"force_p95":0.15213,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20547,"mean_force":0.12981,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53217,-0.02801,0.05535]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":914.0,"contact_point_centroid":[0.53688,-0.03492,0.16278],"force_p95":0.12515,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17224,"mean_force":0.0908,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.531,-0.01707,0.16705]},{"body_a":"world","body_b":"grasp_target","contact_count":964.0,"contact_point_centroid":[0.5456,-0.02923,-0.00186],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12313,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51577,-0.01135,0.24892]},{"body_a":"world","body_b":"grasp_target","contact_count":972.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53619,-0.02602,0.13049]},{"body_a":"world","body_b":"grasp_target","contact_count":760.0,"contact_point_centroid":[0.56181,0.01639,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62701,0.15854,0.2607]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56181,0.01639,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62445,0.16077,0.20466]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.56181,0.01639,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.62071,0.15955,0.26394]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2493.0,"contact_point_centroid":[0.53254,-0.00922,0.0512],"force_p95":0.10505,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11211,"mean_force":0.08074,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53099,-0.02797,0.05394]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2992.0,"contact_point_centroid":[0.53173,-0.04663,0.05088],"force_p95":0.09469,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09497,"mean_force":0.06922,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53099,-0.02797,0.05394]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3015.0,"contact_point_centroid":[0.58983,0.09029,0.2578],"force_p95":0.01111,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01612,"mean_force":0.0105,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.58946,0.09029,0.25543]},{"body_a":"left_finger","body_b":"right_finger","contact_count":815.0,"contact_point_centroid":[0.62735,0.15856,0.26298],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01265,"mean_force":0.01039,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62702,0.15855,0.26056]}],"total_contact_groups":17},"final_pose_error":0.01564,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.56181,0.01639,0.01602],"final_tcp_position":[0.62107,0.1596,0.30856],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.46368,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":242.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":964.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53444,-0.02392,0.19528],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16971,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":243.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":972.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53969,-0.02821,0.06483],"tcp_start":[0.53444,-0.02392,0.19528],"tcp_to_object_dist_end":0.03928,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54556,-0.02833,0.02567],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26047,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.1478,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7285.0,"raw_peak_contact_force":0.20547,"tcp_end":[0.53096,-0.02797,0.0539],"tcp_start":[0.53969,-0.02821,0.06483],"tcp_to_object_dist_end":0.03179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":666.0,"n_steps_budget":750.0,"object_pos_end":[0.53342,-0.028,0.12422],"object_pos_start":[0.54556,-0.02833,0.02567],"object_to_goal_dist_end":0.22335,"object_to_goal_dist_start":0.26047,"object_z_max":0.1241,"peak_contact_force":0.1128,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13142.0,"raw_peak_contact_force":0.29539,"subtask_id":"lift_object","tcp_end":[0.52703,-0.02783,0.16107],"tcp_start":[0.53096,-0.02797,0.0539],"tcp_to_object_dist_end":0.0374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":942.0,"n_steps_budget":1000.0,"object_pos_end":[0.56181,0.01639,0.01602],"object_pos_start":[0.53342,-0.028,0.12422],"object_to_goal_dist_end":0.23021,"object_to_goal_dist_start":0.22335,"object_z_max":0.13456,"peak_contact_force":0.12263,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7589.0,"raw_peak_contact_force":1.46368,"tcp_end":[0.62627,0.15563,0.31066],"tcp_start":[0.52703,-0.02783,0.16107],"tcp_to_object_dist_end":0.3322,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":190.0,"n_steps_budget":1000.0,"object_pos_end":[0.56181,0.01639,0.01602],"object_pos_start":[0.56181,0.01639,0.01602],"object_to_goal_dist_end":0.23021,"object_to_goal_dist_start":0.23021,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1575.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.62859,0.16195,0.20597],"tcp_start":[0.62627,0.15563,0.31066],"tcp_to_object_dist_end":0.24845,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56181,0.01639,0.01602],"object_pos_start":[0.56181,0.01639,0.01602],"object_to_goal_dist_end":0.23021,"object_to_goal_dist_start":0.23021,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6231,0.16032,0.22406],"tcp_start":[0.62859,0.16195,0.20597],"tcp_to_object_dist_end":0.26029,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.56181,0.01639,0.01602],"object_pos_start":[0.56181,0.01639,0.01602],"object_to_goal_dist_end":0.23021,"object_to_goal_dist_start":0.23021,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62107,0.1596,0.30856],"tcp_start":[0.6231,0.16032,0.22406],"tcp_to_object_dist_end":0.33106,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36134,"average_solve_count":238.0,"average_success_count":238.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.19877,"descend_to_grasp.descend_speed":0.09189,"descend_to_place.descend_speed":0.12187,"lift.lift_height":0.0569,"transport.speed":0.02822},"optimized_scores":{"best_composite_score":-0.12157,"best_fitness_score":0.30843,"best_task_score":0.21593},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1066.0,"contact_point_centroid":[0.45291,0.01028,-0.00228],"force_p95":0.28996,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60762,"mean_force":0.14479,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44867,-0.00021,0.08772]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1474.0,"contact_point_centroid":[0.44811,-0.01892,0.06184],"force_p95":0.15005,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30101,"mean_force":0.10234,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44943,-0.00021,0.06537]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2016.0,"contact_point_centroid":[0.44892,0.01792,0.06185],"force_p95":0.11847,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27476,"mean_force":0.07805,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44936,-0.00021,0.06585]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46286,-0.00018,-0.00202],"force_p95":0.13113,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14837,"mean_force":0.12454,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4535,-0.00017,0.05844]},{"body_a":"world","body_b":"grasp_target","contact_count":768.0,"contact_point_centroid":[0.46286,-7e-05,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12326,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48424,-4e-05,0.25101]},{"body_a":"world","body_b":"grasp_target","contact_count":3780.0,"contact_point_centroid":[0.45202,0.01646,-0.00199],"force_p95":0.12267,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12314,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52507,0.07483,0.18166]},{"body_a":"world","body_b":"grasp_target","contact_count":1036.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46322,-8e-05,0.13278]},{"body_a":"world","body_b":"grasp_target","contact_count":736.0,"contact_point_centroid":[0.45202,0.01646,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60209,0.14762,0.20571]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.45202,0.01646,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59974,0.14896,0.15057]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.45202,0.01646,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.595,0.1476,0.21091]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2193.0,"contact_point_centroid":[0.45053,-0.01896,0.05438],"force_p95":0.11408,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1149,"mean_force":0.0903,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45246,-0.00018,0.05741]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2928.0,"contact_point_centroid":[0.45206,0.01823,0.05352],"force_p95":0.09135,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09201,"mean_force":0.06947,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45246,-0.00018,0.05741]},{"body_a":"left_finger","body_b":"right_finger","contact_count":623.0,"contact_point_centroid":[0.44862,-0.00021,0.09949],"force_p95":0.01269,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01608,"mean_force":0.01104,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44829,-0.00021,0.09726]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3997.0,"contact_point_centroid":[0.5257,0.07516,0.18423],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01291,"mean_force":0.01054,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52542,0.07515,0.18201]},{"body_a":"left_finger","body_b":"right_finger","contact_count":788.0,"contact_point_centroid":[0.60252,0.1476,0.20843],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01264,"mean_force":0.0104,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60206,0.14759,0.20622]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.60286,0.14977,0.14846],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.011,"mean_force":0.01019,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60249,0.14975,0.14628]}],"total_contact_groups":16},"final_pose_error":0.01509,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.45202,0.01646,0.02602],"final_tcp_position":[0.59524,0.14763,0.25558],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":273006.17314,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":193.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":768.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.46772,-7e-05,0.19894],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17299,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":259.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1036.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.46019,-0.0001,0.06541],"tcp_start":[0.46772,-7e-05,0.19894],"tcp_to_object_dist_end":0.03948,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46277,-0.00055,0.02592],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23351,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.13024,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":6921.0,"raw_peak_contact_force":0.14837,"tcp_end":[0.45244,-0.00018,0.05739],"tcp_start":[0.46019,-0.0001,0.06541],"tcp_to_object_dist_end":0.03313,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":448.0,"n_steps_budget":600.0,"object_pos_end":[0.45201,0.01637,0.02602],"object_pos_start":[0.46277,-0.00055,0.02592],"object_to_goal_dist_end":0.22997,"object_to_goal_dist_start":0.23351,"object_z_max":0.03877,"peak_contact_force":273004.65907,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5179.0,"raw_peak_contact_force":0.60762,"subtask_id":"lift_object","tcp_end":[0.4484,-0.00021,0.10517],"tcp_start":[0.45244,-0.00018,0.05739],"tcp_to_object_dist_end":0.08095,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":945.0,"n_steps_budget":1000.0,"object_pos_end":[0.45202,0.01646,0.02602],"object_pos_start":[0.45201,0.01637,0.02602],"object_to_goal_dist_end":0.22992,"object_to_goal_dist_start":0.22997,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7777.0,"raw_peak_contact_force":0.12314,"tcp_end":[0.60032,0.1453,0.25666],"tcp_start":[0.4484,-0.00021,0.10517],"tcp_to_object_dist_end":0.30296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":184.0,"n_steps_budget":1000.0,"object_pos_end":[0.45202,0.01646,0.02602],"object_pos_start":[0.45202,0.01646,0.02602],"object_to_goal_dist_end":0.22992,"object_to_goal_dist_start":0.22992,"object_z_max":0.02602,"peak_contact_force":273006.17314,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1524.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.60478,0.15029,0.15115],"tcp_start":[0.60032,0.1453,0.25666],"tcp_to_object_dist_end":0.23855,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45202,0.01646,0.02602],"object_pos_start":[0.45202,0.01646,0.02602],"object_to_goal_dist_end":0.22992,"object_to_goal_dist_start":0.22992,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59806,0.14846,0.17037],"tcp_start":[0.60478,0.15029,0.15115],"tcp_to_object_dist_end":0.24411,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.45202,0.01646,0.02602],"object_pos_start":[0.45202,0.01646,0.02602],"object_to_goal_dist_end":0.22992,"object_to_goal_dist_start":0.22992,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59524,0.14763,0.25558],"tcp_start":[0.59806,0.14846,0.17037],"tcp_to_object_dist_end":0.30069,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```