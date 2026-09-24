## Search State

- **Seed**: 8
- **Iteration**: 15 / 15

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

## Current Skill (Q=0.457) — your mutation base

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

- **Composite score**: 0.457
- **task_score** (E): 1.000
- **fitness_score**: 0.977  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1586 |
| descend_to_grasp | 1.00 | 1.00 | 0.1100 |
| grasp | 1.00 | 1.00 | 0.0126 |
| lift | 1.00 | 1.00 | 0.1033 |
| approach_goal | 1.00 | 1.00 | 0.2419 |
| descend_to_place | 1.00 | 1.00 | 0.0164 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.515, -0.001, 0.148) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.515, -0.001, 0.148)→(0.516, -0.001, 0.038) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 9.284 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.516, -0.001, 0.038)→(0.508, -0.001, 0.029) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 43.000 | 0.148 | 0.223 |
| lift | lift | 1.00 / step_budget | (0.508, -0.001, 0.029)→(0.516, -0.001, 0.131) | (0.522, -0.001, 0.026)→(0.534, -0.001, 0.124) | 0.289→0.237 | 1.00 / 27.333 | 0.103 | 0.621 |
| approach_goal | approach | 1.00 / step_budget | (0.516, -0.001, 0.131)→(0.601, 0.196, 0.240) | (0.534, -0.001, 0.124)→(0.610, 0.196, 0.219) | 0.237→0.019 | 1.00 / 20.000 | 0.123 | 0.151 |
| descend_to_place | descend | 1.00 / step_budget | (0.601, 0.196, 0.240)→(0.603, 0.201, 0.225) | (0.610, 0.196, 0.219)→(0.612, 0.200, 0.202) | 0.019→0.010 | 1.00 / 15.667 | 0.127 | 0.256 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.532
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.572
- phase_breakdown.place_goal_score: 0.642
- phase_breakdown.lift_object_score: 0.381
- phase_breakdown.approach_object_score: 0.672
- phase_breakdown.approach_goal_score: 0.672
- phase_breakdown.grasp_object_score: 0.491
- grasp_place_fitness: 0.980

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.980
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.457
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.359


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.08651,"average_solve_count":289.0,"average_success_count":289.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.03145,"approach_object.approach_speed":0.06586,"descend_to_grasp.descend_speed":0.04628,"descend_to_grasp.grasp_offset_z":3e-05,"descend_to_place.descend_place_speed":0.03754,"descend_to_place.place_tolerance":0.04024,"lift.lift_height":0.12592,"lift.lift_speed":0.06808},"optimized_scores":{"best_composite_score":0.46012,"best_fitness_score":0.98012,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.48006,0.04606,-0.00149],"force_p95":0.58264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6636,"mean_force":0.16424,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46935,0.0466,0.02825]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7041.0,"contact_point_centroid":[0.47287,0.06553,0.07907],"force_p95":0.08601,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30824,"mean_force":0.05499,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47207,0.04644,0.07716]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6405.0,"contact_point_centroid":[0.47317,0.02732,0.08011],"force_p95":0.08848,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27059,"mean_force":0.05846,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47214,0.04644,0.0777]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48277,0.04839,-0.00219],"force_p95":0.17566,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26551,"mean_force":0.13702,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4714,0.04684,0.02786]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":624.0,"contact_point_centroid":[0.57983,0.23921,0.25838],"force_p95":0.11611,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23515,"mean_force":0.08486,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57493,0.2206,0.25917]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":646.0,"contact_point_centroid":[0.57913,0.20211,0.25753],"force_p95":0.1169,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22998,"mean_force":0.07891,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57496,0.22066,0.25893]},{"body_a":"world","body_b":"grasp_target","contact_count":1232.0,"contact_point_centroid":[0.4827,0.04873,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49059,0.01997,0.22571]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4989.0,"contact_point_centroid":[0.4701,0.02749,0.0297],"force_p95":0.07193,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12547,"mean_force":0.0431,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47027,0.04673,0.02672]},{"body_a":"world","body_b":"grasp_target","contact_count":1584.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47857,0.04441,0.0909]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11440.0,"contact_point_centroid":[0.52601,0.11125,0.19526],"force_p95":0.11462,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12002,"mean_force":0.0765,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5227,0.1299,0.19464]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12060.0,"contact_point_centroid":[0.52847,0.1518,0.19812],"force_p95":0.10326,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11781,"mean_force":0.07155,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52459,0.13317,0.19723]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5482.0,"contact_point_centroid":[0.47002,0.0661,0.02907],"force_p95":0.07324,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08456,"mean_force":0.04177,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47028,0.04673,0.02673]}],"total_contact_groups":12},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58864,0.22302,0.23331],"final_tcp_position":[0.57615,0.22286,0.251],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":27.60786,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":309.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1232.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48186,0.04161,0.14852],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12271,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":396.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":27.60786,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1584.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.47813,0.04749,0.03471],"tcp_start":[0.48186,0.04161,0.14852],"tcp_to_object_dist_end":0.0099,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4826,0.04691,0.02536],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29161,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16692,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12271.0,"raw_peak_contact_force":0.26551,"subtask_id":"grasp_object","tcp_end":[0.47025,0.04672,0.02669],"tcp_start":[0.47813,0.04749,0.03471],"tcp_to_object_dist_end":0.01243,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":353.0,"n_steps_budget":1000.0,"object_pos_end":[0.4939,0.04672,0.12719],"object_pos_start":[0.4826,0.04691,0.02536],"object_to_goal_dist_end":0.22711,"object_to_goal_dist_start":0.29161,"object_z_max":0.12693,"peak_contact_force":0.09934,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13531.0,"raw_peak_contact_force":0.6636,"subtask_id":"lift_object","tcp_end":[0.47743,0.04651,0.13213],"tcp_start":[0.47025,0.04672,0.02669],"tcp_to_object_dist_end":0.0172,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":860.0,"n_steps_budget":1000.0,"object_pos_end":[0.58622,0.21867,0.24804],"object_pos_start":[0.4939,0.04672,0.12719],"object_to_goal_dist_end":0.02076,"object_to_goal_dist_start":0.22711,"object_z_max":0.24791,"peak_contact_force":0.11489,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23500.0,"raw_peak_contact_force":0.12002,"subtask_id":"approach_goal","tcp_end":[0.57428,0.21879,0.26511],"tcp_start":[0.47743,0.04651,0.13213],"tcp_to_object_dist_end":0.02084,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":54.0,"n_steps_budget":1000.0,"object_pos_end":[0.58864,0.22302,0.23331],"object_pos_start":[0.58622,0.21867,0.24804],"object_to_goal_dist_end":0.00937,"object_to_goal_dist_start":0.02076,"object_z_max":0.24808,"peak_contact_force":0.14398,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1270.0,"raw_peak_contact_force":0.23515,"subtask_id":"place_goal","tcp_end":[0.57615,0.22286,0.251],"tcp_start":[0.57428,0.21879,0.26511],"tcp_to_object_dist_end":0.02166,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25112,"average_solve_count":223.0,"average_success_count":223.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.02514,"approach_object.approach_speed":0.11967,"descend_to_grasp.descend_speed":0.07931,"descend_to_grasp.grasp_offset_z":0.00749,"descend_to_place.descend_place_speed":0.02383,"descend_to_place.place_tolerance":0.01997,"lift.lift_height":0.12246,"lift.lift_speed":0.131},"optimized_scores":{"best_composite_score":0.45566,"best_fitness_score":0.97566,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.53447,-0.0203,-0.00134],"force_p95":0.53253,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57064,"mean_force":0.11045,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52168,-0.02068,0.0329]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4611.0,"contact_point_centroid":[0.52771,-0.00169,0.07698],"force_p95":0.11039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31704,"mean_force":0.07398,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52473,-0.0206,0.07458]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5004.0,"contact_point_centroid":[0.52767,-0.03939,0.075],"force_p95":0.10672,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29118,"mean_force":0.06955,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5246,-0.0206,0.07335]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":328.0,"contact_point_centroid":[0.60985,0.23558,0.23252],"force_p95":0.20074,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24673,"mean_force":0.14179,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60423,0.2175,0.2376]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":415.0,"contact_point_centroid":[0.6094,0.2002,0.23137],"force_p95":0.13773,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24326,"mean_force":0.10271,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60432,0.21789,0.2363]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02114,-0.00206],"force_p95":0.14002,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18211,"mean_force":0.12737,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52391,-0.02073,0.03296]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10493.0,"contact_point_centroid":[0.57011,0.11578,0.18265],"force_p95":0.12564,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1646,"mean_force":0.08408,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56573,0.09733,0.18355]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10954.0,"contact_point_centroid":[0.56825,0.07267,0.17971],"force_p95":0.12486,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1586,"mean_force":0.08158,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56375,0.0911,0.18045]},{"body_a":"world","body_b":"grasp_target","contact_count":1192.0,"contact_point_centroid":[0.53702,-0.02132,-0.00189],"force_p95":0.13623,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5132,-0.0088,0.22511]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4099.0,"contact_point_centroid":[0.52364,-0.0015,0.03428],"force_p95":0.07763,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12437,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52268,-0.0207,0.03156]},{"body_a":"world","body_b":"grasp_target","contact_count":1336.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.5284,-0.01952,0.09351]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4914.0,"contact_point_centroid":[0.52362,-0.0398,0.03336],"force_p95":0.06971,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08331,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52268,-0.0207,0.03157]}],"total_contact_groups":12},"final_pose_error":0.00983,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61221,0.21896,0.19832],"final_tcp_position":[0.60516,0.22087,0.22718],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.57064,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":299.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1192.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52858,-0.01826,0.14784],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":334.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1336.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.5312,-0.02085,0.04139],"tcp_start":[0.52858,-0.01826,0.14784],"tcp_to_object_dist_end":0.01645,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53691,-0.02064,0.02579],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31634,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13644,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10813.0,"raw_peak_contact_force":0.18211,"subtask_id":"grasp_object","tcp_end":[0.52265,-0.0207,0.03153],"tcp_start":[0.5312,-0.02085,0.04139],"tcp_to_object_dist_end":0.01537,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":328.0,"n_steps_budget":600.0,"object_pos_end":[0.54963,-0.02058,0.11807],"object_pos_start":[0.53691,-0.02064,0.02579],"object_to_goal_dist_end":0.2708,"object_to_goal_dist_start":0.31634,"object_z_max":0.11783,"peak_contact_force":0.10283,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9693.0,"raw_peak_contact_force":0.57064,"subtask_id":"lift_object","tcp_end":[0.53134,-0.02056,0.1293],"tcp_start":[0.52265,-0.0207,0.03153],"tcp_to_object_dist_end":0.02146,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":951.0,"n_steps_budget":1000.0,"object_pos_end":[0.60953,0.21541,0.21819],"object_pos_start":[0.54963,-0.02058,0.11807],"object_to_goal_dist_end":0.01641,"object_to_goal_dist_start":0.2708,"object_z_max":0.2181,"peak_contact_force":0.12491,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21447.0,"raw_peak_contact_force":0.1646,"subtask_id":"approach_goal","tcp_end":[0.60409,0.21555,0.24295],"tcp_start":[0.53134,-0.02056,0.1293],"tcp_to_object_dist_end":0.02534,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":58.0,"n_steps_budget":1000.0,"object_pos_end":[0.61221,0.21896,0.19832],"object_pos_start":[0.60953,0.21541,0.21819],"object_to_goal_dist_end":0.01279,"object_to_goal_dist_start":0.01641,"object_z_max":0.2182,"peak_contact_force":0.10715,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":743.0,"raw_peak_contact_force":0.24673,"subtask_id":"place_goal","tcp_end":[0.60516,0.22087,0.22718],"tcp_start":[0.60409,0.21555,0.24295],"tcp_to_object_dist_end":0.02977,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.00955,"average_solve_count":314.0,"average_success_count":314.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.03157,"approach_object.approach_speed":0.05969,"descend_to_grasp.descend_speed":0.03185,"descend_to_grasp.grasp_offset_z":0.0038,"descend_to_place.descend_place_speed":0.08155,"descend_to_place.place_tolerance":0.00517,"lift.lift_height":0.12625,"lift.lift_speed":0.07147},"optimized_scores":{"best_composite_score":0.45665,"best_fitness_score":0.97665,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.54312,-0.02809,-0.00142],"force_p95":0.51436,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62994,"mean_force":0.13042,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52989,-0.0283,0.02858]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5760.0,"contact_point_centroid":[0.53548,-0.00923,0.07665],"force_p95":0.10894,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31062,"mean_force":0.06996,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53294,-0.02818,0.07434]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6301.0,"contact_point_centroid":[0.53539,-0.04701,0.07446],"force_p95":0.10488,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29924,"mean_force":0.06545,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5328,-0.02819,0.07293]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":620.0,"contact_point_centroid":[0.62815,0.17411,0.20061],"force_p95":0.13623,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28723,"mean_force":0.09542,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62515,0.15593,0.20519]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":558.0,"contact_point_centroid":[0.62889,0.13773,0.20088],"force_p95":0.13501,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28143,"mean_force":0.10035,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62515,0.15593,0.20519]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.02899,-0.00208],"force_p95":0.14708,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2203,"mean_force":0.1293,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53213,-0.02838,0.02879]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9327.0,"contact_point_centroid":[0.58497,0.08246,0.17053],"force_p95":0.11971,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16951,"mean_force":0.0811,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58094,0.06394,0.171]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9663.0,"contact_point_centroid":[0.58253,0.04006,0.16817],"force_p95":0.12135,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16685,"mean_force":0.07905,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57836,0.05857,0.16851]},{"body_a":"world","body_b":"grasp_target","contact_count":1320.0,"contact_point_centroid":[0.5456,-0.02923,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51664,-0.01212,0.22463]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4080.0,"contact_point_centroid":[0.53199,-0.00914,0.03006],"force_p95":0.07876,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13253,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53088,-0.02834,0.02735]},{"body_a":"world","body_b":"grasp_target","contact_count":1480.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53614,-0.02682,0.09121]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4945.0,"contact_point_centroid":[0.53193,-0.04746,0.02913],"force_p95":0.0708,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08598,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53088,-0.02834,0.02735]}],"total_contact_groups":12},"final_pose_error":0.00984,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63497,0.1587,0.17384],"final_tcp_position":[0.62639,0.15877,0.19605],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.62994,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":331.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1320.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53595,-0.02516,0.14684],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":370.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1480.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53955,-0.02859,0.03748],"tcp_start":[0.53595,-0.02516,0.14684],"tcp_to_object_dist_end":0.01297,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54547,-0.02828,0.02572],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26044,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14178,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10825.0,"raw_peak_contact_force":0.2203,"subtask_id":"grasp_object","tcp_end":[0.53085,-0.02834,0.02731],"tcp_start":[0.53955,-0.02859,0.03748],"tcp_to_object_dist_end":0.01471,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":388.0,"n_steps_budget":1000.0,"object_pos_end":[0.55819,-0.02819,0.12528],"object_pos_start":[0.54547,-0.02828,0.02572],"object_to_goal_dist_end":0.21338,"object_to_goal_dist_start":0.26044,"object_z_max":0.12505,"peak_contact_force":0.10818,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12147.0,"raw_peak_contact_force":0.62994,"subtask_id":"lift_object","tcp_end":[0.53978,-0.02815,0.13299],"tcp_start":[0.53085,-0.02834,0.02731],"tcp_to_object_dist_end":0.01996,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":772.0,"n_steps_budget":1000.0,"object_pos_end":[0.6331,0.15326,0.19144],"object_pos_start":[0.55819,-0.02819,0.12528],"object_to_goal_dist_end":0.01863,"object_to_goal_dist_start":0.21338,"object_z_max":0.19136,"peak_contact_force":0.13011,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18990.0,"raw_peak_contact_force":0.16951,"subtask_id":"approach_goal","tcp_end":[0.62452,0.15337,0.21293],"tcp_start":[0.53978,-0.02815,0.13299],"tcp_to_object_dist_end":0.02314,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":62.0,"n_steps_budget":1000.0,"object_pos_end":[0.63497,0.1587,0.17384],"object_pos_start":[0.6331,0.15326,0.19144],"object_to_goal_dist_end":0.00727,"object_to_goal_dist_start":0.01863,"object_z_max":0.19145,"peak_contact_force":0.13088,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1178.0,"raw_peak_contact_force":0.28723,"subtask_id":"place_goal","tcp_end":[0.62639,0.15877,0.19605],"tcp_start":[0.62452,0.15337,0.21293],"tcp_to_object_dist_end":0.02382,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```