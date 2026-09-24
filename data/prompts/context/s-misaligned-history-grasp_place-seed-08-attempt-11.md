## Search State

- **Seed**: 8
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | time_limit | 7  | -0.0402 | 0.22 | ❌ rejected |
| 10 | approach → descend → grasp → lift → push → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | time_limit | 9  | 0.0590 | 0.22 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | time_limit | 7  | 0.1448 | 0.35 | ✅ accepted |
| 8 | approach → descend → grasp → lift → descend → release → retract | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | time_limit | 7  | 0.1356 | 0.22 | ✅ accepted |
| 7 | approach → descend → grasp → lift → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | time_limit | 6  | 0.0582 | 0.22 | ❌ rejected |

**Proposal policy**: task_score is 0.22 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`
- Frozen object start: [0.48269722766055606, 0.048727684333792556, 0.03]
- Frozen task target: [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]
- Goal object position: (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.48269722766055606, 0.048727684333792556, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.4827, 0.0487, 0.03]
  frozen_task_target: [0.5819, 0.2289, 0.2305]
  frozen_object_starts: {'grasp_target': [0.48269722766055606, 0.048727684333792556, 0.03]}
  frozen_targets: {'place_target': [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c

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
| `object` | offset from object initial position (0.48269722766055606, 0.048727684333792556, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5818710838485517, 0.2288548935820029, 0.2304844767544324) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

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

## Current Skill (Q=0.058) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_pregrasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.1
- id: reach_grasp
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.1
- id: lift_object
  target_entity: object
  metric: goal_progress
  weight: 0.3
- id: place_object
  target_entity: object
  weight: 0.5
phases:
- id: approach_1
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
    - 0.12
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    pregrasp_height:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_pregrasp
- id: descend_1
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
    - 0.03
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_grasp
- id: grasp_1
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
      mode: keep_current
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
- id: lift_transport_1
  type: lift
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.18
    offset_along_axis:
      distance: 0.3
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    horizontal_distance:
      type: scalar
      range:
      - 0.15
      - 0.45
      default: 0.3
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_height:
      type: scalar
      range:
      - 0.12
      - 0.3
      default: 0.18
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.15
    on_failure: abort
  subtask_id: lift_object
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
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.03
      default: 0.01
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_object
- id: release_1
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
      mode: keep_current
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.2
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.12]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - pregrasp_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03]
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift_transport_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.18], offset_along_axis={axis=task_goal_direction, distance=0.3, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - horizontal_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=abort, threshold=0.15
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.01]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.2]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.058
- **task_score** (E): 0.220
- **fitness_score**: 0.588  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1313 |
| descend_1 | 1.00 | 1.00 | 0.1385 |
| grasp_1 | 1.00 | 1.00 | 0.0124 |
| lift_vertical | 0.67 | 0.67 | 0.1602 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.000, 0.177) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.516, -0.000, 0.177)→(0.517, -0.001, 0.039) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.517, -0.001, 0.039)→(0.508, -0.001, 0.029) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 41.667 | 0.143 | 0.204 |
| lift_vertical | lift | 0.67 / step_budget | (0.508, -0.001, 0.029)→(0.516, -0.001, 0.189) | (0.522, -0.001, 0.026)→(0.527, 0.001, 0.161) | 0.289→0.229 | 0.67 / 7.667 | 0.132 | 0.618 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.244
- phase_score: 0.233
- phase_breakdown.reach_grasp_score: 0.607
- phase_breakdown.place_object_score: 0.000
- phase_breakdown.lift_object_score: 0.274
- phase_breakdown.reach_pregrasp_score: 0.903
- grasp_place_fitness: 0.602

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.602
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.244
- **Median Q (composite search score)**: 0.067
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.382


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2cbd02033d1f1347f2ac2d0b012406a96501e6b48f5b172bd88b34d6c745630c`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5745d7c2d025a63f908a4bf0f58182445bb06541d436718f39304ac5569d60c0`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93878,"average_solve_count":98.0,"average_success_count":98.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.pregrasp_height":0.11027,"descend_1.grasp_z_offset":0.00065,"descend_to_place.place_z_offset":-0.00242,"lift_vertical.lift_height":0.18619,"lift_vertical.lift_speed":0.10425,"transport_to_goal.transport_height":0.25979,"transport_to_goal.transport_speed":0.15362},"optimized_scores":{"best_composite_score":0.07221,"best_fitness_score":0.60221,"best_task_score":0.24382},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":140.0,"contact_point_centroid":[0.47985,0.04568,-0.00126],"force_p95":0.45675,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64483,"mean_force":0.07828,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.46924,0.04687,0.02938]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13066.0,"contact_point_centroid":[0.47442,0.02793,0.09743],"force_p95":0.13272,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31576,"mean_force":0.07485,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.47147,0.04665,0.09637]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13820.0,"contact_point_centroid":[0.47436,0.06538,0.09707],"force_p95":0.13607,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31267,"mean_force":0.07346,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.4715,0.04665,0.09636]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48275,0.04835,-0.00215],"force_p95":0.16802,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24911,"mean_force":0.1346,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47161,0.04715,0.02872]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3883.0,"contact_point_centroid":[0.47098,0.02778,0.03056],"force_p95":0.08428,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1509,"mean_force":0.05417,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47051,0.04704,0.0276]},{"body_a":"world","body_b":"grasp_target","contact_count":1920.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.1331,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48949,0.02166,0.22409]},{"body_a":"world","body_b":"grasp_target","contact_count":1456.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47813,0.04591,0.0917]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5432.0,"contact_point_centroid":[0.47009,0.06616,0.03004],"force_p95":0.07148,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08719,"mean_force":0.04153,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47051,0.04704,0.02761]}],"total_contact_groups":8},"final_pose_error":0.01753,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.48906,0.05287,0.15815],"final_tcp_position":[0.47834,0.04668,0.19469],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.64483,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":481.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1920.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pregrasp","tcp_end":[0.48059,0.04427,0.14873],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":364.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1456.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.4782,0.0478,0.03549],"tcp_start":[0.48059,0.04427,0.14873],"tcp_to_object_dist_end":0.01053,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.04702,0.02549],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29144,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15812,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11115.0,"raw_peak_contact_force":0.24911,"tcp_end":[0.47048,0.04703,0.02757],"tcp_start":[0.4782,0.0478,0.03549],"tcp_to_object_dist_end":0.01231,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48906,0.05287,0.15815],"object_pos_start":[0.48261,0.04702,0.02549],"object_to_goal_dist_end":0.2117,"object_to_goal_dist_start":0.29144,"object_z_max":0.16709,"peak_contact_force":0.0,"phase_name":"lift_vertical","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27026.0,"raw_peak_contact_force":0.64483,"subtask_id":"lift_object","tcp_end":[0.47834,0.04668,0.19469],"tcp_start":[0.47048,0.04703,0.02757],"tcp_to_object_dist_end":0.03857,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2b35d39beba75b46a5edd8e67b975c00ef2c88fb75a3753bdd32db5918adf9e2`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93333,"average_solve_count":90.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.pregrasp_height":0.17235,"descend_1.grasp_z_offset":0.0049,"descend_to_place.place_z_offset":-0.01797,"lift_vertical.lift_height":0.17329,"lift_vertical.lift_speed":0.11872,"transport_to_goal.transport_height":0.2497,"transport_to_goal.transport_speed":0.17726},"optimized_scores":{"best_composite_score":0.03551,"best_fitness_score":0.56551,"best_task_score":0.17573},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":175.0,"contact_point_centroid":[0.53429,-0.02072,-0.00121],"force_p95":0.38612,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61874,"mean_force":0.0887,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.52181,-0.02082,0.03092]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10503.0,"contact_point_centroid":[0.52821,-0.00196,0.09404],"force_p95":0.13505,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33111,"mean_force":0.08031,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.5247,-0.02072,0.09262]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11333.0,"contact_point_centroid":[0.52817,-0.03939,0.09221],"force_p95":0.13007,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30218,"mean_force":0.07568,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.5246,-0.02072,0.09121]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02115,-0.00204],"force_p95":0.13605,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1714,"mean_force":0.12641,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52455,-0.02088,0.03083]},{"body_a":"world","body_b":"grasp_target","contact_count":1332.0,"contact_point_centroid":[0.53702,-0.02132,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51348,-0.00914,0.25334]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52927,-0.01982,0.12269]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4102.0,"contact_point_centroid":[0.52396,-0.00165,0.03223],"force_p95":0.07691,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11849,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52334,-0.02085,0.02945]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4903.0,"contact_point_centroid":[0.52402,-0.03994,0.0313],"force_p95":0.06906,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09152,"mean_force":0.04475,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52334,-0.02085,0.02945]}],"total_contact_groups":8},"final_pose_error":0.01467,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.54402,-0.02064,0.16345],"final_tcp_position":[0.53263,-0.02066,0.18509],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.61874,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":334.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1332.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pregrasp","tcp_end":[0.52936,-0.01871,0.20796],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18212,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.53176,-0.02101,0.03917],"tcp_start":[0.52936,-0.01871,0.20796],"tcp_to_object_dist_end":0.01417,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5369,-0.02074,0.02584],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3164,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13317,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10805.0,"raw_peak_contact_force":0.1714,"tcp_end":[0.52331,-0.02085,0.02941],"tcp_start":[0.53176,-0.02101,0.03917],"tcp_to_object_dist_end":0.01405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":842.0,"n_steps_budget":900.0,"object_pos_end":[0.54402,-0.02064,0.16345],"object_pos_start":[0.5369,-0.02074,0.02584],"object_to_goal_dist_end":0.26082,"object_to_goal_dist_start":0.3164,"object_z_max":0.16333,"peak_contact_force":0.15169,"phase_name":"lift_vertical","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22011.0,"raw_peak_contact_force":0.61874,"subtask_id":"lift_object","tcp_end":[0.53263,-0.02066,0.18509],"tcp_start":[0.52331,-0.02085,0.02941],"tcp_to_object_dist_end":0.02445,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `530652a2467d9ac78fab654e7ed7fc5283ca1649270bc8f158e04c16074f9f95`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93814,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.pregrasp_height":0.13835,"descend_1.grasp_z_offset":0.0067,"descend_to_place.place_z_offset":-0.01531,"lift_vertical.lift_height":0.25095,"lift_vertical.lift_speed":0.09662,"transport_to_goal.transport_height":0.31238,"transport_to_goal.transport_speed":0.15949},"optimized_scores":{"best_composite_score":0.06683,"best_fitness_score":0.59683,"best_task_score":0.24064},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":150.0,"contact_point_centroid":[0.54335,-0.02839,-0.00114],"force_p95":0.41441,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58934,"mean_force":0.07714,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.53008,-0.02847,0.03249]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12728.0,"contact_point_centroid":[0.53468,-0.00965,0.09767],"force_p95":0.13437,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32744,"mean_force":0.07771,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.53137,-0.02836,0.09679]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13555.0,"contact_point_centroid":[0.53469,-0.04701,0.09574],"force_p95":0.12919,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30319,"mean_force":0.07416,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.5313,-0.02836,0.09521]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54561,-0.02903,-0.00206],"force_p95":0.14192,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19041,"mean_force":0.12795,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5328,-0.02857,0.03221]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.5456,-0.02923,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51771,-0.01304,0.23613]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4091.0,"contact_point_centroid":[0.53232,-0.00933,0.03357],"force_p95":0.07789,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12883,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53158,-0.02853,0.03079]},{"body_a":"world","body_b":"grasp_target","contact_count":1620.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53768,-0.02758,0.10692]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4924.0,"contact_point_centroid":[0.53236,-0.04763,0.03263],"force_p95":0.07019,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08555,"mean_force":0.04475,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53158,-0.02853,0.03079]}],"total_contact_groups":8},"final_pose_error":0.08916,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.54696,-0.03014,0.16187],"final_tcp_position":[0.537,-0.02834,0.18796],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.58934,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":452.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1804.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_pregrasp","tcp_end":[0.53791,-0.02648,0.17408],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14828,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":405.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1620.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_grasp","tcp_end":[0.54009,-0.0288,0.04084],"tcp_start":[0.53791,-0.02648,0.17408],"tcp_to_object_dist_end":0.01582,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54548,-0.02847,0.02577],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26054,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13793,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10815.0,"raw_peak_contact_force":0.19041,"tcp_end":[0.53155,-0.02853,0.03075],"tcp_start":[0.54009,-0.0288,0.04084],"tcp_to_object_dist_end":0.0148,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54696,-0.03014,0.16187],"object_pos_start":[0.54548,-0.02847,0.02577],"object_to_goal_dist_end":0.21367,"object_to_goal_dist_start":0.26054,"object_z_max":0.16322,"peak_contact_force":0.24286,"phase_name":"lift_vertical","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26433.0,"raw_peak_contact_force":0.58934,"subtask_id":"lift_object","tcp_end":[0.537,-0.02834,0.18796],"tcp_start":[0.53155,-0.02853,0.03075],"tcp_to_object_dist_end":0.02799,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```