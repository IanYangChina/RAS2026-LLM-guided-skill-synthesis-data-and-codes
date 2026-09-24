## Search State

- **Seed**: 9
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0128 | 0.35 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | 9 | -0.3728 | 0.17 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | 9 | -0.3608 | 0.17 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | 8 | 0.0544 | 0.34 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3770 | 0.77 | ✅ accepted |

**Proposal policy**: task_score is 0.35 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.013) — your mutation base

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

- **Composite score**: 0.013
- **task_score** (E): 0.348
- **fitness_score**: 0.643  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1099 |
| descend_to_grasp | 1.00 | 1.00 | 0.1471 |
| grasp | 1.00 | 1.00 | 0.0130 |
| lift | 0.67 | 1.00 | 0.1040 |
| transport | 1.00 | 1.00 | 0.2638 |
| descend_to_place | 1.00 | 1.00 | 0.0513 |
| release | 1.00 | 1.00 | 0.0191 |
| retract | 1.00 | 1.00 | 0.1302 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.014, 0.197) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.014, 0.197)→(0.510, -0.016, 0.050) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, -0.016, 0.050)→(0.502, -0.016, 0.040) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 42.000 | 0.139 | 0.186 |
| lift | lift | 0.67 / step_budget | (0.502, -0.016, 0.040)→(0.507, -0.016, 0.144) | (0.515, -0.016, 0.026)→(0.515, -0.016, 0.121) | 0.270→0.235 | 1.00 / 30.000 | 0.097 | 0.451 |
| transport | approach | 1.00 / step_budget | (0.507, -0.016, 0.144)→(0.609, 0.167, 0.298) | (0.515, -0.016, 0.121)→(0.609, 0.117, 0.088) | 0.235→0.170 | 1.00 / 14.333 | 0.115 | 1.292 |
| descend_to_place | descend | 1.00 / step_budget | (0.609, 0.167, 0.298)→(0.613, 0.176, 0.248) | (0.609, 0.117, 0.088)→(0.610, 0.118, 0.073) | 0.170→0.155 | 1.00 / 14.333 | 0.116 | 0.174 |
| release | release | 1.00 / step_budget | (0.613, 0.176, 0.248)→(0.608, 0.174, 0.266) | (0.610, 0.118, 0.073)→(0.606, 0.118, 0.016) | 0.155→0.169 | 1.00 / 3.667 | 0.191 | 0.690 |
| retract | retract | 1.00 / step_budget | (0.608, 0.174, 0.266)→(0.607, 0.174, 0.396) | (0.606, 0.118, 0.016)→(0.602, 0.116, 0.019) | 0.169→0.167 | 1.00 / 4.000 | 0.123 | 0.187 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.515
- phase_score: 0.245
- phase_breakdown.lift_object_score: 0.433
- phase_breakdown.reach_object_score: 0.204
- phase_breakdown.place_object_score: 0.158
- grasp_place_fitness: 0.727

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.727
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.515
- **Median Q (composite search score)**: -0.020
- **K-run variance**: 0.0036
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.278


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78788,"average_solve_count":231.0,"average_success_count":231.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.09201,"descend_to_grasp.descend_speed":0.11521,"descend_to_place.descend_speed":0.06739,"descend_to_place.place_z_offset":0.05132,"lift.lift_height":0.15108,"lift.lift_speed":0.06515,"release.release_duration":1.01252,"retract.retract_speed":0.12674,"transport.transport_speed":0.07437},"optimized_scores":{"best_composite_score":-0.03841,"best_fitness_score":0.59159,"best_task_score":0.24493},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":720.0,"contact_point_centroid":[0.60803,0.13873,-0.00388],"force_p95":0.83066,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.94642,"mean_force":0.19959,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.59328,0.18091,0.30963]},{"body_a":"world","body_b":"grasp_target","contact_count":180.0,"contact_point_centroid":[0.53402,-0.02012,-0.00117],"force_p95":0.25823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46265,"mean_force":0.07052,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52124,-0.02045,0.0411]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15097.0,"contact_point_centroid":[0.52635,-0.00153,0.08918],"force_p95":0.10332,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29858,"mean_force":0.06651,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52384,-0.02041,0.0875]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16353.0,"contact_point_centroid":[0.52641,-0.03919,0.08797],"force_p95":0.09707,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28139,"mean_force":0.06231,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52378,-0.02041,0.08678]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6868.0,"contact_point_centroid":[0.5568,0.07155,0.20175],"force_p95":0.15175,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26267,"mean_force":0.09383,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55089,0.05313,0.2016]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7443.0,"contact_point_centroid":[0.55845,0.04021,0.20598],"force_p95":0.12209,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19568,"mean_force":0.08727,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55269,0.05846,0.20617]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53705,-0.02116,-0.00207],"force_p95":0.1445,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19486,"mean_force":0.12854,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52386,-0.02051,0.04079]},{"body_a":"world","body_b":"grasp_target","contact_count":864.0,"contact_point_centroid":[0.53702,-0.02132,-0.00185],"force_p95":0.13725,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12319,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51265,-0.00823,0.24946]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4097.0,"contact_point_centroid":[0.52363,-0.00128,0.04214],"force_p95":0.07837,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13422,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52267,-0.02049,0.03942]},{"body_a":"world","body_b":"grasp_target","contact_count":412.0,"contact_point_centroid":[0.60805,0.13891,-0.00199],"force_p95":0.12266,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12272,"mean_force":0.12261,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60198,0.20755,0.30184]},{"body_a":"world","body_b":"grasp_target","contact_count":1084.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52847,-0.01891,0.1236]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.60805,0.13891,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60202,0.21609,0.27371]},{"body_a":"world","body_b":"grasp_target","contact_count":1948.0,"contact_point_centroid":[0.60805,0.13891,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.60025,0.21504,0.35719]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4930.0,"contact_point_centroid":[0.52361,-0.03958,0.04122],"force_p95":0.07052,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07689,"mean_force":0.04464,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52267,-0.02049,0.03943]},{"body_a":"left_finger","body_b":"right_finger","contact_count":617.0,"contact_point_centroid":[0.59493,0.18452,0.31499],"force_p95":0.01369,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01644,"mean_force":0.01098,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.59448,0.18451,0.31267]},{"body_a":"left_finger","body_b":"right_finger","contact_count":432.0,"contact_point_centroid":[0.60234,0.20755,0.30413],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.01061,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60197,0.20754,0.3019]}],"total_contact_groups":17},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.60805,0.13891,0.01602],"final_tcp_position":[0.60115,0.21527,0.42336],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.94642,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":217.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":864.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.52736,-0.01726,0.19661],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17091,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":271.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1084.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.5315,-0.02063,0.04996],"tcp_start":[0.52736,-0.01726,0.19661],"tcp_to_object_dist_end":0.02458,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53694,-0.02053,0.02573],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31629,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14052,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10827.0,"raw_peak_contact_force":0.19486,"tcp_end":[0.52264,-0.02049,0.03939],"tcp_start":[0.5315,-0.02063,0.04996],"tcp_to_object_dist_end":0.01978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53982,-0.02033,0.12093],"object_pos_start":[0.53694,-0.02053,0.02573],"object_to_goal_dist_end":0.27202,"object_to_goal_dist_start":0.31629,"object_z_max":0.12081,"peak_contact_force":0.11316,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":31630.0,"raw_peak_contact_force":0.46265,"subtask_id":"lift_object","tcp_end":[0.53001,-0.02043,0.14446],"tcp_start":[0.52264,-0.02049,0.03939],"tcp_to_object_dist_end":0.0255,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60805,0.13892,0.01602],"object_pos_start":[0.53982,-0.02033,0.12093],"object_to_goal_dist_end":0.21102,"object_to_goal_dist_start":0.27202,"object_z_max":0.2423,"peak_contact_force":0.12272,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15648.0,"raw_peak_contact_force":1.94642,"tcp_end":[0.59957,0.19958,0.3254],"tcp_start":[0.53001,-0.02043,0.14446],"tcp_to_object_dist_end":0.31539,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":103.0,"n_steps_budget":1000.0,"object_pos_end":[0.60805,0.13891,0.01602],"object_pos_start":[0.60805,0.13892,0.01602],"object_to_goal_dist_end":0.21102,"object_to_goal_dist_start":0.21102,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":844.0,"raw_peak_contact_force":0.12272,"subtask_id":"place_object","tcp_end":[0.60497,0.21704,0.27473],"tcp_start":[0.59957,0.19958,0.3254],"tcp_to_object_dist_end":0.27027,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60805,0.13891,0.01602],"object_pos_start":[0.60805,0.13891,0.01602],"object_to_goal_dist_end":0.21102,"object_to_goal_dist_start":0.21102,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60118,0.21561,0.29316],"tcp_start":[0.60497,0.21704,0.27473],"tcp_to_object_dist_end":0.28764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":487.0,"n_steps_budget":750.0,"object_pos_end":[0.60805,0.13891,0.01602],"object_pos_start":[0.60805,0.13891,0.01602],"object_to_goal_dist_end":0.21102,"object_to_goal_dist_start":0.21102,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1948.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60115,0.21527,0.42336],"tcp_start":[0.60118,0.21561,0.29316],"tcp_to_object_dist_end":0.41449,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.52,"average_solve_count":275.0,"average_success_count":275.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.04564,"descend_to_grasp.descend_speed":0.0614,"descend_to_place.descend_speed":0.12086,"descend_to_place.place_z_offset":0.05815,"lift.lift_height":0.17146,"lift.lift_speed":0.06771,"release.release_duration":1.05134,"retract.retract_speed":0.13728,"transport.transport_speed":0.07153},"optimized_scores":{"best_composite_score":-0.01984,"best_fitness_score":0.61016,"best_task_score":0.28247},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1510.0,"contact_point_centroid":[0.60929,0.06729,-0.00278],"force_p95":0.36086,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.7809,"mean_force":0.15403,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.6086,0.1204,0.27802]},{"body_a":"world","body_b":"grasp_target","contact_count":202.0,"contact_point_centroid":[0.54275,-0.02739,-0.00123],"force_p95":0.25457,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4717,"mean_force":0.0726,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52901,-0.02798,0.04044]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14447.0,"contact_point_centroid":[0.53442,-0.00912,0.08935],"force_p95":0.10615,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29955,"mean_force":0.06874,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53139,-0.02795,0.08781]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15542.0,"contact_point_centroid":[0.53445,-0.04664,0.08836],"force_p95":0.09895,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28891,"mean_force":0.06497,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53136,-0.02795,0.08724]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3596.0,"contact_point_centroid":[0.56128,0.03282,0.18154],"force_p95":0.16136,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27195,"mean_force":0.11114,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55545,0.01444,0.18206]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54564,-0.02905,-0.00211],"force_p95":0.15329,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21651,"mean_force":0.13081,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53191,-0.02808,0.04033]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4559.0,"contact_point_centroid":[0.56225,-0.00174,0.18267],"force_p95":0.13439,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19242,"mean_force":0.08882,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55632,0.01623,0.18365]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4088.0,"contact_point_centroid":[0.53186,-0.00883,0.04162],"force_p95":0.07971,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14217,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5307,-0.02804,0.03891]},{"body_a":"world","body_b":"grasp_target","contact_count":964.0,"contact_point_centroid":[0.5456,-0.02923,-0.00186],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12313,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51575,-0.01134,0.24897]},{"body_a":"world","body_b":"grasp_target","contact_count":1132.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53591,-0.02603,0.12314]},{"body_a":"world","body_b":"grasp_target","contact_count":404.0,"contact_point_centroid":[0.60932,0.06738,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62758,0.15844,0.28425]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.60932,0.06738,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62547,0.16017,0.25281]},{"body_a":"world","body_b":"grasp_target","contact_count":1944.0,"contact_point_centroid":[0.60932,0.06738,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.62322,0.15928,0.33639]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4966.0,"contact_point_centroid":[0.5318,-0.04716,0.04068],"force_p95":0.07208,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07692,"mean_force":0.04456,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5307,-0.02804,0.03892]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1405.0,"contact_point_centroid":[0.61105,0.12479,0.28414],"force_p95":0.01253,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01613,"mean_force":0.01071,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.61082,0.12479,0.28202]},{"body_a":"left_finger","body_b":"right_finger","contact_count":425.0,"contact_point_centroid":[0.62806,0.15846,0.28636],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01273,"mean_force":0.01057,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62759,0.15845,0.28412]}],"total_contact_groups":17},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.60932,0.06738,0.01602],"final_tcp_position":[0.6241,0.15944,0.40219],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.7809,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":242.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":964.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53443,-0.02391,0.19533],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16976,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":283.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1132.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53962,-0.02828,0.04976],"tcp_start":[0.53443,-0.02391,0.19533],"tcp_to_object_dist_end":0.0245,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54553,-0.02819,0.02563],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.2604,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14776,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10854.0,"raw_peak_contact_force":0.21651,"tcp_end":[0.53067,-0.02804,0.03888],"tcp_start":[0.53962,-0.02828,0.04976],"tcp_to_object_dist_end":0.01991,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54715,-0.02807,0.12486],"object_pos_start":[0.54553,-0.02819,0.02563],"object_to_goal_dist_end":0.21749,"object_to_goal_dist_start":0.2604,"object_z_max":0.12477,"peak_contact_force":0.10907,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":30191.0,"raw_peak_contact_force":0.4717,"subtask_id":"lift_object","tcp_end":[0.5374,-0.02801,0.14852],"tcp_start":[0.53067,-0.02804,0.03888],"tcp_to_object_dist_end":0.02559,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":923.0,"n_steps_budget":1000.0,"object_pos_end":[0.60932,0.06738,0.01602],"object_pos_start":[0.54715,-0.02807,0.12486],"object_to_goal_dist_end":0.18963,"object_to_goal_dist_start":0.21749,"object_z_max":0.19712,"peak_contact_force":0.12263,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11070.0,"raw_peak_contact_force":1.7809,"tcp_end":[0.62662,0.15588,0.31028],"tcp_start":[0.5374,-0.02801,0.14852],"tcp_to_object_dist_end":0.30777,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":101.0,"n_steps_budget":1000.0,"object_pos_end":[0.60932,0.06738,0.01602],"object_pos_start":[0.60932,0.06738,0.01602],"object_to_goal_dist_end":0.18963,"object_to_goal_dist_start":0.18963,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":829.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.62882,0.16114,0.25419],"tcp_start":[0.62662,0.15588,0.31028],"tcp_to_object_dist_end":0.2567,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60932,0.06738,0.01602],"object_pos_start":[0.60932,0.06738,0.01602],"object_to_goal_dist_end":0.18963,"object_to_goal_dist_start":0.18963,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62444,0.15979,0.27218],"tcp_start":[0.62882,0.16114,0.25419],"tcp_to_object_dist_end":0.27273,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":486.0,"n_steps_budget":690.0,"object_pos_end":[0.60932,0.06738,0.01602],"object_pos_start":[0.60932,0.06738,0.01602],"object_to_goal_dist_end":0.18963,"object_to_goal_dist_start":0.18963,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1944.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6241,0.15944,0.40219],"tcp_start":[0.62444,0.15979,0.27218],"tcp_to_object_dist_end":0.39727,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33566,"average_solve_count":286.0,"average_success_count":286.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.08874,"descend_to_grasp.descend_speed":0.05325,"descend_to_place.descend_speed":0.08617,"descend_to_place.place_z_offset":0.07411,"lift.lift_height":0.23581,"lift.lift_speed":0.02935,"release.release_duration":1.55991,"retract.retract_speed":0.09454,"transport.transport_speed":0.06627},"optimized_scores":{"best_composite_score":0.09678,"best_fitness_score":0.72678,"best_task_score":0.51536},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":140.0,"contact_point_centroid":[0.59299,0.14332,-0.00971],"force_p95":1.46065,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.82447,"mean_force":0.52337,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59843,0.14745,0.22725]},{"body_a":"world","body_b":"grasp_target","contact_count":161.0,"contact_point_centroid":[0.45862,-0.00026,-0.00118],"force_p95":0.35976,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41884,"mean_force":0.08857,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45067,-0.00022,0.04397]},{"body_a":"world","body_b":"grasp_target","contact_count":1868.0,"contact_point_centroid":[0.58865,0.14186,-0.00214],"force_p95":0.20126,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3169,"mean_force":0.12648,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.59641,0.1468,0.30144]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":912.0,"contact_point_centroid":[0.60495,0.12964,0.20801],"force_p95":0.14531,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30224,"mean_force":0.07391,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60157,0.14845,0.20883]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":969.0,"contact_point_centroid":[0.60534,0.16717,0.20808],"force_p95":0.12298,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29911,"mean_force":0.06855,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60159,0.14845,0.20887]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1140.0,"contact_point_centroid":[0.60604,0.16531,0.23798],"force_p95":0.13618,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27682,"mean_force":0.08128,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60149,0.14669,0.23763]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20267.0,"contact_point_centroid":[0.45091,0.01892,0.0937],"force_p95":0.07192,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25928,"mean_force":0.04969,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45067,-0.00022,0.09152]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20255.0,"contact_point_centroid":[0.45083,-0.01937,0.0942],"force_p95":0.07298,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25642,"mean_force":0.04959,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45069,-0.00022,0.09194]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1036.0,"contact_point_centroid":[0.60552,0.12805,0.23708],"force_p95":0.14493,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25555,"mean_force":0.08756,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60151,0.14671,0.23735]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17119.0,"contact_point_centroid":[0.52168,0.05001,0.19575],"force_p95":0.07395,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14889,"mean_force":0.04753,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52163,0.06908,0.1941]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15579.0,"contact_point_centroid":[0.52399,0.08984,0.19735],"force_p95":0.07941,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14872,"mean_force":0.05197,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52325,0.07065,0.19542]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46285,-9e-05,-0.00202],"force_p95":0.12866,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14708,"mean_force":0.12445,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45307,-0.00019,0.04355]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.46286,-7e-05,-0.00184],"force_p95":0.1373,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12324,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48431,-4e-05,0.25111]},{"body_a":"world","body_b":"grasp_target","contact_count":1212.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46303,-9e-05,0.12555]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4864.0,"contact_point_centroid":[0.45219,0.019,0.04443],"force_p95":0.06805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08881,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45201,-0.0002,0.04254]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4854.0,"contact_point_centroid":[0.45222,-0.01939,0.04444],"force_p95":0.06798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08653,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45201,-0.0002,0.04254]}],"total_contact_groups":16},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.58744,0.14178,0.02602],"final_tcp_position":[0.59709,0.14692,0.36378],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":1.82447,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":201.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":800.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.46782,-7e-05,0.19896],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":303.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1212.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.45987,-0.00011,0.05046],"tcp_start":[0.46782,-7e-05,0.19896],"tcp_to_object_dist_end":0.02462,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46276,-0.00016,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23327,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12843,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11518.0,"raw_peak_contact_force":0.14708,"tcp_end":[0.45199,-0.0002,0.04251],"tcp_start":[0.45987,-0.00011,0.05046],"tcp_to_object_dist_end":0.01979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45794,-0.00012,0.1173],"object_pos_start":[0.46276,-0.00016,0.02591],"object_to_goal_dist_end":0.21586,"object_to_goal_dist_start":0.23327,"object_z_max":0.11721,"peak_contact_force":0.0674,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40683.0,"raw_peak_contact_force":0.41884,"subtask_id":"lift_object","tcp_end":[0.45309,-0.00021,0.13935],"tcp_start":[0.45199,-0.0002,0.04251],"tcp_to_object_dist_end":0.02258,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":822.0,"n_steps_budget":1000.0,"object_pos_end":[0.60824,0.14476,0.23151],"object_pos_start":[0.45794,-0.00012,0.1173],"object_to_goal_dist_end":0.10964,"object_to_goal_dist_start":0.21586,"object_z_max":0.23139,"peak_contact_force":0.09941,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32698.0,"raw_peak_contact_force":0.14889,"tcp_end":[0.59961,0.14454,0.25749],"tcp_start":[0.45309,-0.00021,0.13935],"tcp_to_object_dist_end":0.02738,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":85.0,"n_steps_budget":1000.0,"object_pos_end":[0.61158,0.14873,0.1872],"object_pos_start":[0.60824,0.14476,0.23151],"object_to_goal_dist_end":0.06516,"object_to_goal_dist_start":0.10964,"object_z_max":0.23154,"peak_contact_force":0.10208,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2176.0,"raw_peak_contact_force":0.27682,"subtask_id":"place_object","tcp_end":[0.60376,0.14894,0.21428],"tcp_start":[0.59961,0.14454,0.25749],"tcp_to_object_dist_end":0.02819,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60212,0.14827,0.01679],"object_pos_start":[0.61158,0.14873,0.1872],"object_to_goal_dist_end":0.10581,"object_to_goal_dist_start":0.06516,"object_z_max":0.1872,"peak_contact_force":0.3282,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2021.0,"raw_peak_contact_force":1.82447,"tcp_end":[0.5984,0.14744,0.2335],"tcp_start":[0.60376,0.14894,0.21428],"tcp_to_object_dist_end":0.21675,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":496.0,"n_steps_budget":990.0,"object_pos_end":[0.58744,0.14178,0.02602],"object_pos_start":[0.60212,0.14827,0.01679],"object_to_goal_dist_end":0.09943,"object_to_goal_dist_start":0.10581,"object_z_max":0.02913,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1868.0,"raw_peak_contact_force":0.3169,"tcp_end":[0.59709,0.14692,0.36378],"tcp_start":[0.5984,0.14744,0.2335],"tcp_to_object_dist_end":0.33794,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```