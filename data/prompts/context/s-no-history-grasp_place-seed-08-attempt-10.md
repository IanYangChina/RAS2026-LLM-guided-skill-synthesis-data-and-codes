## Search State

- **Seed**: 8
- **Iteration**: 11 / 15

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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

## Current Skill (Q=0.322) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: grasp_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.2
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: approach_goal
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.2
- id: place_goal
  target_entity: object
  weight: 0.2
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
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
    - 0.03
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.005
      - 0.1
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_offset_z:
      type: scalar
      range:
      - 0.0
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: grasp_object
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
    orientation:
      mode: keep_current
  subtask_id: grasp_object
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
    - 0.15
    tolerance: 0.02
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
      - path: target.offset.z
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_goal_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_goal
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
    - 0.015
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_place_speed:
      type: scalar
      range:
      - 0.005
      - 0.1
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    place_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: place_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_offset_z: status=consumed; consumers=target.offset.z (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.015], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_place_speed: status=consumed; consumers=generator.speed (replace)
    - place_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: 0.322
- **task_score** (E): 1.000
- **fitness_score**: 0.892  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1287 |
| descend_to_grasp | 1.00 | 1.00 | 0.1355 |
| grasp | 1.00 | 1.00 | 0.0128 |
| lift | 1.00 | 1.00 | 0.1068 |
| approach_goal | 1.00 | 1.00 | 0.2110 |
| descend_to_place | 1.00 | 1.00 | 0.0387 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.515, -0.000, 0.177) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 5.921 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.515, -0.000, 0.177)→(0.516, -0.001, 0.042) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.516, -0.001, 0.042)→(0.508, -0.001, 0.032) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.025) | 0.289→0.290 | 1.00 / 42.333 | 0.163 | 0.247 |
| lift | lift | 1.00 / step_budget | (0.508, -0.001, 0.032)→(0.516, -0.001, 0.139) | (0.522, -0.001, 0.025)→(0.529, -0.001, 0.128) | 0.290→0.240 | 1.00 / 33.333 | 0.091 | 0.500 |
| approach_goal | approach | 1.00 / step_budget | (0.516, -0.001, 0.139)→(0.592, 0.171, 0.227) | (0.529, -0.001, 0.128)→(0.604, 0.171, 0.214) | 0.240→0.038 | 1.00 / 30.000 | 0.096 | 0.116 |
| descend_to_place | descend | 1.00 / step_budget | (0.592, 0.171, 0.227)→(0.604, 0.204, 0.212) | (0.604, 0.171, 0.214)→(0.612, 0.204, 0.193) | 0.038→0.013 | 1.00 / 29.000 | 0.107 | 0.264 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.542
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.503
- phase_breakdown.place_goal_score: 0.834
- phase_breakdown.lift_object_score: 0.396
- phase_breakdown.approach_object_score: 0.371
- phase_breakdown.approach_goal_score: 0.370
- phase_breakdown.grasp_object_score: 0.545
- grasp_place_fitness: 0.978

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.978
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.406
- **K-run variance**: 0.0145
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.451


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.79348,"average_solve_count":460.0,"average_success_count":460.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.0128,"approach_object.approach_speed":0.01098,"descend_to_grasp.descend_speed":0.02933,"descend_to_grasp.grasp_offset_z":4e-05,"descend_to_grasp.grasp_tolerance":0.04372,"descend_to_place.descend_place_speed":0.05772,"descend_to_place.place_tolerance":0.04041,"lift.lift_height":0.1282,"lift.lift_speed":0.02593},"optimized_scores":{"best_composite_score":0.40836,"best_fitness_score":0.97836,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":111.0,"contact_point_centroid":[0.47927,0.04537,-0.00178],"force_p95":0.4404,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51167,"mean_force":0.19546,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47005,0.04552,0.0332]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48282,0.04833,-0.00228],"force_p95":0.20109,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28038,"mean_force":0.14343,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4722,0.04575,0.03325]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7456.0,"contact_point_centroid":[0.47281,0.06468,0.08312],"force_p95":0.08336,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2639,"mean_force":0.05322,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47263,0.04551,0.08132]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5555.0,"contact_point_centroid":[0.57238,0.2333,0.24233],"force_p95":0.0802,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22126,"mean_force":0.05847,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57143,0.21408,0.23995]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7456.0,"contact_point_centroid":[0.47284,0.02635,0.08328],"force_p95":0.07987,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21913,"mean_force":0.05175,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47263,0.04551,0.08132]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4582.0,"contact_point_centroid":[0.47139,0.0264,0.03475],"force_p95":0.07897,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15252,"mean_force":0.04676,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47108,0.04564,0.03213]},{"body_a":"world","body_b":"grasp_target","contact_count":556.0,"contact_point_centroid":[0.4827,0.04873,-0.00177],"force_p95":0.13792,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1235,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49469,0.01369,0.24873]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6470.0,"contact_point_centroid":[0.57234,0.19505,0.24204],"force_p95":0.07444,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13241,"mean_force":0.04958,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57137,0.21398,0.23997]},{"body_a":"world","body_b":"grasp_target","contact_count":1376.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.48192,0.03985,0.10707]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5112.0,"contact_point_centroid":[0.51799,0.0982,0.18882],"force_p95":0.07456,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08995,"mean_force":0.04921,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51789,0.11734,0.1868]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5433.0,"contact_point_centroid":[0.47086,0.06509,0.03374],"force_p95":0.07702,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08335,"mean_force":0.0427,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4711,0.04564,0.03214]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4942.0,"contact_point_centroid":[0.51673,0.13425,0.18692],"force_p95":0.07425,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08296,"mean_force":0.05028,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51661,0.1151,0.18508]}],"total_contact_groups":12},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58647,0.22509,0.22352],"final_tcp_position":[0.57742,0.22506,0.23739],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":17.51721,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":140.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":17.51721,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":556.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48761,0.03353,0.17693],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15175,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":344.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1376.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.47906,0.04636,0.04039],"tcp_start":[0.48761,0.03353,0.17693],"tcp_to_object_dist_end":0.01501,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48265,0.04616,0.02504],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29228,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.18746,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11815.0,"raw_peak_contact_force":0.28038,"subtask_id":"grasp_object","tcp_end":[0.47106,0.04563,0.0321],"tcp_start":[0.47906,0.04636,0.04039],"tcp_to_object_dist_end":0.01358,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":372.0,"n_steps_budget":1000.0,"object_pos_end":[0.48717,0.04599,0.12523],"object_pos_start":[0.48265,0.04616,0.02504],"object_to_goal_dist_end":0.23127,"object_to_goal_dist_start":0.29228,"object_z_max":0.12497,"peak_contact_force":0.07935,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15023.0,"raw_peak_contact_force":0.51167,"subtask_id":"lift_object","tcp_end":[0.47758,0.04573,0.13412],"tcp_start":[0.47106,0.04563,0.0321],"tcp_to_object_dist_end":0.01307,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":250.0,"n_steps_budget":1000.0,"object_pos_end":[0.57377,0.19654,0.23667],"object_pos_start":[0.48717,0.04599,0.12523],"object_to_goal_dist_end":0.03388,"object_to_goal_dist_start":0.23127,"object_z_max":0.23618,"peak_contact_force":0.07943,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10054.0,"raw_peak_contact_force":0.08995,"subtask_id":"approach_goal","tcp_end":[0.56338,0.19642,0.24769],"tcp_start":[0.47758,0.04573,0.13412],"tcp_to_object_dist_end":0.01515,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":325.0,"n_steps_budget":1000.0,"object_pos_end":[0.58647,0.22509,0.22352],"object_pos_start":[0.57377,0.19654,0.23667],"object_to_goal_dist_end":0.00916,"object_to_goal_dist_start":0.03388,"object_z_max":0.23777,"peak_contact_force":0.08166,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12025.0,"raw_peak_contact_force":0.22126,"subtask_id":"place_goal","tcp_end":[0.57742,0.22506,0.23739],"tcp_start":[0.56338,0.19642,0.24769],"tcp_to_object_dist_end":0.01656,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.03183,"average_solve_count":377.0,"average_success_count":377.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.06658,"approach_object.approach_speed":0.02425,"descend_to_grasp.descend_speed":0.0979,"descend_to_grasp.grasp_offset_z":0.00032,"descend_to_grasp.grasp_tolerance":0.03413,"descend_to_place.descend_place_speed":0.02862,"descend_to_place.place_tolerance":0.0348,"lift.lift_height":0.18832,"lift.lift_speed":0.035},"optimized_scores":{"best_composite_score":0.40586,"best_fitness_score":0.97586,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":97.0,"contact_point_centroid":[0.53297,-0.01996,-0.00153],"force_p95":0.49553,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51822,"mean_force":0.19705,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52114,-0.02023,0.03042]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11218.0,"contact_point_centroid":[0.52612,-0.00104,0.11429],"force_p95":0.0824,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26444,"mean_force":0.05713,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52535,-0.02016,0.11178]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12107.0,"contact_point_centroid":[0.52581,-0.03921,0.11067],"force_p95":0.07869,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25942,"mean_force":0.05399,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52509,-0.02016,0.10861]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53706,-0.02107,-0.0021],"force_p95":0.15151,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2235,"mean_force":0.13036,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52343,-0.02027,0.03093]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6369.0,"contact_point_centroid":[0.60413,0.22682,0.22232],"force_p95":0.08558,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22157,"mean_force":0.06095,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60137,0.20797,0.22202]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5619.0,"contact_point_centroid":[0.60434,0.18899,0.2236],"force_p95":0.08946,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15338,"mean_force":0.06617,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60137,0.20795,0.22204]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4077.0,"contact_point_centroid":[0.52335,-0.00104,0.03226],"force_p95":0.07938,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13858,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5222,-0.02025,0.02955]},{"body_a":"world","body_b":"grasp_target","contact_count":560.0,"contact_point_centroid":[0.53702,-0.02132,-0.00177],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1235,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51011,-0.00593,0.2489]},{"body_a":"world","body_b":"grasp_target","contact_count":1240.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52662,-0.01751,0.10589]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4606.0,"contact_point_centroid":[0.56281,0.05447,0.21452],"force_p95":0.08286,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10246,"mean_force":0.05521,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5613,0.07343,0.21324]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3937.0,"contact_point_centroid":[0.56313,0.09281,0.21531],"force_p95":0.08947,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10222,"mean_force":0.06031,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5614,0.07375,0.21331]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4964.0,"contact_point_centroid":[0.52328,-0.03937,0.03134],"force_p95":0.07154,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08655,"mean_force":0.04471,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52221,-0.02025,0.02956]}],"total_contact_groups":12},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61548,0.22282,0.19874],"final_tcp_position":[0.60596,0.22313,0.21469],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.51822,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":141.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":560.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52491,-0.01458,0.17725],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":310.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1240.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.53091,-0.02037,0.03961],"tcp_start":[0.52491,-0.01458,0.17725],"tcp_to_object_dist_end":0.01494,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53691,-0.02024,0.02567],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3161,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14548,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10841.0,"raw_peak_contact_force":0.2235,"subtask_id":"grasp_object","tcp_end":[0.52218,-0.02024,0.02952],"tcp_start":[0.53091,-0.02037,0.03961],"tcp_to_object_dist_end":0.01523,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":623.0,"n_steps_budget":1000.0,"object_pos_end":[0.5439,-0.02018,0.18514],"object_pos_start":[0.53691,-0.02024,0.02567],"object_to_goal_dist_end":0.25763,"object_to_goal_dist_start":0.3161,"object_z_max":0.18489,"peak_contact_force":0.08197,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23422.0,"raw_peak_contact_force":0.51822,"subtask_id":"lift_object","tcp_end":[0.53241,-0.02017,0.19469],"tcp_start":[0.52218,-0.02024,0.02952],"tcp_to_object_dist_end":0.01494,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":244.0,"n_steps_budget":1000.0,"object_pos_end":[0.60908,0.18388,0.2268],"object_pos_start":[0.5439,-0.02018,0.18514],"object_to_goal_dist_end":0.04799,"object_to_goal_dist_start":0.25763,"object_z_max":0.22661,"peak_contact_force":0.09217,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8543.0,"raw_peak_contact_force":0.10246,"subtask_id":"approach_goal","tcp_end":[0.5963,0.18393,0.23877],"tcp_start":[0.53241,-0.02017,0.19469],"tcp_to_object_dist_end":0.01751,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":388.0,"n_steps_budget":1000.0,"object_pos_end":[0.61548,0.22282,0.19874],"object_pos_start":[0.60908,0.18388,0.2268],"object_to_goal_dist_end":0.01123,"object_to_goal_dist_start":0.04799,"object_z_max":0.22695,"peak_contact_force":0.08473,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11988.0,"raw_peak_contact_force":0.22157,"subtask_id":"place_goal","tcp_end":[0.60596,0.22313,0.21469],"tcp_start":[0.5963,0.18393,0.23877],"tcp_to_object_dist_end":0.01858,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29032,"average_solve_count":248.0,"average_success_count":248.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.02509,"approach_object.approach_speed":0.06921,"descend_to_grasp.descend_speed":0.09541,"descend_to_grasp.grasp_offset_z":0.00598,"descend_to_grasp.grasp_tolerance":0.02535,"descend_to_place.descend_place_speed":0.03484,"descend_to_place.place_tolerance":0.02717,"lift.lift_height":0.08001,"lift.lift_speed":0.11141},"optimized_scores":{"best_composite_score":0.15181,"best_fitness_score":0.72181,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.54425,-0.02714,-0.00145],"force_p95":0.3577,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46875,"mean_force":0.08583,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52952,-0.0276,0.03644]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7342.0,"contact_point_centroid":[0.62904,0.1714,0.18523],"force_p95":0.119,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35023,"mean_force":0.08509,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6235,0.15287,0.18485]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2763.0,"contact_point_centroid":[0.53542,-0.00866,0.05987],"force_p95":0.11266,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28393,"mean_force":0.07515,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53243,-0.02759,0.05727]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3020.0,"contact_point_centroid":[0.53555,-0.04641,0.05881],"force_p95":0.10829,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27367,"mean_force":0.07135,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53241,-0.02759,0.05707]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54567,-0.02898,-0.00215],"force_p95":0.16428,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23633,"mean_force":0.13357,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53154,-0.02768,0.03644]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7830.0,"contact_point_centroid":[0.6286,0.13421,0.18543],"force_p95":0.10787,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22798,"mean_force":0.07923,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62343,0.15268,0.18498]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3349.0,"contact_point_centroid":[0.5779,0.02794,0.13635],"force_p95":0.11031,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15432,"mean_force":0.07804,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57328,0.04646,0.13543]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4071.0,"contact_point_centroid":[0.53162,-0.00843,0.03771],"force_p95":0.08132,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15325,"mean_force":0.05191,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53031,-0.02764,0.03501]},{"body_a":"world","body_b":"grasp_target","contact_count":508.0,"contact_point_centroid":[0.5456,-0.02923,-0.00175],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12359,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51462,-0.00904,0.24372]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2697.0,"contact_point_centroid":[0.5779,0.06424,0.13697],"force_p95":0.11549,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1372,"mean_force":0.08962,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57286,0.04559,0.13485]},{"body_a":"world","body_b":"grasp_target","contact_count":1180.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53382,-0.02405,0.10831]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5015.0,"contact_point_centroid":[0.53153,-0.0468,0.03677],"force_p95":0.07392,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08112,"mean_force":0.0445,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53032,-0.02764,0.03502]}],"total_contact_groups":12},"final_pose_error":0.01025,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63435,0.16282,0.1582],"final_tcp_position":[0.62843,0.16272,0.18294],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.46875,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":128.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12259,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":508.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.5313,-0.02016,0.17629],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15121,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":295.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1180.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.53905,-0.02786,0.04542],"tcp_start":[0.5313,-0.02016,0.17629],"tcp_to_object_dist_end":0.02053,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54553,-0.02783,0.02551],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.2602,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.15643,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10886.0,"raw_peak_contact_force":0.23633,"subtask_id":"grasp_object","tcp_end":[0.53029,-0.02764,0.03498],"tcp_start":[0.53905,-0.02786,0.04542],"tcp_to_object_dist_end":0.01795,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":197.0,"n_steps_budget":600.0,"object_pos_end":[0.55632,-0.02769,0.07467],"object_pos_start":[0.54553,-0.02783,0.02551],"object_to_goal_dist_end":0.23111,"object_to_goal_dist_start":0.2602,"object_z_max":0.07444,"peak_contact_force":0.11139,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5875.0,"raw_peak_contact_force":0.46875,"subtask_id":"lift_object","tcp_end":[0.53834,-0.02765,0.08711],"tcp_start":[0.53029,-0.02764,0.03498],"tcp_to_object_dist_end":0.02186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":254.0,"n_steps_budget":1000.0,"object_pos_end":[0.6301,0.13184,0.17735],"object_pos_start":[0.55632,-0.02769,0.07467],"object_to_goal_dist_end":0.0332,"object_to_goal_dist_start":0.23111,"object_z_max":0.1769,"peak_contact_force":0.11593,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6046.0,"raw_peak_contact_force":0.15432,"subtask_id":"approach_goal","tcp_end":[0.61563,0.13178,0.19497],"tcp_start":[0.53834,-0.02765,0.08711],"tcp_to_object_dist_end":0.0228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":672.0,"n_steps_budget":1000.0,"object_pos_end":[0.63435,0.16282,0.1582],"object_pos_start":[0.6301,0.13184,0.17735],"object_to_goal_dist_end":0.0189,"object_to_goal_dist_start":0.0332,"object_z_max":0.17835,"peak_contact_force":0.15489,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":15172.0,"raw_peak_contact_force":0.35023,"subtask_id":"place_goal","tcp_end":[0.62843,0.16272,0.18294],"tcp_start":[0.61563,0.13178,0.19497],"tcp_to_object_dist_end":0.02544,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```