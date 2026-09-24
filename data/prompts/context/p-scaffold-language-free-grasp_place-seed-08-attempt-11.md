## Search State

- **Seed**: 8
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | pose_tolerance | 8 | 0.2423 | 0.53 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | pose_tolerance | 7 | 0.3971 | 0.73 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | time_limit | time_limit | time_limit | pose_tolerance | pose_tolerance | time_limit | 9 | 0.1162 | 0.43 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.1094 | 0.29 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | pose_tolerance | time_limit | 9 | 0.1146 | 0.43 | ❌ rejected |

**Proposal policy**: task_score is 0.53 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.242) — your mutation base

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
  - 0.12
  weight: 0.2
- id: reach_object
  anchor: object
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: hold_at_goal
  target_entity: object
  weight: 0.4
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.12
    orientation:
      mode: none
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_above_object
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: none
  parameters:
    grasp_offset_z:
      type: scalar
      range:
      - -0.01
      - 0.03
      default: 0.005
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
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
  parameters:
    grasp_duration:
      type: scalar
      range:
      - 0.5
      - 3.0
      default: 1.5
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - -0.005
  subtask_id: reach_object
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.15
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: lift_object
- id: transport_1
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
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.2
      - 1.0
      default: 0.5
      binds_to:
      - path: generator.speed
        mode: replace
    transport_xy_offset_x:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    transport_xy_offset_y:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
  subtask_id: hold_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.12]
  - orientation: mode=none
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings:
    - grasp_offset_z: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=3, strategy=offset_target, offset=[0.005, 0.005, -0.005]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_xy_offset_x: status=consumed; consumers=target.offset.x (add)
    - transport_xy_offset_y: status=consumed; consumers=target.offset.y (add)

## Design Metrics

- **Composite score**: 0.242
- **task_score** (E): 0.526
- **fitness_score**: 0.732  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1192 |
| descend_1 | 1.00 | 1.00 | 0.1535 |
| grasp_1 | 1.00 | 1.00 | 0.0088 |
| lift_1 | 1.00 | 1.00 | 0.1705 |
| transport_1 | 1.00 | 1.00 | 0.2194 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.517, -0.001, 0.191) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / time_limit | (0.517, -0.001, 0.191)→(0.516, -0.001, 0.038) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.025) | 0.289→0.290 | 1.00 / 4.333 | 0.166 | 0.236 |
| grasp_1 | grasp | 1.00 / step_budget | (0.514, -0.001, 0.035)→(0.508, -0.001, 0.029) | (0.522, -0.001, 0.025)→(0.520, -0.001, 0.025) | 0.290→0.291 | 1.00 / 36.000 | 0.406 | 0.568 |
| lift_1 | lift | 1.00 / step_budget | (0.508, -0.001, 0.029)→(0.515, -0.001, 0.199) | (0.520, -0.001, 0.025)→(0.534, -0.001, 0.179) | 0.291→0.224 | 1.00 / 19.000 | 0.101 | 1.892 |
| transport_1 | approach | 1.00 / step_budget | (0.515, -0.001, 0.199)→(0.601, 0.198, 0.196) | (0.534, -0.001, 0.179)→(0.597, 0.153, 0.103) | 0.224→0.123 | 1.00 / 12.667 | 0.149 | 0.808 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.712
- phase_score: 0.609
- phase_breakdown.reach_above_object_score: 0.337
- phase_breakdown.hold_at_goal_score: 0.630
- phase_breakdown.reach_object_score: 0.737
- phase_breakdown.lift_object_score: 0.713
- grasp_place_fitness: 0.829

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.829
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.712
- **Median Q (composite search score)**: 0.321
- **K-run variance**: 0.0154
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.363


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.2549,"average_solve_count":102.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11448,"descend_1.grasp_offset_z":-0.00997,"grasp_1.grasp_duration":1.16189,"lift_1.lift_height":0.23075,"lift_1.lift_speed":0.27749,"transport_1.transport_speed":0.49631,"transport_1.transport_xy_offset_x":-0.0006,"transport_1.transport_xy_offset_y":9e-05},"optimized_scores":{"best_composite_score":0.06684,"best_fitness_score":0.55684,"best_task_score":0.17216},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"left_finger","contact_count":92.0,"contact_point_centroid":[0.47512,0.01203,-0.0011],"force_p95":4.43139,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4.71009,"mean_force":1.69799,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46897,0.04718,0.00708]},{"body_a":"world","body_b":"right_finger","contact_count":49.0,"contact_point_centroid":[0.47144,0.08365,-0.00071],"force_p95":3.76522,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.81854,"mean_force":1.66965,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46913,0.0472,0.00649]},{"body_a":"world","body_b":"grasp_target","contact_count":1415.0,"contact_point_centroid":[0.55023,0.07833,-0.00287],"force_p95":0.40632,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.86625,"mean_force":0.15897,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53273,0.15095,0.22463]},{"body_a":"world","body_b":"left_finger","contact_count":4013.0,"contact_point_centroid":[0.47476,0.00859,-0.00133],"force_p95":0.96869,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1.38157,"mean_force":0.66997,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46987,0.04731,0.00609]},{"body_a":"world","body_b":"right_finger","contact_count":2485.0,"contact_point_centroid":[0.47145,0.08668,-0.00083],"force_p95":0.58593,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.59908,"mean_force":0.46783,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46976,0.04729,0.00599]},{"body_a":"world","body_b":"grasp_target","contact_count":246.0,"contact_point_centroid":[0.47538,0.04814,-0.00267],"force_p95":0.2826,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57738,"mean_force":0.14652,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46775,0.04706,0.01586]},{"body_a":"grasp_target","body_b":"hand","contact_count":160.0,"contact_point_centroid":[0.49234,0.05943,0.07017],"force_p95":0.42024,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.53859,"mean_force":0.10205,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46726,0.04708,0.0363]},{"body_a":"grasp_target","body_b":"hand","contact_count":600.0,"contact_point_centroid":[0.49585,0.04927,0.04648],"force_p95":0.4711,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.47265,"mean_force":0.44861,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47049,0.04738,0.0067]},{"body_a":"grasp_target","body_b":"hand","contact_count":126.0,"contact_point_centroid":[0.50279,0.04683,0.0529],"force_p95":0.25033,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.46202,"mean_force":0.16637,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47746,0.04807,0.01835]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8563.0,"contact_point_centroid":[0.47241,0.02884,0.11757],"force_p95":0.10573,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34895,"mean_force":0.05933,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46909,0.04749,0.11661]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7131.0,"contact_point_centroid":[0.47006,0.06665,0.11265],"force_p95":0.12073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34458,"mean_force":0.06932,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46891,0.04745,0.11024]},{"body_a":"world","body_b":"grasp_target","contact_count":3968.0,"contact_point_centroid":[0.48268,0.04873,-0.00205],"force_p95":0.16177,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27859,"mean_force":0.12752,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47695,0.04712,0.06649]},{"body_a":"world","body_b":"grasp_target","contact_count":2400.0,"contact_point_centroid":[0.47958,0.04858,-0.00362],"force_p95":0.26552,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26756,"mean_force":0.23067,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47049,0.04738,0.0067]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":151.0,"contact_point_centroid":[0.48253,0.0345,0.22932],"force_p95":0.17515,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2496,"mean_force":0.0539,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.47451,0.04944,0.2319]},{"body_a":"world","body_b":"grasp_target","contact_count":2952.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12843,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48862,0.0229,0.22167]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1338.0,"contact_point_centroid":[0.53837,0.15899,0.22651],"force_p95":0.01193,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01565,"mean_force":0.01054,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53753,0.15898,0.22439]}],"total_contact_groups":16},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.55037,0.07834,0.01602],"final_tcp_position":[0.57053,0.21411,0.22282],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":4.71009,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":739.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2952.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.47957,0.0459,0.14707],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12113,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":992.0,"n_steps_budget":1000.0,"object_pos_end":[0.48314,0.04872,0.02421],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29111,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.25298,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4094.0,"raw_peak_contact_force":0.46202,"subtask_id":"reach_object","tcp_end":[0.47745,0.04816,0.0136],"tcp_start":[0.47957,0.0459,0.14707],"tcp_to_object_dist_end":0.01206,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":200.0,"n_steps_budget":50.0,"object_pos_end":[0.47747,0.04857,0.02262],"object_pos_start":[0.48314,0.04872,0.02421],"object_to_goal_dist_end":0.2943,"object_to_goal_dist_start":0.29111,"object_z_max":0.02421,"peak_contact_force":0.94444,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9498.0,"raw_peak_contact_force":1.38157,"subtask_id":"reach_object","tcp_end":[0.4695,0.04726,0.0058],"tcp_start":[0.46951,0.04726,0.0058],"tcp_to_object_dist_end":0.01866,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":12.0,"n_steps":533.0,"n_steps_budget":600.0,"object_pos_end":[0.4987,0.0489,0.21744],"object_pos_start":[0.47623,0.04856,0.02271],"object_to_goal_dist_end":0.19867,"object_to_goal_dist_start":0.29468,"object_z_max":0.21736,"peak_contact_force":0.07805,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16241.0,"raw_peak_contact_force":4.71009,"subtask_id":"lift_object","tcp_end":[0.47326,0.04819,0.2316],"tcp_start":[0.4695,0.04726,0.0058],"tcp_to_object_dist_end":0.02913,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":456.0,"n_steps_budget":1000.0,"object_pos_end":[0.55037,0.07834,0.01602],"object_pos_start":[0.4987,0.0489,0.21744],"object_to_goal_dist_end":0.2639,"object_to_goal_dist_start":0.19867,"object_z_max":0.21744,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2904.0,"raw_peak_contact_force":1.86625,"subtask_id":"hold_at_goal","tcp_end":[0.57053,0.21411,0.22282],"tcp_start":[0.47326,0.04819,0.2316],"tcp_to_object_dist_end":0.24821,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.45745,"average_solve_count":94.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17563,"descend_1.grasp_offset_z":0.02387,"grasp_1.grasp_duration":1.12636,"lift_1.lift_height":0.15716,"lift_1.lift_speed":0.35568,"transport_1.transport_speed":0.70969,"transport_1.transport_xy_offset_x":0.00669,"transport_1.transport_xy_offset_y":0.03482},"optimized_scores":{"best_composite_score":0.33884,"best_fitness_score":0.82884,"best_task_score":0.7123},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.5352,-0.02142,-0.00128],"force_p95":0.48379,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53945,"mean_force":0.10796,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52216,-0.02108,0.03795]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6605.0,"contact_point_centroid":[0.52824,-0.00247,0.09232],"force_p95":0.10377,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31389,"mean_force":0.06468,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52503,-0.02119,0.09085]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5617.0,"contact_point_centroid":[0.52771,-0.04026,0.09478],"force_p95":0.10936,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30066,"mean_force":0.07319,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52516,-0.02119,0.09232]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7634.0,"contact_point_centroid":[0.5752,0.13001,0.17731],"force_p95":0.12085,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2948,"mean_force":0.08201,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56932,0.11175,0.17761]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6549.0,"contact_point_centroid":[0.57584,0.09696,0.17867],"force_p95":0.13754,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29108,"mean_force":0.09281,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57052,0.11582,0.17815]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02142,-0.00203],"force_p95":0.13311,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14766,"mean_force":0.12546,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52453,-0.02111,0.03805]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.53702,-0.02132,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51664,-0.01135,0.2443]},{"body_a":"world","body_b":"grasp_target","contact_count":3964.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53048,-0.02078,0.10954]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5333.0,"contact_point_centroid":[0.52401,-0.00199,0.0386],"force_p95":0.06863,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09959,"mean_force":0.04125,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52325,-0.02109,0.03658]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4264.0,"contact_point_centroid":[0.52263,-0.04034,0.03956],"force_p95":0.08018,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08849,"mean_force":0.05045,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52326,-0.02109,0.03658]}],"total_contact_groups":10},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61471,0.24874,0.16126],"final_tcp_position":[0.60999,0.24784,0.19595],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.53945,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.53165,-0.0202,0.20405],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17811,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":991.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3964.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53174,-0.02122,0.04646],"tcp_start":[0.53165,-0.0202,0.20405],"tcp_to_object_dist_end":0.02112,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5369,-0.02147,0.02587],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31695,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13458,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11397.0,"raw_peak_contact_force":0.14766,"subtask_id":"reach_object","tcp_end":[0.52322,-0.02109,0.03655],"tcp_start":[0.53174,-0.02122,0.04646],"tcp_to_object_dist_end":0.01735,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":399.0,"n_steps_budget":600.0,"object_pos_end":[0.54866,-0.022,0.14544],"object_pos_start":[0.5369,-0.02147,0.02587],"object_to_goal_dist_end":0.26462,"object_to_goal_dist_start":0.31695,"object_z_max":0.1452,"peak_contact_force":0.10604,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12301.0,"raw_peak_contact_force":0.53945,"subtask_id":"lift_object","tcp_end":[0.53206,-0.02139,0.16381],"tcp_start":[0.52322,-0.02109,0.03655],"tcp_to_object_dist_end":0.02476,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":635.0,"n_steps_budget":1000.0,"object_pos_end":[0.61471,0.24874,0.16126],"object_pos_start":[0.54866,-0.022,0.14544],"object_to_goal_dist_end":0.05089,"object_to_goal_dist_start":0.26462,"object_z_max":0.16125,"peak_contact_force":0.13836,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14183.0,"raw_peak_contact_force":0.2948,"subtask_id":"hold_at_goal","tcp_end":[0.60999,0.24784,0.19595],"tcp_start":[0.53206,-0.02139,0.16381],"tcp_to_object_dist_end":0.03502,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.06542,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19602,"descend_1.grasp_offset_z":0.00594,"grasp_1.grasp_duration":0.70426,"lift_1.lift_height":0.19454,"lift_1.lift_speed":0.11492,"transport_1.transport_speed":0.454,"transport_1.transport_xy_offset_x":0.00078,"transport_1.transport_xy_offset_y":-0.01738},"optimized_scores":{"best_composite_score":0.32116,"best_fitness_score":0.81116,"best_task_score":0.69252},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.54375,-0.02895,-0.00133],"force_p95":0.3864,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42646,"mean_force":0.08784,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53012,-0.02863,0.04483]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6971.0,"contact_point_centroid":[0.53623,-0.04783,0.11223],"force_p95":0.11974,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28374,"mean_force":0.07804,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53321,-0.02876,0.1097]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8591.0,"contact_point_centroid":[0.53708,-0.01018,0.11196],"force_p95":0.10568,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28241,"mean_force":0.06664,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53327,-0.02876,0.11059]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3955.0,"contact_point_centroid":[0.58447,0.02893,0.18305],"force_p95":0.15487,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26238,"mean_force":0.10938,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57898,0.04768,0.18433]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4570.0,"contact_point_centroid":[0.58337,0.0619,0.18322],"force_p95":0.13621,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22511,"mean_force":0.08782,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57723,0.04422,0.18495]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54561,-0.02931,-0.00205],"force_p95":0.13828,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17523,"mean_force":0.12689,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53249,-0.02869,0.04493]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.5456,-0.02923,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52019,-0.0148,0.25706]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53867,-0.02839,0.12248]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5319.0,"contact_point_centroid":[0.53225,-0.00961,0.04554],"force_p95":0.07098,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10369,"mean_force":0.04105,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53123,-0.02866,0.04342]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4156.0,"contact_point_centroid":[0.53186,-0.04794,0.04626],"force_p95":0.08243,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08946,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53123,-0.02866,0.04342]}],"total_contact_groups":10},"final_pose_error":0.01973,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.62577,0.13339,0.13228],"final_tcp_position":[0.62269,0.13244,0.17046],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.42646,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.54012,-0.02778,0.22304],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1971,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53967,-0.02888,0.05359],"tcp_start":[0.54012,-0.02778,0.22304],"tcp_to_object_dist_end":0.0282,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54552,-0.02916,0.02579],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26103,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13806,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11275.0,"raw_peak_contact_force":0.17523,"subtask_id":"reach_object","tcp_end":[0.5312,-0.02866,0.04338],"tcp_start":[0.53967,-0.02888,0.05359],"tcp_to_object_dist_end":0.02269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":538.0,"n_steps_budget":960.0,"object_pos_end":[0.55522,-0.03008,0.17504],"object_pos_start":[0.54552,-0.02916,0.02579],"object_to_goal_dist_end":0.2099,"object_to_goal_dist_start":0.26103,"object_z_max":0.17481,"peak_contact_force":0.11897,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15646.0,"raw_peak_contact_force":0.42646,"subtask_id":"lift_object","tcp_end":[0.5411,-0.02904,0.20108],"tcp_start":[0.5312,-0.02866,0.04338],"tcp_to_object_dist_end":0.02964,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":428.0,"n_steps_budget":1000.0,"object_pos_end":[0.62577,0.13339,0.13228],"object_pos_start":[0.55522,-0.03008,0.17504],"object_to_goal_dist_end":0.05511,"object_to_goal_dist_start":0.2099,"object_z_max":0.17524,"peak_contact_force":0.18701,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8525.0,"raw_peak_contact_force":0.26238,"subtask_id":"hold_at_goal","tcp_end":[0.62269,0.13244,0.17046],"tcp_start":[0.5411,-0.02904,0.20108],"tcp_to_object_dist_end":0.03831,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```