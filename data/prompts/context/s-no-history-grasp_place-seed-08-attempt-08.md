## Search State

- **Seed**: 8
- **Iteration**: 9 / 15

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
| approach_object | 1.00 | 1.00 | 0.1588 |
| descend_to_grasp | 1.00 | 1.00 | 0.1128 |
| grasp | 1.00 | 1.00 | 0.0126 |
| lift | 1.00 | 1.00 | 0.1384 |
| approach_goal | 1.00 | 1.00 | 0.2279 |
| descend_to_place | 1.00 | 1.00 | 0.0183 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.148) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.516, -0.001, 0.148)→(0.516, -0.001, 0.035) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 8.061 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.516, -0.001, 0.035)→(0.508, -0.001, 0.026) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 43.000 | 0.148 | 0.224 |
| lift | lift | 1.00 / step_budget | (0.508, -0.001, 0.026)→(0.517, -0.001, 0.164) | (0.522, -0.001, 0.026)→(0.529, -0.001, 0.159) | 0.289→0.228 | 1.00 / 39.000 | 0.079 | 0.602 |
| approach_goal | approach | 1.00 / step_budget | (0.517, -0.001, 0.164)→(0.601, 0.195, 0.241) | (0.529, -0.001, 0.159)→(0.610, 0.195, 0.230) | 0.228→0.028 | 1.00 / 39.000 | 0.078 | 0.092 |
| descend_to_place | descend | 1.00 / step_budget | (0.601, 0.195, 0.241)→(0.602, 0.201, 0.224) | (0.610, 0.195, 0.230)→(0.613, 0.201, 0.212) | 0.028→0.011 | 1.00 / 33.333 | 0.085 | 0.139 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.467
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.675
- phase_breakdown.place_goal_score: 0.656
- phase_breakdown.lift_object_score: 0.881
- phase_breakdown.approach_object_score: 0.675
- phase_breakdown.approach_goal_score: 0.671
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
- **Final σ (mean)**: 0.360


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.67876,"average_solve_count":386.0,"average_success_count":386.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.02173,"approach_object.approach_speed":0.13902,"descend_to_grasp.descend_speed":0.02612,"descend_to_grasp.grasp_offset_z":0.00016,"descend_to_place.descend_place_speed":0.00768,"descend_to_place.place_tolerance":0.044,"lift.lift_height":0.16998,"lift.lift_speed":0.04516},"optimized_scores":{"best_composite_score":0.46013,"best_fitness_score":0.98013,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":89.0,"contact_point_centroid":[0.47884,0.04609,-0.00157],"force_p95":0.611,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63479,"mean_force":0.22679,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46938,0.04662,0.02807]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10815.0,"contact_point_centroid":[0.47216,0.06566,0.10163],"force_p95":0.07552,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29771,"mean_force":0.05041,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47242,0.04646,0.10007]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48277,0.0484,-0.00219],"force_p95":0.17551,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26516,"mean_force":0.13697,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47142,0.04685,0.02792]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10930.0,"contact_point_centroid":[0.47177,0.02727,0.10065],"force_p95":0.07337,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2539,"mean_force":0.04908,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47235,0.04646,0.09903]},{"body_a":"world","body_b":"grasp_target","contact_count":1160.0,"contact_point_centroid":[0.4827,0.04873,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49069,0.0201,0.22533]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1560.0,"contact_point_centroid":[0.57425,0.23844,0.26044],"force_p95":0.0745,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13493,"mean_force":0.05005,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57383,0.21916,0.25948]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1600.0,"contact_point_centroid":[0.57437,0.20006,0.26099],"force_p95":0.07152,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.127,"mean_force":0.04769,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57381,0.21913,0.25959]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4990.0,"contact_point_centroid":[0.47011,0.0275,0.02975],"force_p95":0.07179,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12622,"mean_force":0.0431,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47029,0.04674,0.02679]},{"body_a":"world","body_b":"grasp_target","contact_count":1640.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47857,0.04442,0.09098]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16320.0,"contact_point_centroid":[0.52568,0.11523,0.22253],"force_p95":0.06869,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08503,"mean_force":0.04565,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52585,0.13439,0.22075]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5484.0,"contact_point_centroid":[0.47002,0.06611,0.02913],"force_p95":0.0732,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08442,"mean_force":0.04174,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4703,0.04674,0.0268]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15677.0,"contact_point_centroid":[0.52546,0.15319,0.22179],"force_p95":0.06891,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0767,"mean_force":0.04787,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52562,0.13398,0.22052]}],"total_contact_groups":12},"final_pose_error":0.00986,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58571,0.2223,0.23795],"final_tcp_position":[0.57569,0.22236,0.24958],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":23.93764,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":291.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1160.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48196,0.04166,0.14835],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12254,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":410.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":23.93764,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1640.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.47813,0.0475,0.03477],"tcp_start":[0.48196,0.04166,0.14835],"tcp_to_object_dist_end":0.00994,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4826,0.04692,0.02536],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.2916,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16681,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12274.0,"raw_peak_contact_force":0.26516,"subtask_id":"grasp_object","tcp_end":[0.47026,0.04673,0.02676],"tcp_start":[0.47813,0.0475,0.03477],"tcp_to_object_dist_end":0.01242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":514.0,"n_steps_budget":1000.0,"object_pos_end":[0.48911,0.04664,0.17089],"object_pos_start":[0.4826,0.04692,0.02536],"object_to_goal_dist_end":0.21298,"object_to_goal_dist_start":0.2916,"object_z_max":0.17062,"peak_contact_force":0.07303,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21834.0,"raw_peak_contact_force":0.63479,"subtask_id":"lift_object","tcp_end":[0.47818,0.04656,0.17609],"tcp_start":[0.47026,0.04673,0.02676],"tcp_to_object_dist_end":0.01211,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":747.0,"n_steps_budget":1000.0,"object_pos_end":[0.58242,0.21725,0.25544],"object_pos_start":[0.48911,0.04664,0.17089],"object_to_goal_dist_end":0.02753,"object_to_goal_dist_start":0.21298,"object_z_max":0.25534,"peak_contact_force":0.06829,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31997.0,"raw_peak_contact_force":0.08503,"subtask_id":"approach_goal","tcp_end":[0.57352,0.21734,0.26652],"tcp_start":[0.47818,0.04656,0.17609],"tcp_to_object_dist_end":0.01421,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":78.0,"n_steps_budget":1000.0,"object_pos_end":[0.58571,0.2223,0.23795],"object_pos_start":[0.58242,0.21725,0.25544],"object_to_goal_dist_end":0.01065,"object_to_goal_dist_start":0.02753,"object_z_max":0.25546,"peak_contact_force":0.08009,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3160.0,"raw_peak_contact_force":0.13493,"subtask_id":"place_goal","tcp_end":[0.57569,0.22236,0.24958],"tcp_start":[0.57352,0.21734,0.26652],"tcp_to_object_dist_end":0.01535,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29474,"average_solve_count":285.0,"average_success_count":285.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.0721,"approach_object.approach_speed":0.09342,"descend_to_grasp.descend_speed":0.08621,"descend_to_grasp.grasp_offset_z":0.00154,"descend_to_place.descend_place_speed":0.0978,"descend_to_place.place_tolerance":0.02822,"lift.lift_height":0.17056,"lift.lift_speed":0.0231},"optimized_scores":{"best_composite_score":0.45724,"best_fitness_score":0.97724,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":104.0,"contact_point_centroid":[0.53314,-0.02037,-0.00152],"force_p95":0.49694,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53935,"mean_force":0.21589,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52149,-0.0207,0.0264]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10729.0,"contact_point_centroid":[0.52592,-0.00147,0.10236],"force_p95":0.08159,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25072,"mean_force":0.05626,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52533,-0.02059,0.09984]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11438.0,"contact_point_centroid":[0.52568,-0.03965,0.09959],"force_p95":0.07745,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24243,"mean_force":0.05364,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52512,-0.0206,0.09747]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02111,-0.00205],"force_p95":0.13938,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18346,"mean_force":0.12728,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52383,-0.02075,0.02703]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1003.0,"contact_point_centroid":[0.60631,0.23613,0.23803],"force_p95":0.08678,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14993,"mean_force":0.06458,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60404,0.21711,0.23674]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1084.0,"contact_point_centroid":[0.60638,0.19839,0.23714],"force_p95":0.08347,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14778,"mean_force":0.05883,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60407,0.21723,0.23636]},{"body_a":"world","body_b":"grasp_target","contact_count":1220.0,"contact_point_centroid":[0.53702,-0.02132,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51328,-0.00883,0.2249]},{"body_a":"world","body_b":"grasp_target","contact_count":1396.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52851,-0.01956,0.0904]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4093.0,"contact_point_centroid":[0.52359,-0.00153,0.02835],"force_p95":0.07751,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12136,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52259,-0.02073,0.02564]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15517.0,"contact_point_centroid":[0.56691,0.07817,0.20967],"force_p95":0.07552,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09668,"mean_force":0.05149,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56649,0.0973,0.20858]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15812.0,"contact_point_centroid":[0.56836,0.12085,0.21101],"force_p95":0.07468,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08859,"mean_force":0.05015,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56788,0.10175,0.20992]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4917.0,"contact_point_centroid":[0.52356,-0.03982,0.02743],"force_p95":0.06948,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08758,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5226,-0.02073,0.02564]}],"total_contact_groups":12},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.6161,0.22073,0.21385],"final_tcp_position":[0.60504,0.22056,0.22685],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.53935,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":306.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1220.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52872,-0.0183,0.14755],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12185,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":349.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1396.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53119,-0.02087,0.03545],"tcp_start":[0.52872,-0.0183,0.14755],"tcp_to_object_dist_end":0.0111,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53688,-0.02062,0.02581],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31633,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13563,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10810.0,"raw_peak_contact_force":0.18346,"subtask_id":"grasp_object","tcp_end":[0.52256,-0.02072,0.0256],"tcp_start":[0.53119,-0.02087,0.03545],"tcp_to_object_dist_end":0.01432,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":586.0,"n_steps_budget":1000.0,"object_pos_end":[0.54451,-0.02054,0.17187],"object_pos_start":[0.53688,-0.02062,0.02581],"object_to_goal_dist_end":0.25931,"object_to_goal_dist_start":0.31633,"object_z_max":0.17162,"peak_contact_force":0.08164,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22271.0,"raw_peak_contact_force":0.53935,"subtask_id":"lift_object","tcp_end":[0.53213,-0.02055,0.17705],"tcp_start":[0.52256,-0.02072,0.0256],"tcp_to_object_dist_end":0.01342,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":793.0,"n_steps_budget":1000.0,"object_pos_end":[0.61345,0.2139,0.23213],"object_pos_start":[0.54451,-0.02054,0.17187],"object_to_goal_dist_end":0.02851,"object_to_goal_dist_start":0.25931,"object_z_max":0.23206,"peak_contact_force":0.08964,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31329.0,"raw_peak_contact_force":0.09668,"subtask_id":"approach_goal","tcp_end":[0.60374,0.21415,0.24468],"tcp_start":[0.53213,-0.02055,0.17705],"tcp_to_object_dist_end":0.01587,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":65.0,"n_steps_budget":1000.0,"object_pos_end":[0.6161,0.22073,0.21385],"object_pos_start":[0.61345,0.2139,0.23213],"object_to_goal_dist_end":0.01115,"object_to_goal_dist_start":0.02851,"object_z_max":0.23213,"peak_contact_force":0.08521,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2087.0,"raw_peak_contact_force":0.14993,"subtask_id":"place_goal","tcp_end":[0.60504,0.22056,0.22685],"tcp_start":[0.60374,0.21415,0.24468],"tcp_to_object_dist_end":0.01707,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.06515,"average_solve_count":307.0,"average_success_count":307.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.03913,"approach_object.approach_speed":0.0855,"descend_to_grasp.descend_speed":0.03809,"descend_to_grasp.grasp_offset_z":0.00062,"descend_to_place.descend_place_speed":0.09591,"descend_to_place.place_tolerance":0.04828,"lift.lift_height":0.1312,"lift.lift_speed":0.04654},"optimized_scores":{"best_composite_score":0.45662,"best_fitness_score":0.97662,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":93.0,"contact_point_centroid":[0.54173,-0.02784,-0.00146],"force_p95":0.59817,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63078,"mean_force":0.20384,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52987,-0.02831,0.02544]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7664.0,"contact_point_centroid":[0.53445,-0.00903,0.08336],"force_p95":0.0832,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28435,"mean_force":0.05905,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53364,-0.02818,0.08076]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8596.0,"contact_point_centroid":[0.53419,-0.0472,0.08085],"force_p95":0.07828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27989,"mean_force":0.05405,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53343,-0.02818,0.07889]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54562,-0.02896,-0.00208],"force_p95":0.14665,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22347,"mean_force":0.12924,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53208,-0.02839,0.02581]},{"body_a":"world","body_b":"grasp_target","contact_count":1260.0,"contact_point_centroid":[0.5456,-0.02923,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51685,-0.01216,0.22443]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1060.0,"contact_point_centroid":[0.627,0.17483,0.20579],"force_p95":0.08412,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13135,"mean_force":0.05936,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62511,0.15582,0.20559]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":968.0,"contact_point_centroid":[0.62702,0.13675,0.20698],"force_p95":0.08995,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1286,"mean_force":0.06278,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62508,0.15574,0.20589]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4077.0,"contact_point_centroid":[0.53195,-0.00915,0.02708],"force_p95":0.07869,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12808,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53082,-0.02835,0.02437]},{"body_a":"world","body_b":"grasp_target","contact_count":1512.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53614,-0.02683,0.08958]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15106.0,"contact_point_centroid":[0.58274,0.04657,0.17562],"force_p95":0.0758,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09498,"mean_force":0.05121,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58197,0.06564,0.17436]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14249.0,"contact_point_centroid":[0.5844,0.08817,0.17739],"force_p95":0.07845,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08894,"mean_force":0.05346,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5836,0.06905,0.17585]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4945.0,"contact_point_centroid":[0.53189,-0.04747,0.02615],"force_p95":0.07067,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08823,"mean_force":0.04483,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53083,-0.02835,0.02438]}],"total_contact_groups":12},"final_pose_error":0.00982,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63786,0.15862,0.18439],"final_tcp_position":[0.62638,0.15877,0.19603],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.63078,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":316.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1260.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53596,-0.02517,0.14678],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12121,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":378.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1512.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53953,-0.0286,0.0345],"tcp_start":[0.53596,-0.02517,0.14678],"tcp_to_object_dist_end":0.01044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54546,-0.02826,0.02573],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26042,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14117,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10822.0,"raw_peak_contact_force":0.22347,"subtask_id":"grasp_object","tcp_end":[0.53079,-0.02834,0.02434],"tcp_start":[0.53953,-0.0286,0.0345],"tcp_to_object_dist_end":0.01473,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":436.0,"n_steps_budget":1000.0,"object_pos_end":[0.55346,-0.02812,0.13477],"object_pos_start":[0.54546,-0.02826,0.02573],"object_to_goal_dist_end":0.21295,"object_to_goal_dist_start":0.26042,"object_z_max":0.13453,"peak_contact_force":0.0825,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16353.0,"raw_peak_contact_force":0.63078,"subtask_id":"lift_object","tcp_end":[0.54002,-0.02814,0.13788],"tcp_start":[0.53079,-0.02834,0.02434],"tcp_to_object_dist_end":0.01379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":760.0,"n_steps_budget":1000.0,"object_pos_end":[0.63529,0.15329,0.20203],"object_pos_start":[0.55346,-0.02812,0.13477],"object_to_goal_dist_end":0.02778,"object_to_goal_dist_start":0.21295,"object_z_max":0.20195,"peak_contact_force":0.07728,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29355.0,"raw_peak_contact_force":0.09498,"subtask_id":"approach_goal","tcp_end":[0.62451,0.1533,0.21318],"tcp_start":[0.54002,-0.02814,0.13788],"tcp_to_object_dist_end":0.0155,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":63.0,"n_steps_budget":1000.0,"object_pos_end":[0.63786,0.15862,0.18439],"object_pos_start":[0.63529,0.15329,0.20203],"object_to_goal_dist_end":0.01099,"object_to_goal_dist_start":0.02778,"object_z_max":0.20204,"peak_contact_force":0.09041,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2028.0,"raw_peak_contact_force":0.13135,"subtask_id":"place_goal","tcp_end":[0.62638,0.15877,0.19603],"tcp_start":[0.62451,0.1533,0.21318],"tcp_to_object_dist_end":0.01634,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```