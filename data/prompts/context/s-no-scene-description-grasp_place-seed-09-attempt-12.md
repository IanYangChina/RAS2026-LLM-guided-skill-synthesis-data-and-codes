## Search State

- **Seed**: 9
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | 0.0916 | 0.37 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0128 | 0.35 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | 9 | -0.3728 | 0.17 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | 9 | -0.3608 | 0.17 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | 8 | 0.0544 | 0.34 | ❌ rejected |

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

## Current Skill (Q=0.092) — your mutation base

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
    - 0.0
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
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.15
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_object

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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.092
- **task_score** (E): 0.366
- **fitness_score**: 0.647  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.680

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1097 |
| descend_to_grasp | 1.00 | 1.00 | 0.1424 |
| grasp | 1.00 | 1.00 | 0.0130 |
| lift | 0.67 | 1.00 | 0.1111 |
| transport | 1.00 | 0.67 | 0.2365 |
| descend_to_place | 1.00 | 1.00 | 0.0061 |
| release | 1.00 | 1.00 | 0.0206 |
| retract | 1.00 | 1.00 | 0.0238 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.014, 0.197) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.014, 0.197)→(0.510, -0.016, 0.055) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, -0.016, 0.055)→(0.502, -0.016, 0.045) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 42.333 | 0.139 | 0.185 |
| lift | lift | 0.67 / step_budget | (0.502, -0.016, 0.045)→(0.506, -0.016, 0.156) | (0.515, -0.016, 0.026)→(0.514, -0.016, 0.129) | 0.270→0.237 | 1.00 / 30.333 | 0.094 | 0.408 |
| transport | approach | 1.00 / step_budget | (0.506, -0.016, 0.156)→(0.599, 0.150, 0.287) | (0.514, -0.016, 0.129)→(0.619, 0.156, 0.060) | 0.237→0.136 | 0.67 / 1.667 | 2.217 | 0.974 |
| descend_to_place | descend | 1.00 / force_exceeded | (0.599, 0.150, 0.287)→(0.600, 0.152, 0.282) | (0.619, 0.156, 0.060)→(0.630, 0.164, 0.018) | 0.136→0.153 | 1.00 / 3.667 | 4152.058 | 1.088 |
| release | release | 1.00 / step_budget | (0.600, 0.152, 0.282)→(0.596, 0.151, 0.302) | (0.630, 0.164, 0.018)→(0.629, 0.163, 0.016) | 0.153→0.155 | 1.00 / 4.000 | 0.123 | 1.431 |
| retract | retract | 1.00 / step_budget | (0.596, 0.151, 0.302)→(0.609, 0.170, 0.306) | (0.629, 0.163, 0.016)→(0.629, 0.163, 0.016) | 0.155→0.155 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.483
- phase_score: 0.332
- phase_breakdown.lift_object_score: 0.863
- phase_breakdown.reach_object_score: 0.225
- phase_breakdown.place_object_score: 0.084
- grasp_place_fitness: 0.704

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.704
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.483
- **Median Q (composite search score)**: 0.079
- **K-run variance**: 0.0018
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.378


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69412,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.14856,"descend_to_grasp.descend_speed":0.08155,"descend_to_place.contact_force_threshold":5.85069,"descend_to_place.descend_speed":0.11509,"grasp.grasp_duration":1.26363,"lift.lift_height":0.14891,"lift.lift_speed":0.05878,"release.release_duration":1.44715,"retract.retract_speed":0.10347,"transport.transport_speed":0.14343},"optimized_scores":{"best_composite_score":0.04705,"best_fitness_score":0.60205,"best_task_score":0.27643},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.6451,0.22174,-0.00423],"force_p95":2.4163,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.41639,"mean_force":2.41076,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60107,0.19568,0.32195]},{"body_a":"world","body_b":"grasp_target","contact_count":766.0,"contact_point_centroid":[0.62479,0.20857,-0.00353],"force_p95":0.77653,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.16496,"mean_force":0.19268,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5992,0.1962,0.32321]},{"body_a":"world","body_b":"grasp_target","contact_count":224.0,"contact_point_centroid":[0.53365,-0.02022,-0.00118],"force_p95":0.23228,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41924,"mean_force":0.06962,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52091,-0.02043,0.0459]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19462.0,"contact_point_centroid":[0.52514,-0.03959,0.09263],"force_p95":0.07607,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26981,"mean_force":0.05223,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52398,-0.02048,0.09094]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19177.0,"contact_point_centroid":[0.52483,-0.00137,0.09086],"force_p95":0.07609,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26718,"mean_force":0.05289,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52375,-0.02047,0.08889]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2676.0,"contact_point_centroid":[0.55247,0.05894,0.18728],"force_p95":0.12569,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26365,"mean_force":0.07908,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54806,0.04008,0.1874]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2726.0,"contact_point_centroid":[0.55128,0.01814,0.18488],"force_p95":0.13345,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23566,"mean_force":0.07749,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54701,0.03687,0.1847]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53705,-0.02123,-0.00208],"force_p95":0.14348,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19359,"mean_force":0.12871,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52373,-0.02048,0.04557]},{"body_a":"world","body_b":"grasp_target","contact_count":832.0,"contact_point_centroid":[0.53702,-0.02132,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12321,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51264,-0.00824,0.24934]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5065.0,"contact_point_centroid":[0.5232,-0.00128,0.04729],"force_p95":0.06682,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1267,"mean_force":0.04278,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52254,-0.02046,0.0442]},{"body_a":"world","body_b":"grasp_target","contact_count":264.0,"contact_point_centroid":[0.62373,0.20809,-0.00199],"force_p95":0.12267,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12271,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.6015,0.20355,0.34349]},{"body_a":"world","body_b":"grasp_target","contact_count":1076.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52815,-0.01886,0.12622]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4929.0,"contact_point_centroid":[0.52353,-0.03973,0.04598],"force_p95":0.07075,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0732,"mean_force":0.04498,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52254,-0.02046,0.0442]},{"body_a":"left_finger","body_b":"right_finger","contact_count":86.0,"contact_point_centroid":[0.60073,0.1967,0.31982],"force_p95":0.01534,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01574,"mean_force":0.01183,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60004,0.19669,0.3178]}],"total_contact_groups":14},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.62373,0.20809,0.01602],"final_tcp_position":[0.60464,0.21343,0.34501],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":2695.72829,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":209.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":832.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.52715,-0.0172,0.19689],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17121,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":269.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1076.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53129,-0.0206,0.05472],"tcp_start":[0.52715,-0.0172,0.19689],"tcp_to_object_dist_end":0.02928,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53696,-0.02073,0.0257],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31645,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.1406,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11794.0,"raw_peak_contact_force":0.19359,"tcp_end":[0.52251,-0.02046,0.04416],"tcp_start":[0.53129,-0.0206,0.05472],"tcp_to_object_dist_end":0.02344,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53473,-0.02052,0.11267],"object_pos_start":[0.53696,-0.02073,0.0257],"object_to_goal_dist_end":0.27628,"object_to_goal_dist_start":0.31645,"object_z_max":0.11256,"peak_contact_force":0.08781,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38863.0,"raw_peak_contact_force":0.41924,"subtask_id":"lift_object","tcp_end":[0.52942,-0.02058,0.13858],"tcp_start":[0.52251,-0.02046,0.04416],"tcp_to_object_dist_end":0.02645,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":319.0,"n_steps_budget":1000.0,"object_pos_end":[0.62778,0.20965,0.03299],"object_pos_start":[0.53473,-0.02052,0.11267],"object_to_goal_dist_end":0.17623,"object_to_goal_dist_start":0.27628,"object_z_max":0.22791,"peak_contact_force":5.74795,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5402.0,"raw_peak_contact_force":0.26365,"tcp_end":[0.60089,0.19495,0.32142],"tcp_start":[0.52942,-0.02058,0.13858],"tcp_to_object_dist_end":0.29006,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.62864,0.21217,0.01873],"object_pos_start":[0.62778,0.20965,0.03299],"object_to_goal_dist_end":0.19021,"object_to_goal_dist_start":0.17623,"object_z_max":0.03299,"peak_contact_force":2695.72829,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4.0,"raw_peak_contact_force":2.41639,"subtask_id":"place_object","tcp_end":[0.60128,0.19659,0.32238],"tcp_start":[0.60089,0.19495,0.32142],"tcp_to_object_dist_end":0.30528,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62373,0.2081,0.01602],"object_pos_start":[0.62864,0.21217,0.01873],"object_to_goal_dist_end":0.19286,"object_to_goal_dist_start":0.19021,"object_z_max":0.01873,"peak_contact_force":0.12272,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":852.0,"raw_peak_contact_force":2.16496,"tcp_end":[0.59869,0.19584,0.34244],"tcp_start":[0.60128,0.19659,0.32238],"tcp_to_object_dist_end":0.32761,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":66.0,"n_steps_budget":600.0,"object_pos_end":[0.62373,0.20809,0.01602],"object_pos_start":[0.62373,0.2081,0.01602],"object_to_goal_dist_end":0.19287,"object_to_goal_dist_start":0.19286,"object_z_max":0.01602,"peak_contact_force":0.12264,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":264.0,"raw_peak_contact_force":0.12271,"tcp_end":[0.60464,0.21343,0.34501],"tcp_start":[0.59869,0.19584,0.34244],"tcp_to_object_dist_end":0.32959,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46597,"average_solve_count":191.0,"average_success_count":191.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.1876,"descend_to_grasp.descend_speed":0.04364,"descend_to_place.contact_force_threshold":9.9852,"descend_to_place.descend_speed":0.11052,"grasp.grasp_duration":1.01875,"lift.lift_height":0.38053,"lift.lift_speed":0.05943,"release.release_duration":1.79598,"retract.retract_speed":0.07455,"transport.transport_speed":0.17131},"optimized_scores":{"best_composite_score":0.07854,"best_fitness_score":0.63354,"best_task_score":0.33933},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":42.0,"contact_point_centroid":[0.63952,0.14486,-0.00663],"force_p95":1.92551,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.41307,"mean_force":1.06089,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.61546,0.13032,0.28709]},{"body_a":"world","body_b":"grasp_target","contact_count":128.0,"contact_point_centroid":[0.63401,0.14431,-0.00892],"force_p95":0.64371,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.84818,"mean_force":0.25237,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61785,0.13628,0.28934]},{"body_a":"world","body_b":"grasp_target","contact_count":207.0,"contact_point_centroid":[0.54149,-0.0276,-0.00121],"force_p95":0.22553,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42656,"mean_force":0.07615,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5289,-0.02796,0.04547]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1565.0,"contact_point_centroid":[0.55411,-0.0115,0.17303],"force_p95":0.16368,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31509,"mean_force":0.08946,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54864,0.00717,0.17318]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16701.0,"contact_point_centroid":[0.53056,-0.00889,0.09006],"force_p95":0.10029,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29113,"mean_force":0.0609,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52841,-0.0279,0.08854]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18113.0,"contact_point_centroid":[0.53051,-0.04681,0.09103],"force_p95":0.08862,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28494,"mean_force":0.05673,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52845,-0.0279,0.08978]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1604.0,"contact_point_centroid":[0.55628,0.02902,0.17575],"force_p95":0.14305,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25687,"mean_force":0.086,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55035,0.01041,0.17604]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54564,-0.02909,-0.00211],"force_p95":0.15262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21237,"mean_force":0.13097,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53195,-0.02805,0.04518]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4309.0,"contact_point_centroid":[0.53177,-0.0088,0.04659],"force_p95":0.07837,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14444,"mean_force":0.04947,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53075,-0.02802,0.04377]},{"body_a":"world","body_b":"grasp_target","contact_count":876.0,"contact_point_centroid":[0.5456,-0.02923,-0.00185],"force_p95":0.13713,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12318,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51621,-0.01146,0.24859]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.63467,0.1452,-0.00206],"force_p95":0.12625,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12753,"mean_force":0.11516,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61474,0.13571,0.28499]},{"body_a":"world","body_b":"grasp_target","contact_count":348.0,"contact_point_centroid":[0.63467,0.14521,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61923,0.14421,0.30772]},{"body_a":"world","body_b":"grasp_target","contact_count":1116.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53589,-0.02599,0.12595]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4966.0,"contact_point_centroid":[0.53184,-0.04718,0.04553],"force_p95":0.07232,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07441,"mean_force":0.04462,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53075,-0.02802,0.04377]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.6168,0.13622,0.28354],"force_p95":0.01428,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01487,"mean_force":0.01104,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61636,0.13621,0.28137]},{"body_a":"left_finger","body_b":"right_finger","contact_count":15.0,"contact_point_centroid":[0.61718,0.13653,0.28718],"force_p95":0.01436,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01436,"mean_force":0.01388,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61753,0.13653,0.28558]}],"total_contact_groups":16},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63467,0.14521,0.01602],"final_tcp_position":[0.62501,0.15422,0.3121],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":9755.00906,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":876.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53452,-0.02387,0.19556],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16998,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":279.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1116.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53957,-0.02826,0.05457],"tcp_start":[0.53452,-0.02387,0.19556],"tcp_to_object_dist_end":0.0292,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54555,-0.02824,0.02562],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26043,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14809,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11075.0,"raw_peak_contact_force":0.21237,"tcp_end":[0.53072,-0.02802,0.04373],"tcp_start":[0.53957,-0.02826,0.05457],"tcp_to_object_dist_end":0.02341,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53966,-0.02811,0.11685],"object_pos_start":[0.54555,-0.02824,0.02562],"object_to_goal_dist_end":0.22261,"object_to_goal_dist_start":0.26043,"object_z_max":0.11674,"peak_contact_force":0.10342,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35021.0,"raw_peak_contact_force":0.42656,"subtask_id":"lift_object","tcp_end":[0.53083,-0.02794,0.14347],"tcp_start":[0.53072,-0.02802,0.04373],"tcp_to_object_dist_end":0.02804,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":255.0,"n_steps_budget":1000.0,"object_pos_end":[0.6366,0.14729,-0.00129],"object_pos_start":[0.53966,-0.02811,0.11685],"object_to_goal_dist_end":0.17912,"object_to_goal_dist_start":0.22261,"object_z_max":0.19206,"peak_contact_force":0.90223,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3211.0,"raw_peak_contact_force":2.41307,"tcp_end":[0.6176,0.13428,0.29076],"tcp_start":[0.53083,-0.02794,0.14347],"tcp_to_object_dist_end":0.29296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":32.0,"n_steps_budget":1000.0,"object_pos_end":[0.6352,0.14702,0.01023],"object_pos_start":[0.6366,0.14729,-0.00129],"object_to_goal_dist_end":0.16766,"object_to_goal_dist_start":0.17912,"object_z_max":0.00975,"peak_contact_force":9755.00906,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":143.0,"raw_peak_contact_force":0.84818,"subtask_id":"place_object","tcp_end":[0.61747,0.13651,0.28502],"tcp_start":[0.6176,0.13428,0.29076],"tcp_to_object_dist_end":0.27556,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63467,0.14521,0.01602],"object_pos_start":[0.6352,0.14702,0.01023],"object_to_goal_dist_end":0.16212,"object_to_goal_dist_start":0.16766,"object_z_max":0.01671,"peak_contact_force":0.12264,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12753,"tcp_end":[0.61388,0.13542,0.30448],"tcp_start":[0.61747,0.13651,0.28502],"tcp_to_object_dist_end":0.28937,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":87.0,"n_steps_budget":600.0,"object_pos_end":[0.63467,0.14521,0.01602],"object_pos_start":[0.63467,0.14521,0.01602],"object_to_goal_dist_end":0.16212,"object_to_goal_dist_start":0.16212,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":348.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.62501,0.15422,0.3121],"tcp_start":[0.61388,0.13542,0.30448],"tcp_to_object_dist_end":0.29638,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70769,"average_solve_count":195.0,"average_success_count":195.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.06711,"descend_to_grasp.descend_speed":0.08222,"descend_to_place.contact_force_threshold":5.39505,"descend_to_place.descend_speed":0.10672,"grasp.grasp_duration":1.25855,"lift.lift_height":0.17228,"lift.lift_speed":0.10904,"release.release_duration":0.82054,"retract.retract_speed":0.16979,"transport.transport_speed":0.07708},"optimized_scores":{"best_composite_score":0.14932,"best_fitness_score":0.70432,"best_task_score":0.48281},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":794.0,"contact_point_centroid":[0.62908,0.13535,-0.0035],"force_p95":0.72013,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.99916,"mean_force":0.18541,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5766,0.12258,0.23966]},{"body_a":"world","body_b":"grasp_target","contact_count":127.0,"contact_point_centroid":[0.46068,-0.00045,-0.00121],"force_p95":0.22911,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37925,"mean_force":0.05673,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45086,-0.00021,0.04892]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12222.0,"contact_point_centroid":[0.45488,-0.0192,0.10775],"force_p95":0.10289,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29081,"mean_force":0.06593,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45287,-0.00028,0.10749]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12697.0,"contact_point_centroid":[0.45543,0.0186,0.10835],"force_p95":0.09769,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27744,"mean_force":0.06386,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4529,-0.00028,0.10773]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1184.0,"contact_point_centroid":[0.49666,0.04965,0.19962],"force_p95":0.18798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24515,"mean_force":0.11478,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.49041,0.03121,0.20135]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1631.0,"contact_point_centroid":[0.50249,0.01893,0.20301],"force_p95":0.14264,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22478,"mean_force":0.08893,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.49617,0.037,0.20427]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46285,-0.00014,-0.00202],"force_p95":0.12934,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1477,"mean_force":0.12452,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45304,-0.00018,0.04848]},{"body_a":"world","body_b":"grasp_target","contact_count":812.0,"contact_point_centroid":[0.46286,-7e-05,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12323,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48422,-4e-05,0.25136]},{"body_a":"world","body_b":"grasp_target","contact_count":392.0,"contact_point_centroid":[0.62909,0.13559,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.58581,0.13185,0.26015]},{"body_a":"world","body_b":"grasp_target","contact_count":1124.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46303,-9e-05,0.12775]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4129.0,"contact_point_centroid":[0.4513,-0.0194,0.04897],"force_p95":0.07593,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09828,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.452,-0.00019,0.04746]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4864.0,"contact_point_centroid":[0.45212,0.01887,0.04873],"force_p95":0.06782,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.088,"mean_force":0.04462,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.452,-0.00019,0.04746]},{"body_a":"left_finger","body_b":"right_finger","contact_count":42.0,"contact_point_centroid":[0.57779,0.12295,0.23522],"force_p95":0.0157,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0157,"mean_force":0.01161,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57794,0.12294,0.23349]}],"total_contact_groups":13},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.62909,0.13559,0.01602],"final_tcp_position":[0.59697,0.14239,0.2615],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":5.43627,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":204.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":812.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.46756,-7e-05,0.19894],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":281.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1124.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.45983,-0.00011,0.05543],"tcp_start":[0.46756,-7e-05,0.19894],"tcp_to_object_dist_end":0.02957,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46277,-0.00033,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23337,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.1288,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.1477,"tcp_end":[0.45197,-0.00019,0.04743],"tcp_start":[0.45983,-0.00011,0.05543],"tcp_to_object_dist_end":0.02408,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":794.0,"n_steps_budget":870.0,"object_pos_end":[0.46868,-9e-05,0.15622],"object_pos_start":[0.46277,-0.00033,0.02591],"object_to_goal_dist_end":0.21111,"object_to_goal_dist_start":0.23337,"object_z_max":0.15609,"peak_contact_force":0.09209,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25046.0,"raw_peak_contact_force":0.37925,"subtask_id":"lift_object","tcp_end":[0.4588,-0.00034,0.18614],"tcp_start":[0.45197,-0.00019,0.04743],"tcp_to_object_dist_end":0.03152,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":204.0,"n_steps_budget":1000.0,"object_pos_end":[0.59311,0.11118,0.14968],"object_pos_start":[0.46868,-9e-05,0.15622],"object_to_goal_dist_end":0.05277,"object_to_goal_dist_start":0.21111,"object_z_max":0.19662,"peak_contact_force":0.0,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2815.0,"raw_peak_contact_force":0.24515,"tcp_end":[0.57973,0.12125,0.24843],"tcp_start":[0.4588,-0.00034,0.18614],"tcp_to_object_dist_end":0.10016,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":45.0,"n_steps_budget":1000.0,"object_pos_end":[0.62653,0.13356,0.02382],"object_pos_start":[0.59311,0.11118,0.14968],"object_to_goal_dist_end":0.10158,"object_to_goal_dist_start":0.05277,"object_z_max":0.14968,"peak_contact_force":5.43627,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"place_object","tcp_end":[0.58007,0.12342,0.23847],"tcp_start":[0.57973,0.12125,0.24843],"tcp_to_object_dist_end":0.21985,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62909,0.1356,0.01602],"object_pos_start":[0.62653,0.13356,0.02382],"object_to_goal_dist_end":0.10922,"object_to_goal_dist_start":0.10158,"object_z_max":0.02382,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":836.0,"raw_peak_contact_force":1.99916,"tcp_end":[0.57544,0.12226,0.25964],"tcp_start":[0.58007,0.12342,0.23847],"tcp_to_object_dist_end":0.24982,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":98.0,"n_steps_budget":600.0,"object_pos_end":[0.62909,0.13559,0.01602],"object_pos_start":[0.62909,0.1356,0.01602],"object_to_goal_dist_end":0.10922,"object_to_goal_dist_start":0.10922,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":392.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.59697,0.14239,0.2615],"tcp_start":[0.57544,0.12226,0.25964],"tcp_to_object_dist_end":0.24766,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```