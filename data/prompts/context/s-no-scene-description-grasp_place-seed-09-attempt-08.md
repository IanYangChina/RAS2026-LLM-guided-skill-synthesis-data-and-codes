## Search State

- **Seed**: 9
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | 8 | 0.0544 | 0.34 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3770 | 0.77 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1636 | 0.36 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.1002 | 0.19 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1455 | 0.17 | ❌ rejected |

**Proposal policy**: task_score is 0.34 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.054) — your mutation base

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

- **Composite score**: 0.054
- **task_score** (E): 0.342
- **fitness_score**: 0.634  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1100 |
| descend_to_grasp | 1.00 | 1.00 | 0.1419 |
| grasp | 1.00 | 1.00 | 0.0130 |
| lift | 0.67 | 1.00 | 0.1126 |
| transport | 1.00 | 1.00 | 0.2624 |
| descend_to_place | 1.00 | 1.00 | 0.0311 |
| release_object | 1.00 | 1.00 | 0.0190 |
| retract_after_place | 1.00 | 1.00 | 0.0119 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.014, 0.197) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.014, 0.197)→(0.510, -0.016, 0.055) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, -0.016, 0.055)→(0.502, -0.016, 0.045) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 43.667 | 0.139 | 0.184 |
| lift | lift | 0.67 / step_budget | (0.502, -0.016, 0.045)→(0.508, -0.016, 0.158) | (0.515, -0.016, 0.026)→(0.516, -0.016, 0.130) | 0.270→0.235 | 1.00 / 30.000 | 0.093 | 0.408 |
| transport | approach | 1.00 / step_budget | (0.508, -0.016, 0.158)→(0.610, 0.170, 0.302) | (0.516, -0.016, 0.130)→(0.599, 0.130, 0.016) | 0.235→0.164 | 1.00 / 8.000 | 0.124 | 2.034 |
| descend_to_place | descend | 1.00 / step_budget | (0.610, 0.170, 0.302)→(0.613, 0.176, 0.271) | (0.599, 0.130, 0.016)→(0.599, 0.130, 0.016) | 0.164→0.164 | 1.00 / 8.000 | 0.123 | 0.124 |
| release_object | release | 1.00 / step_budget | (0.613, 0.176, 0.271)→(0.609, 0.174, 0.290) | (0.599, 0.130, 0.016)→(0.599, 0.130, 0.016) | 0.164→0.164 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract_after_place | retract | 1.00 / step_budget | (0.609, 0.174, 0.290)→(0.612, 0.177, 0.300) | (0.599, 0.130, 0.016)→(0.599, 0.130, 0.016) | 0.164→0.164 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.449
- phase_score: 0.362
- phase_breakdown.lift_object_score: 0.902
- phase_breakdown.reach_object_score: 0.225
- phase_breakdown.place_object_score: 0.115
- grasp_place_fitness: 0.687

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.687
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.449
- **Median Q (composite search score)**: 0.037
- **K-run variance**: 0.0015
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.254


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36269,"average_solve_count":193.0,"average_success_count":193.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.08079,"descend_to_grasp.descend_speed":0.05319,"descend_to_place.descend_speed":0.1255,"descend_to_place.place_z_offset":0.09048,"lift.lift_height":0.15748,"lift.lift_speed":0.05864,"retract_after_place.speed":0.18738,"transport.speed":0.42075},"optimized_scores":{"best_composite_score":0.01907,"best_fitness_score":0.59907,"best_task_score":0.27106},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":382.0,"contact_point_centroid":[0.6117,0.18625,-0.00531],"force_p95":1.03539,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.40588,"mean_force":0.25969,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.59757,0.19063,0.31708]},{"body_a":"world","body_b":"grasp_target","contact_count":224.0,"contact_point_centroid":[0.53363,-0.0202,-0.00118],"force_p95":0.22777,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41566,"mean_force":0.07015,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52086,-0.02043,0.04615]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4475.0,"contact_point_centroid":[0.55198,0.0628,0.18972],"force_p95":0.12988,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2807,"mean_force":0.07947,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.548,0.04407,0.19042]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20540.0,"contact_point_centroid":[0.52448,-0.03956,0.09145],"force_p95":0.07323,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26979,"mean_force":0.04987,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52346,-0.02047,0.08976]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18602.0,"contact_point_centroid":[0.5247,-0.00132,0.09142],"force_p95":0.07752,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26744,"mean_force":0.0544,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52344,-0.02047,0.08947]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4406.0,"contact_point_centroid":[0.54969,0.01876,0.18446],"force_p95":0.1158,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25787,"mean_force":0.07137,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54581,0.03742,0.18474]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53705,-0.02122,-0.00207],"force_p95":0.1425,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19343,"mean_force":0.12839,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5237,-0.02048,0.04582]},{"body_a":"world","body_b":"grasp_target","contact_count":872.0,"contact_point_centroid":[0.53702,-0.02132,-0.00185],"force_p95":0.13717,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12319,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5125,-0.00823,0.24938]},{"body_a":"world","body_b":"grasp_target","contact_count":192.0,"contact_point_centroid":[0.61141,0.1864,-0.00194],"force_p95":0.12602,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12609,"mean_force":0.12417,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60528,0.21479,0.32695]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.61141,0.18639,-0.00199],"force_p95":0.1227,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12316,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60407,0.21763,0.31354]},{"body_a":"world","body_b":"grasp_target","contact_count":1116.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52807,-0.01889,0.12628]},{"body_a":"world","body_b":"grasp_target","contact_count":180.0,"contact_point_centroid":[0.61141,0.18639,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.60454,0.21893,0.33536]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5067.0,"contact_point_centroid":[0.52337,-0.00128,0.0475],"force_p95":0.06673,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10051,"mean_force":0.04274,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52251,-0.02046,0.04445]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4929.0,"contact_point_centroid":[0.52351,-0.03974,0.04623],"force_p95":0.07056,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07291,"mean_force":0.04498,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52252,-0.02046,0.04445]},{"body_a":"left_finger","body_b":"right_finger","contact_count":305.0,"contact_point_centroid":[0.60006,0.19638,0.3243],"force_p95":0.01448,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01594,"mean_force":0.01119,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.59955,0.19637,0.32206]},{"body_a":"left_finger","body_b":"right_finger","contact_count":203.0,"contact_point_centroid":[0.6055,0.21481,0.3294],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01263,"mean_force":0.01048,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60528,0.2148,0.32693]}],"total_contact_groups":17},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61141,0.18639,0.01602],"final_tcp_position":[0.60598,0.22152,0.33912],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":2.40588,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":219.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":872.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.52711,-0.01727,0.19639],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1707,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":279.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1116.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53122,-0.0206,0.05493],"tcp_start":[0.52711,-0.01727,0.19639],"tcp_to_object_dist_end":0.02949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53695,-0.02073,0.02572],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31645,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13979,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11796.0,"raw_peak_contact_force":0.19343,"tcp_end":[0.52248,-0.02046,0.04441],"tcp_start":[0.53122,-0.0206,0.05493],"tcp_to_object_dist_end":0.02364,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53401,-0.0205,0.11247],"object_pos_start":[0.53695,-0.02073,0.02572],"object_to_goal_dist_end":0.27652,"object_to_goal_dist_start":0.31645,"object_z_max":0.11236,"peak_contact_force":0.09003,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39366.0,"raw_peak_contact_force":0.41566,"subtask_id":"lift_object","tcp_end":[0.52872,-0.02057,0.13858],"tcp_start":[0.52248,-0.02046,0.04441],"tcp_to_object_dist_end":0.02665,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.61141,0.18631,0.01644],"object_pos_start":[0.53401,-0.0205,0.11247],"object_to_goal_dist_end":0.19542,"object_to_goal_dist_start":0.27652,"object_z_max":0.22224,"peak_contact_force":0.12544,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9568.0,"raw_peak_contact_force":2.40588,"tcp_end":[0.60455,0.21144,0.33499],"tcp_start":[0.52872,-0.02057,0.13858],"tcp_to_object_dist_end":0.31962,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":48.0,"n_steps_budget":1000.0,"object_pos_end":[0.61141,0.18639,0.016],"object_pos_start":[0.61141,0.18631,0.01644],"object_to_goal_dist_end":0.19584,"object_to_goal_dist_start":0.19542,"object_z_max":0.01644,"peak_contact_force":0.1232,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":395.0,"raw_peak_contact_force":0.12609,"tcp_end":[0.60632,0.21845,0.31461],"tcp_start":[0.60455,0.21144,0.33499],"tcp_to_object_dist_end":0.30037,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61141,0.18639,0.01602],"object_pos_start":[0.61141,0.18639,0.016],"object_to_goal_dist_end":0.19581,"object_to_goal_dist_start":0.19584,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12316,"subtask_id":"place_object","tcp_end":[0.60351,0.21724,0.33295],"tcp_start":[0.60632,0.21845,0.31461],"tcp_to_object_dist_end":0.31853,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":45.0,"n_steps_budget":600.0,"object_pos_end":[0.61141,0.18639,0.01602],"object_pos_start":[0.61141,0.18639,0.01602],"object_to_goal_dist_end":0.19581,"object_to_goal_dist_start":0.19581,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":180.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60598,0.22152,0.33912],"tcp_start":[0.60351,0.21724,0.33295],"tcp_to_object_dist_end":0.32505,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60185,"average_solve_count":216.0,"average_success_count":216.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.08545,"descend_to_grasp.descend_speed":0.10119,"descend_to_place.descend_speed":0.08343,"descend_to_place.place_z_offset":0.0935,"lift.lift_height":0.20146,"lift.lift_speed":0.0663,"retract_after_place.speed":0.17406,"transport.speed":0.07929},"optimized_scores":{"best_composite_score":0.03681,"best_fitness_score":0.61681,"best_task_score":0.30662},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1549.0,"contact_point_centroid":[0.61149,0.09344,-0.00274],"force_p95":0.33647,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79463,"mean_force":0.15524,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.60736,0.11888,0.27736]},{"body_a":"world","body_b":"grasp_target","contact_count":182.0,"contact_point_centroid":[0.54248,-0.02766,-0.0012],"force_p95":0.25455,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43016,"mean_force":0.07056,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52927,-0.02797,0.04586]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16264.0,"contact_point_centroid":[0.53369,-0.04687,0.09341],"force_p95":0.09574,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28143,"mean_force":0.06282,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53076,-0.02799,0.09216]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15701.0,"contact_point_centroid":[0.53351,-0.00911,0.09221],"force_p95":0.10278,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27446,"mean_force":0.06376,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53065,-0.02799,0.09066]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4910.0,"contact_point_centroid":[0.56115,-0.00224,0.18579],"force_p95":0.12431,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25471,"mean_force":0.08196,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55515,0.01637,0.18613]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4993.0,"contact_point_centroid":[0.56148,0.03572,0.18631],"force_p95":0.12154,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21629,"mean_force":0.08056,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55552,0.01711,0.18678]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54564,-0.02912,-0.00211],"force_p95":0.15096,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21199,"mean_force":0.13067,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.532,-0.02805,0.04554]},{"body_a":"world","body_b":"grasp_target","contact_count":916.0,"contact_point_centroid":[0.5456,-0.02923,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12316,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51609,-0.01147,0.24853]},{"body_a":"world","body_b":"grasp_target","contact_count":1044.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53617,-0.02605,0.12553]},{"body_a":"world","body_b":"grasp_target","contact_count":188.0,"contact_point_centroid":[0.61151,0.09352,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62737,0.15767,0.30157]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.61151,0.09352,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6256,0.15883,0.28738]},{"body_a":"world","body_b":"grasp_target","contact_count":104.0,"contact_point_centroid":[0.61151,0.09352,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.62531,0.1589,0.30749]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5061.0,"contact_point_centroid":[0.53171,-0.00884,0.04719],"force_p95":0.06805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10772,"mean_force":0.04275,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5308,-0.02802,0.04413]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4966.0,"contact_point_centroid":[0.53188,-0.04732,0.0459],"force_p95":0.07206,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07371,"mean_force":0.04486,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5308,-0.02802,0.04414]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1436.0,"contact_point_centroid":[0.61012,0.12367,0.28394],"force_p95":0.01227,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01638,"mean_force":0.01071,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.60984,0.12367,0.28165]},{"body_a":"left_finger","body_b":"right_finger","contact_count":197.0,"contact_point_centroid":[0.62767,0.15769,0.30381],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01268,"mean_force":0.0106,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62738,0.15768,0.30151]}],"total_contact_groups":17},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.61151,0.09352,0.01602],"final_tcp_position":[0.62626,0.15976,0.30878],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.79463,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":230.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":916.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53448,-0.02394,0.19519],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16961,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":261.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1044.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53965,-0.02826,0.05501],"tcp_start":[0.53448,-0.02394,0.19519],"tcp_to_object_dist_end":0.02961,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54555,-0.02841,0.02561],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26057,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14719,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11827.0,"raw_peak_contact_force":0.21199,"tcp_end":[0.53077,-0.02802,0.0441],"tcp_start":[0.53965,-0.02826,0.05501],"tcp_to_object_dist_end":0.02367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54429,-0.02832,0.12386],"object_pos_start":[0.54555,-0.02841,0.02561],"object_to_goal_dist_end":0.21909,"object_to_goal_dist_start":0.26057,"object_z_max":0.12375,"peak_contact_force":0.09652,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32147.0,"raw_peak_contact_force":0.43016,"subtask_id":"lift_object","tcp_end":[0.53579,-0.02812,0.15151],"tcp_start":[0.53077,-0.02802,0.0441],"tcp_to_object_dist_end":0.02892,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":911.0,"n_steps_budget":1000.0,"object_pos_end":[0.61151,0.09352,0.01602],"object_pos_start":[0.54429,-0.02832,0.12386],"object_to_goal_dist_end":0.17732,"object_to_goal_dist_start":0.21909,"object_z_max":0.19487,"peak_contact_force":0.12263,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12888.0,"raw_peak_contact_force":1.79463,"tcp_end":[0.6266,0.1559,0.31044],"tcp_start":[0.53579,-0.02812,0.15151],"tcp_to_object_dist_end":0.30133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":47.0,"n_steps_budget":1000.0,"object_pos_end":[0.61151,0.09352,0.01602],"object_pos_start":[0.61151,0.09352,0.01602],"object_to_goal_dist_end":0.17732,"object_to_goal_dist_start":0.17732,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":385.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62838,0.15962,0.28869],"tcp_start":[0.6266,0.1559,0.31044],"tcp_to_object_dist_end":0.28108,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61151,0.09352,0.01602],"object_pos_start":[0.61151,0.09352,0.01602],"object_to_goal_dist_end":0.17732,"object_to_goal_dist_start":0.17732,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.62482,0.1585,0.30674],"tcp_start":[0.62838,0.15962,0.28869],"tcp_to_object_dist_end":0.29819,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":26.0,"n_steps_budget":600.0,"object_pos_end":[0.61151,0.09352,0.01602],"object_pos_start":[0.61151,0.09352,0.01602],"object_to_goal_dist_end":0.17732,"object_to_goal_dist_start":0.17732,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":104.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62626,0.15976,0.30878],"tcp_start":[0.62482,0.1585,0.30674],"tcp_to_object_dist_end":0.30053,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.52632,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.1417,"descend_to_grasp.descend_speed":0.0606,"descend_to_place.descend_speed":0.05324,"descend_to_place.place_z_offset":0.06979,"lift.lift_height":0.1691,"lift.lift_speed":0.10921,"retract_after_place.speed":0.22979,"transport.speed":0.2624},"optimized_scores":{"best_composite_score":0.1074,"best_fitness_score":0.6874,"best_task_score":0.44894},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":719.0,"contact_point_centroid":[0.57459,0.10913,-0.00352],"force_p95":0.68893,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.9012,"mean_force":0.18861,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.57684,0.12108,0.24689]},{"body_a":"world","body_b":"grasp_target","contact_count":127.0,"contact_point_centroid":[0.46068,-0.00045,-0.00119],"force_p95":0.22919,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37859,"mean_force":0.05365,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45094,-0.00021,0.04899]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12309.0,"contact_point_centroid":[0.45478,-0.01921,0.10655],"force_p95":0.10243,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28779,"mean_force":0.0653,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4529,-0.00028,0.10626]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12775.0,"contact_point_centroid":[0.45536,0.01861,0.10726],"force_p95":0.09742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27509,"mean_force":0.06328,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45294,-0.00028,0.10659]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2757.0,"contact_point_centroid":[0.49499,0.01369,0.196],"force_p95":0.16405,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26642,"mean_force":0.09733,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.48919,0.03216,0.19827]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3064.0,"contact_point_centroid":[0.49747,0.0529,0.1973],"force_p95":0.13151,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21763,"mean_force":0.08773,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.4916,0.03464,0.19957]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46285,-0.00014,-0.00202],"force_p95":0.12935,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14769,"mean_force":0.12452,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45312,-0.00018,0.0485]},{"body_a":"world","body_b":"grasp_target","contact_count":768.0,"contact_point_centroid":[0.46286,-7e-05,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12326,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48424,-4e-05,0.25101]},{"body_a":"world","body_b":"grasp_target","contact_count":388.0,"contact_point_centroid":[0.57477,0.1092,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60072,0.14572,0.23655]},{"body_a":"world","body_b":"grasp_target","contact_count":1156.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46294,-9e-05,0.12802]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57477,0.1092,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59942,0.14751,0.20961]},{"body_a":"world","body_b":"grasp_target","contact_count":464.0,"contact_point_centroid":[0.57477,0.1092,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.60096,0.14877,0.24058]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4129.0,"contact_point_centroid":[0.45137,-0.0194,0.04899],"force_p95":0.07593,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09828,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45207,-0.00019,0.04749]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4864.0,"contact_point_centroid":[0.45219,0.01887,0.04875],"force_p95":0.06782,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08799,"mean_force":0.04462,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45207,-0.00019,0.04749]},{"body_a":"left_finger","body_b":"right_finger","contact_count":554.0,"contact_point_centroid":[0.5838,0.1275,0.25263],"force_p95":0.01421,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01587,"mean_force":0.01088,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.58324,0.12749,0.25046]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.60215,0.14824,0.20752],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.0101,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60167,0.14822,0.20539]}],"total_contact_groups":17},"final_pose_error":0.01981,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.57477,0.1092,0.01602],"final_tcp_position":[0.60456,0.15062,0.25331],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":1.9012,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":193.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":768.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.46772,-7e-05,0.19894],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17299,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":289.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1156.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.45987,-0.00011,0.05541],"tcp_start":[0.46772,-7e-05,0.19894],"tcp_to_object_dist_end":0.02954,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46277,-0.00033,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23337,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.1288,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.14769,"tcp_end":[0.45204,-0.00019,0.04746],"tcp_start":[0.45987,-0.00011,0.05541],"tcp_to_object_dist_end":0.02407,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":792.0,"n_steps_budget":870.0,"object_pos_end":[0.46867,-9e-05,0.15344],"object_pos_start":[0.46277,-0.00033,0.02591],"object_to_goal_dist_end":0.21069,"object_to_goal_dist_start":0.23337,"object_z_max":0.15332,"peak_contact_force":0.09278,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25211.0,"raw_peak_contact_force":0.37859,"subtask_id":"lift_object","tcp_end":[0.45877,-0.00034,0.18312],"tcp_start":[0.45204,-0.00019,0.04746],"tcp_to_object_dist_end":0.03128,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":555.0,"n_steps_budget":1000.0,"object_pos_end":[0.57477,0.1092,0.01602],"object_pos_start":[0.46867,-9e-05,0.15344],"object_to_goal_dist_end":0.12013,"object_to_goal_dist_start":0.21069,"object_z_max":0.18362,"peak_contact_force":0.12265,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7094.0,"raw_peak_contact_force":1.9012,"tcp_end":[0.59871,0.14313,0.25907],"tcp_start":[0.45877,-0.00034,0.18312],"tcp_to_object_dist_end":0.24658,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":97.0,"n_steps_budget":1000.0,"object_pos_end":[0.57477,0.1092,0.01602],"object_pos_start":[0.57477,0.1092,0.01602],"object_to_goal_dist_end":0.12013,"object_to_goal_dist_start":0.12013,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":801.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.60351,0.14859,0.21008],"tcp_start":[0.59871,0.14313,0.25907],"tcp_to_object_dist_end":0.20009,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57477,0.1092,0.01602],"object_pos_start":[0.57477,0.1092,0.01602],"object_to_goal_dist_end":0.12013,"object_to_goal_dist_start":0.12013,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.59809,0.14709,0.22938],"tcp_start":[0.60351,0.14859,0.21008],"tcp_to_object_dist_end":0.21795,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":116.0,"n_steps_budget":600.0,"object_pos_end":[0.57477,0.1092,0.01602],"object_pos_start":[0.57477,0.1092,0.01602],"object_to_goal_dist_end":0.12013,"object_to_goal_dist_start":0.12013,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":464.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60456,0.15062,0.25331],"tcp_start":[0.59809,0.14709,0.22938],"tcp_to_object_dist_end":0.24272,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```