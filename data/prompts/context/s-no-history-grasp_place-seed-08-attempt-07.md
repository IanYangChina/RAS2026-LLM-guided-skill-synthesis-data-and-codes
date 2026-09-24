## Search State

- **Seed**: 8
- **Iteration**: 8 / 15

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

## Current Skill (Q=0.458) — your mutation base

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

- **Composite score**: 0.458
- **task_score** (E): 1.000
- **fitness_score**: 0.978  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1587 |
| descend_to_grasp | 1.00 | 1.00 | 0.1125 |
| grasp | 1.00 | 1.00 | 0.0126 |
| lift | 1.00 | 1.00 | 0.1437 |
| approach_goal | 1.00 | 1.00 | 0.2285 |
| descend_to_place | 1.00 | 1.00 | 0.0188 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.148) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.516, -0.001, 0.148)→(0.516, -0.001, 0.035) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 27.129 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.516, -0.001, 0.035)→(0.508, -0.001, 0.026) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 43.000 | 0.148 | 0.224 |
| lift | lift | 1.00 / step_budget | (0.508, -0.001, 0.026)→(0.517, -0.001, 0.169) | (0.522, -0.001, 0.026)→(0.529, -0.001, 0.164) | 0.289→0.231 | 1.00 / 38.000 | 0.080 | 0.558 |
| approach_goal | approach | 1.00 / step_budget | (0.517, -0.001, 0.169)→(0.600, 0.195, 0.242) | (0.529, -0.001, 0.164)→(0.611, 0.195, 0.228) | 0.231→0.027 | 1.00 / 34.000 | 0.089 | 0.133 |
| descend_to_place | descend | 1.00 / step_budget | (0.600, 0.195, 0.242)→(0.602, 0.201, 0.224) | (0.611, 0.195, 0.228)→(0.614, 0.201, 0.210) | 0.027→0.011 | 1.00 / 28.667 | 0.099 | 0.187 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.399
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.594
- phase_breakdown.place_goal_score: 0.644
- phase_breakdown.lift_object_score: 0.491
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
- **Final σ (mean)**: 0.409


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.91,"average_solve_count":300.0,"average_success_count":300.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.06218,"approach_object.approach_speed":0.11339,"descend_to_grasp.descend_speed":0.05701,"descend_to_grasp.grasp_offset_z":3e-05,"descend_to_place.descend_place_speed":0.06765,"descend_to_place.place_tolerance":0.03794,"lift.lift_height":0.1388,"lift.lift_speed":0.01339},"optimized_scores":{"best_composite_score":0.4603,"best_fitness_score":0.9803,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":113.0,"contact_point_centroid":[0.47937,0.04642,-0.00168],"force_p95":0.45159,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53133,"mean_force":0.21631,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46932,0.04662,0.0276]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48277,0.0484,-0.00219],"force_p95":0.17548,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26523,"mean_force":0.13696,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47152,0.04686,0.02783]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8654.0,"contact_point_centroid":[0.47241,0.06562,0.08557],"force_p95":0.07942,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25002,"mean_force":0.05237,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47224,0.04646,0.08376]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8665.0,"contact_point_centroid":[0.47242,0.02731,0.0857],"force_p95":0.07643,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21293,"mean_force":0.05122,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47223,0.04646,0.08374]},{"body_a":"world","body_b":"grasp_target","contact_count":1180.0,"contact_point_centroid":[0.4827,0.04873,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49074,0.02005,0.22553]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1002.0,"contact_point_centroid":[0.5762,0.23952,0.25967],"force_p95":0.08315,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13242,"mean_force":0.05738,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57474,0.22035,0.25926]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4991.0,"contact_point_centroid":[0.47018,0.02751,0.02958],"force_p95":0.07138,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12694,"mean_force":0.04309,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47039,0.04674,0.0267]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":923.0,"contact_point_centroid":[0.57604,0.20135,0.26096],"force_p95":0.08518,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12381,"mean_force":0.05929,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57476,0.22038,0.25913]},{"body_a":"world","body_b":"grasp_target","contact_count":1576.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47871,0.04444,0.09074]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16665.0,"contact_point_centroid":[0.52687,0.11745,0.20791],"force_p95":0.0715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09781,"mean_force":0.04803,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5267,0.13655,0.20626]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5488.0,"contact_point_centroid":[0.47009,0.06612,0.02896],"force_p95":0.07309,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08432,"mean_force":0.04171,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4704,0.04675,0.02671]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15775.0,"contact_point_centroid":[0.52797,0.15768,0.20912],"force_p95":0.07369,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08422,"mean_force":0.05072,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52782,0.13851,0.20766]}],"total_contact_groups":12},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58703,0.22267,0.2394],"final_tcp_position":[0.57606,0.22276,0.25081],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":296.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1180.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48204,0.04163,0.14852],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1227,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":394.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1576.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.47824,0.04751,0.03469],"tcp_start":[0.48204,0.04163,0.14852],"tcp_to_object_dist_end":0.00982,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4826,0.04692,0.02536],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.2916,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16683,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12279.0,"raw_peak_contact_force":0.26523,"subtask_id":"grasp_object","tcp_end":[0.47036,0.04674,0.02667],"tcp_start":[0.47824,0.04751,0.03469],"tcp_to_object_dist_end":0.01231,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":431.0,"n_steps_budget":1000.0,"object_pos_end":[0.48838,0.04662,0.14101],"object_pos_start":[0.4826,0.04692,0.02536],"object_to_goal_dist_end":0.2235,"object_to_goal_dist_start":0.2916,"object_z_max":0.14074,"peak_contact_force":0.07705,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17432.0,"raw_peak_contact_force":0.53133,"subtask_id":"lift_object","tcp_end":[0.47768,0.04654,0.14486],"tcp_start":[0.47036,0.04674,0.02667],"tcp_to_object_dist_end":0.01138,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":799.0,"n_steps_budget":1000.0,"object_pos_end":[0.58427,0.21846,0.25455],"object_pos_start":[0.48838,0.04662,0.14101],"object_to_goal_dist_end":0.02632,"object_to_goal_dist_start":0.2235,"object_z_max":0.25443,"peak_contact_force":0.06941,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32440.0,"raw_peak_contact_force":0.09781,"subtask_id":"approach_goal","tcp_end":[0.57403,0.2184,0.26547],"tcp_start":[0.47768,0.04654,0.14486],"tcp_to_object_dist_end":0.01497,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":56.0,"n_steps_budget":1000.0,"object_pos_end":[0.58703,0.22267,0.2394],"object_pos_start":[0.58427,0.21846,0.25455],"object_to_goal_dist_end":0.01202,"object_to_goal_dist_start":0.02632,"object_z_max":0.25459,"peak_contact_force":0.08796,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1925.0,"raw_peak_contact_force":0.13242,"subtask_id":"place_goal","tcp_end":[0.57606,0.22276,0.25081],"tcp_start":[0.57403,0.2184,0.26547],"tcp_to_object_dist_end":0.01583,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48357,"average_solve_count":213.0,"average_success_count":213.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.10502,"approach_object.approach_speed":0.16412,"descend_to_grasp.descend_speed":0.07013,"descend_to_grasp.grasp_offset_z":0.00134,"descend_to_place.descend_place_speed":0.04296,"descend_to_place.place_tolerance":0.02119,"lift.lift_height":0.16807,"lift.lift_speed":0.04292},"optimized_scores":{"best_composite_score":0.45728,"best_fitness_score":0.97728,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.53283,-0.02031,-0.00144],"force_p95":0.57154,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60421,"mean_force":0.2121,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52162,-0.02071,0.02643]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10195.0,"contact_point_centroid":[0.52603,-0.00146,0.10154],"force_p95":0.08173,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28116,"mean_force":0.05686,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52541,-0.0206,0.099]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10998.0,"contact_point_centroid":[0.5258,-0.03965,0.09897],"force_p95":0.07729,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27071,"mean_force":0.05359,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52522,-0.0206,0.09688]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":695.0,"contact_point_centroid":[0.6091,0.19857,0.23602],"force_p95":0.11822,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23799,"mean_force":0.08757,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60391,0.21719,0.23667]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":848.0,"contact_point_centroid":[0.60888,0.23592,0.23689],"force_p95":0.106,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19454,"mean_force":0.07923,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60392,0.21724,0.23649]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02111,-0.00205],"force_p95":0.1393,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18351,"mean_force":0.12727,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52386,-0.02075,0.02682]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12175.0,"contact_point_centroid":[0.56696,0.07431,0.20799],"force_p95":0.09295,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14941,"mean_force":0.06349,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56527,0.09343,0.20616]},{"body_a":"world","body_b":"grasp_target","contact_count":1136.0,"contact_point_centroid":[0.53702,-0.02132,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5133,-0.00884,0.2247]},{"body_a":"world","body_b":"grasp_target","contact_count":1440.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52839,-0.01955,0.09023]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14830.0,"contact_point_centroid":[0.56765,0.11644,0.20845],"force_p95":0.07931,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12251,"mean_force":0.05239,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56654,0.09757,0.20741]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4093.0,"contact_point_centroid":[0.52361,-0.00153,0.02814],"force_p95":0.0775,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12114,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52262,-0.02073,0.02542]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4916.0,"contact_point_centroid":[0.52358,-0.03982,0.02721],"force_p95":0.06948,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08771,"mean_force":0.04478,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52263,-0.02073,0.02543]}],"total_contact_groups":12},"final_pose_error":0.00992,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.62043,0.22101,0.21261],"final_tcp_position":[0.60496,0.22063,0.22676],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.60421,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":285.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1136.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52859,-0.0183,0.14746],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12178,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":360.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1440.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53123,-0.02088,0.03524],"tcp_start":[0.52859,-0.0183,0.14746],"tcp_to_object_dist_end":0.0109,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53688,-0.02062,0.02581],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31633,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13555,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10809.0,"raw_peak_contact_force":0.18351,"subtask_id":"grasp_object","tcp_end":[0.52259,-0.02072,0.02539],"tcp_start":[0.53123,-0.02088,0.03524],"tcp_to_object_dist_end":0.01429,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":561.0,"n_steps_budget":1000.0,"object_pos_end":[0.54469,-0.02055,0.16965],"object_pos_start":[0.53688,-0.02062,0.02581],"object_to_goal_dist_end":0.25959,"object_to_goal_dist_start":0.31633,"object_z_max":0.16941,"peak_contact_force":0.08139,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21285.0,"raw_peak_contact_force":0.60421,"subtask_id":"lift_object","tcp_end":[0.53212,-0.02055,0.17467],"tcp_start":[0.52259,-0.02072,0.02539],"tcp_to_object_dist_end":0.01353,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":772.0,"n_steps_budget":1000.0,"object_pos_end":[0.61795,0.21464,0.2313],"object_pos_start":[0.54469,-0.02055,0.16965],"object_to_goal_dist_end":0.0283,"object_to_goal_dist_start":0.25959,"object_z_max":0.23124,"peak_contact_force":0.10607,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27005.0,"raw_peak_contact_force":0.14941,"subtask_id":"approach_goal","tcp_end":[0.60355,0.21425,0.24454],"tcp_start":[0.53212,-0.02055,0.17467],"tcp_to_object_dist_end":0.01957,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":65.0,"n_steps_budget":1000.0,"object_pos_end":[0.62043,0.22101,0.21261],"object_pos_start":[0.61795,0.21464,0.2313],"object_to_goal_dist_end":0.01322,"object_to_goal_dist_start":0.0283,"object_z_max":0.2313,"peak_contact_force":0.1171,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1543.0,"raw_peak_contact_force":0.23799,"subtask_id":"place_goal","tcp_end":[0.60496,0.22063,0.22676],"tcp_start":[0.60355,0.21425,0.24454],"tcp_to_object_dist_end":0.02096,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.91049,"average_solve_count":324.0,"average_success_count":324.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.16886,"approach_object.approach_speed":0.10004,"descend_to_grasp.descend_speed":0.01298,"descend_to_grasp.grasp_offset_z":0.0023,"descend_to_place.descend_place_speed":0.06061,"descend_to_place.place_tolerance":0.03843,"lift.lift_height":0.18237,"lift.lift_speed":0.0101},"optimized_scores":{"best_composite_score":0.4568,"best_fitness_score":0.9768,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":103.0,"contact_point_centroid":[0.54155,-0.02792,-0.00153],"force_p95":0.51311,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53794,"mean_force":0.21285,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52976,-0.0283,0.02673]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11306.0,"contact_point_centroid":[0.5346,-0.00906,0.10916],"force_p95":0.08252,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25077,"mean_force":0.0569,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53386,-0.02818,0.10666]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12154.0,"contact_point_centroid":[0.53431,-0.04723,0.10566],"force_p95":0.07822,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25035,"mean_force":0.05398,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53361,-0.02818,0.10359]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.02898,-0.00208],"force_p95":0.14689,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22181,"mean_force":0.12927,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53214,-0.02838,0.02735]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":988.0,"contact_point_centroid":[0.6266,0.13561,0.20742],"force_p95":0.0948,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18963,"mean_force":0.07156,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62455,0.15458,0.20623]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1230.0,"contact_point_centroid":[0.62672,0.17336,0.20652],"force_p95":0.08367,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17406,"mean_force":0.06091,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62454,0.15454,0.20634]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7947.0,"contact_point_centroid":[0.58208,0.03985,0.20099],"force_p95":0.09316,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15322,"mean_force":0.06717,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57972,0.05885,0.19959]},{"body_a":"world","body_b":"grasp_target","contact_count":1244.0,"contact_point_centroid":[0.5456,-0.02923,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51691,-0.01215,0.22451]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4079.0,"contact_point_centroid":[0.53199,-0.00915,0.02862],"force_p95":0.07871,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13059,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53088,-0.02835,0.02591]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9065.0,"contact_point_centroid":[0.58385,0.0822,0.20085],"force_p95":0.08893,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12713,"mean_force":0.06031,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58182,0.06336,0.20032]},{"body_a":"world","body_b":"grasp_target","contact_count":1576.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53619,-0.0268,0.09076]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4945.0,"contact_point_centroid":[0.53193,-0.04746,0.02769],"force_p95":0.07075,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08709,"mean_force":0.0448,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53089,-0.02835,0.02591]}],"total_contact_groups":12},"final_pose_error":0.00986,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63369,0.15835,0.17744],"final_tcp_position":[0.62625,0.15843,0.1953],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.53794,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":312.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1244.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53616,-0.02514,0.14711],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12152,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":394.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1576.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53955,-0.0286,0.03601],"tcp_start":[0.53616,-0.02514,0.14711],"tcp_to_object_dist_end":0.01169,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54547,-0.02827,0.02572],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26043,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14151,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10824.0,"raw_peak_contact_force":0.22181,"subtask_id":"grasp_object","tcp_end":[0.53086,-0.02834,0.02587],"tcp_start":[0.53955,-0.0286,0.03601],"tcp_to_object_dist_end":0.01461,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":626.0,"n_steps_budget":1000.0,"object_pos_end":[0.55327,-0.02817,0.18252],"object_pos_start":[0.54547,-0.02827,0.02572],"object_to_goal_dist_end":0.20893,"object_to_goal_dist_start":0.26043,"object_z_max":0.18227,"peak_contact_force":0.08278,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23563.0,"raw_peak_contact_force":0.53794,"subtask_id":"lift_object","tcp_end":[0.54087,-0.02816,0.18865],"tcp_start":[0.53086,-0.02834,0.02587],"tcp_to_object_dist_end":0.01383,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":533.0,"n_steps_budget":1000.0,"object_pos_end":[0.63006,0.15088,0.19855],"object_pos_start":[0.55327,-0.02817,0.18252],"object_to_goal_dist_end":0.02594,"object_to_goal_dist_start":0.20893,"object_z_max":0.19853,"peak_contact_force":0.09037,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17012.0,"raw_peak_contact_force":0.15322,"subtask_id":"approach_goal","tcp_end":[0.6237,0.15101,0.21598],"tcp_start":[0.54087,-0.02816,0.18865],"tcp_to_object_dist_end":0.01856,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":75.0,"n_steps_budget":1000.0,"object_pos_end":[0.63369,0.15835,0.17744],"object_pos_start":[0.63006,0.15088,0.19855],"object_to_goal_dist_end":0.00665,"object_to_goal_dist_start":0.02594,"object_z_max":0.19855,"peak_contact_force":0.09295,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2218.0,"raw_peak_contact_force":0.18963,"subtask_id":"place_goal","tcp_end":[0.62625,0.15843,0.1953],"tcp_start":[0.6237,0.15101,0.21598],"tcp_to_object_dist_end":0.01935,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```