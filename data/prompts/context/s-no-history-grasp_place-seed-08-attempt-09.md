## Search State

- **Seed**: 8
- **Iteration**: 10 / 15

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

## Current Skill (Q=0.493) — your mutation base

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

- **Composite score**: 0.493
- **task_score** (E): 0.899
- **fitness_score**: 0.913  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.420

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1283 |
| descend_to_grasp | 1.00 | 1.00 | 0.1227 |
| grasp | 1.00 | 1.00 | 0.0145 |
| lift | 1.00 | 1.00 | 0.0959 |
| approach_goal | 1.00 | 1.00 | 0.2085 |
| descend_to_place | 1.00 | 1.00 | 0.0186 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.515, -0.000, 0.177) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.122 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.515, -0.000, 0.177)→(0.517, -0.001, 0.055) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.517, -0.001, 0.055)→(0.508, -0.001, 0.044) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.025) | 0.289→0.290 | 1.00 / 40.667 | 0.191 | 0.249 |
| lift | lift | 1.00 / step_budget | (0.508, -0.001, 0.044)→(0.516, -0.001, 0.139) | (0.522, -0.001, 0.025)→(0.527, -0.001, 0.120) | 0.290→0.241 | 1.00 / 39.667 | 88.864 | 0.376 |
| approach_goal | approach | 1.00 / step_budget | (0.516, -0.001, 0.139)→(0.591, 0.170, 0.227) | (0.527, -0.001, 0.120)→(0.602, 0.170, 0.206) | 0.241→0.038 | 1.00 / 37.667 | 0.089 | 0.136 |
| descend_to_place | descend | 1.00 / step_budget | (0.591, 0.170, 0.227)→(0.597, 0.186, 0.219) | (0.602, 0.170, 0.206)→(0.609, 0.186, 0.197) | 0.038→0.023 | 1.00 / 35.333 | 0.107 | 0.294 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.045
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.501
- phase_breakdown.place_goal_score: 0.638
- phase_breakdown.lift_object_score: 0.508
- phase_breakdown.approach_object_score: 0.369
- phase_breakdown.approach_goal_score: 0.374
- phase_breakdown.grasp_object_score: 0.618
- grasp_place_fitness: 0.963

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.963
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.470
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.557


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18081,"average_solve_count":271.0,"average_success_count":271.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.02257,"approach_object.approach_speed":0.15089,"descend_to_grasp.descend_speed":0.04915,"descend_to_place.descend_place_speed":0.04541,"lift.lift_height":0.15991,"lift.lift_speed":0.06803},"optimized_scores":{"best_composite_score":0.46569,"best_fitness_score":0.88569,"best_task_score":0.84339},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":69.0,"contact_point_centroid":[0.48109,0.04559,-0.00193],"force_p95":0.4192,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45899,"mean_force":0.17729,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47111,0.04412,0.04684]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2441.0,"contact_point_centroid":[0.47367,0.0634,0.08874],"force_p95":0.12045,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31359,"mean_force":0.0625,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47335,0.04437,0.08659]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48282,0.04844,-0.00234],"force_p95":0.26388,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28016,"mean_force":0.17927,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47315,0.04433,0.0466]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":422.0,"contact_point_centroid":[0.56626,0.21886,0.24969],"force_p95":0.17622,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28013,"mean_force":0.07866,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56477,0.19947,0.24842]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1928.0,"contact_point_centroid":[0.47269,0.02513,0.08722],"force_p95":0.12836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27359,"mean_force":0.07207,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47331,0.04436,0.08603]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4051.0,"contact_point_centroid":[0.47142,0.02496,0.04678],"force_p95":0.09597,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2013,"mean_force":0.06033,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47209,0.04423,0.04553]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":418.0,"contact_point_centroid":[0.56551,0.18058,0.24926],"force_p95":0.09829,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16197,"mean_force":0.05818,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56473,0.1994,0.24844]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4517.0,"contact_point_centroid":[0.51843,0.09862,0.19007],"force_p95":0.08685,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13916,"mean_force":0.05603,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51868,0.11774,0.18906]},{"body_a":"world","body_b":"grasp_target","contact_count":460.0,"contact_point_centroid":[0.4827,0.04873,-0.00173],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12369,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49504,0.01558,0.24245]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4661.0,"contact_point_centroid":[0.51732,0.13303,0.18803],"force_p95":0.08589,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12481,"mean_force":0.05511,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.51657,0.11401,0.18631]},{"body_a":"world","body_b":"grasp_target","contact_count":704.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.48367,0.03904,0.11684]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5403.0,"contact_point_centroid":[0.47228,0.06357,0.04746],"force_p95":0.08795,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10278,"mean_force":0.05046,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4721,0.04423,0.04554]}],"total_contact_groups":12},"final_pose_error":0.02968,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57972,0.20442,0.22333],"final_tcp_position":[0.56703,0.20319,0.24707],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":266.43223,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":116.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28997,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12249,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":460.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48819,0.03353,0.17718],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15201,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":176.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28997,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":704.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.48075,0.04493,0.05518],"tcp_start":[0.48819,0.03353,0.17718],"tcp_to_object_dist_end":0.02947,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4827,0.04567,0.0248],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29274,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.24531,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11254.0,"raw_peak_contact_force":0.28016,"subtask_id":"grasp_object","tcp_end":[0.47206,0.04422,0.0455],"tcp_start":[0.48075,0.04493,0.05518],"tcp_to_object_dist_end":0.02332,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":112.0,"n_steps_budget":1000.0,"object_pos_end":[0.48899,0.04604,0.11416],"object_pos_start":[0.4827,0.04567,0.0248],"object_to_goal_dist_end":0.23576,"object_to_goal_dist_start":0.29274,"object_z_max":0.11328,"peak_contact_force":266.43223,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4438.0,"raw_peak_contact_force":0.45899,"subtask_id":"lift_object","tcp_end":[0.47754,0.04486,0.13562],"tcp_start":[0.47206,0.04422,0.0455],"tcp_to_object_dist_end":0.02435,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":248.0,"n_steps_budget":1000.0,"object_pos_end":[0.5737,0.1971,0.22401],"object_pos_start":[0.48899,0.04604,0.11416],"object_to_goal_dist_end":0.03343,"object_to_goal_dist_start":0.23576,"object_z_max":0.22353,"peak_contact_force":0.08411,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9178.0,"raw_peak_contact_force":0.13916,"subtask_id":"approach_goal","tcp_end":[0.56348,0.19642,0.2481],"tcp_start":[0.47754,0.04486,0.13562],"tcp_to_object_dist_end":0.02618,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":22.0,"n_steps_budget":1000.0,"object_pos_end":[0.57972,0.20442,0.22333],"object_pos_start":[0.5737,0.1971,0.22401],"object_to_goal_dist_end":0.02555,"object_to_goal_dist_start":0.03343,"object_z_max":0.2251,"peak_contact_force":0.11198,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":840.0,"raw_peak_contact_force":0.28013,"subtask_id":"place_goal","tcp_end":[0.56703,0.20319,0.24707],"tcp_start":[0.56348,0.19642,0.2481],"tcp_to_object_dist_end":0.02694,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.73438,"average_solve_count":384.0,"average_success_count":384.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.01002,"approach_object.approach_speed":0.19142,"descend_to_grasp.descend_speed":0.05802,"descend_to_place.descend_place_speed":0.01227,"lift.lift_height":0.15919,"lift.lift_speed":0.01293},"optimized_scores":{"best_composite_score":0.47014,"best_fitness_score":0.89014,"best_task_score":0.85329},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":109.0,"contact_point_centroid":[0.5345,-0.01968,-0.00172],"force_p95":0.30824,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.34556,"mean_force":0.16401,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52037,-0.01957,0.044]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1223.0,"contact_point_centroid":[0.59956,0.21477,0.22876],"force_p95":0.10908,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23949,"mean_force":0.06553,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59808,0.19552,0.2264]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3028.0,"contact_point_centroid":[0.52296,-0.03878,0.08127],"force_p95":0.10332,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23033,"mean_force":0.05526,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52315,-0.01964,0.07958]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53709,-0.02112,-0.00214],"force_p95":0.16337,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22431,"mean_force":0.13332,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52262,-0.01961,0.04469]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2879.0,"contact_point_centroid":[0.52312,-0.00045,0.08241],"force_p95":0.1056,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22388,"mean_force":0.05591,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5232,-0.01965,0.08031]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1400.0,"contact_point_centroid":[0.59945,0.17653,0.22828],"force_p95":0.0805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15923,"mean_force":0.05093,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59805,0.19541,0.22648]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4082.0,"contact_point_centroid":[0.52285,-0.00037,0.04605],"force_p95":0.08119,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14608,"mean_force":0.05188,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52145,-0.01958,0.04338]},{"body_a":"world","body_b":"grasp_target","contact_count":452.0,"contact_point_centroid":[0.53702,-0.02132,-0.00172],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12372,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51263,-0.00675,0.24258]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5671.0,"contact_point_centroid":[0.5614,0.05944,0.18098],"force_p95":0.07849,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13794,"mean_force":0.05111,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56107,0.07851,0.17912]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5001.0,"contact_point_centroid":[0.56056,0.09433,0.18028],"force_p95":0.08164,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.126,"mean_force":0.05496,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56001,0.07516,0.17765]},{"body_a":"world","body_b":"grasp_target","contact_count":684.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52698,-0.01709,0.11596]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5019.0,"contact_point_centroid":[0.52275,-0.03874,0.04514],"force_p95":0.07393,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07644,"mean_force":0.04436,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52145,-0.01958,0.04338]}],"total_contact_groups":12},"final_pose_error":0.0242,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61295,0.20515,0.20044],"final_tcp_position":[0.60112,0.20542,0.22099],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.34556,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":114.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12246,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":452.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52549,-0.01456,0.17759],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":171.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":684.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.5308,-0.01969,0.05497],"tcp_start":[0.52549,-0.01456,0.17759],"tcp_to_object_dist_end":0.02966,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53699,-0.01997,0.02551],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31596,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.15643,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10901.0,"raw_peak_contact_force":0.22431,"subtask_id":"grasp_object","tcp_end":[0.52142,-0.01958,0.04334],"tcp_start":[0.5308,-0.01969,0.05497],"tcp_to_object_dist_end":0.02368,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":141.0,"n_steps_budget":1000.0,"object_pos_end":[0.54133,-0.02012,0.11801],"object_pos_start":[0.53699,-0.01997,0.02551],"object_to_goal_dist_end":0.27238,"object_to_goal_dist_start":0.31596,"object_z_max":0.11717,"peak_contact_force":0.07243,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6016.0,"raw_peak_contact_force":0.34556,"subtask_id":"lift_object","tcp_end":[0.52997,-0.0198,0.13565],"tcp_start":[0.52142,-0.01958,0.04334],"tcp_to_object_dist_end":0.02099,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":278.0,"n_steps_budget":1000.0,"object_pos_end":[0.60816,0.18802,0.2103],"object_pos_start":[0.54133,-0.02012,0.11801],"object_to_goal_dist_end":0.03989,"object_to_goal_dist_start":0.27238,"object_z_max":0.20994,"peak_contact_force":0.0817,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10672.0,"raw_peak_contact_force":0.13794,"subtask_id":"approach_goal","tcp_end":[0.59707,0.18842,0.23035],"tcp_start":[0.52997,-0.0198,0.13565],"tcp_to_object_dist_end":0.02291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":70.0,"n_steps_budget":1000.0,"object_pos_end":[0.61295,0.20515,0.20044],"object_pos_start":[0.60816,0.18802,0.2103],"object_to_goal_dist_end":0.0238,"object_to_goal_dist_start":0.03989,"object_z_max":0.21094,"peak_contact_force":0.10116,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2623.0,"raw_peak_contact_force":0.23949,"subtask_id":"place_goal","tcp_end":[0.60112,0.20542,0.22099],"tcp_start":[0.59707,0.18842,0.23035],"tcp_to_object_dist_end":0.02372,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.61353,"average_solve_count":414.0,"average_success_count":414.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.03362,"approach_object.approach_speed":0.19515,"descend_to_grasp.descend_speed":0.09276,"descend_to_place.descend_place_speed":0.00731,"lift.lift_height":0.1709,"lift.lift_speed":0.01141},"optimized_scores":{"best_composite_score":0.54267,"best_fitness_score":0.96267,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":1758.0,"contact_point_centroid":[0.61841,0.15407,0.19781],"force_p95":0.10951,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36269,"mean_force":0.06921,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61564,0.13491,0.19675]},{"body_a":"world","body_b":"grasp_target","contact_count":108.0,"contact_point_centroid":[0.5435,-0.02732,-0.00182],"force_p95":0.28865,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.32484,"mean_force":0.1552,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52804,-0.02677,0.04344]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2571.0,"contact_point_centroid":[0.53262,-0.00775,0.08825],"force_p95":0.11408,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28023,"mean_force":0.06664,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53159,-0.0269,0.08537]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3158.0,"contact_point_centroid":[0.53182,-0.04577,0.08712],"force_p95":0.10259,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26549,"mean_force":0.05728,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53153,-0.0269,0.08501]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54572,-0.02902,-0.00221],"force_p95":0.17963,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24381,"mean_force":0.13817,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53031,-0.02683,0.0441]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2199.0,"contact_point_centroid":[0.61777,0.11644,0.19778],"force_p95":0.09132,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20683,"mean_force":0.05564,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61569,0.13508,0.19649]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4052.0,"contact_point_centroid":[0.53101,-0.00776,0.04527],"force_p95":0.1013,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15489,"mean_force":0.05625,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52913,-0.0268,0.04274]},{"body_a":"world","body_b":"grasp_target","contact_count":464.0,"contact_point_centroid":[0.5456,-0.02923,-0.00173],"force_p95":0.13812,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12368,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51544,-0.0093,0.24234]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4340.0,"contact_point_centroid":[0.57378,0.02441,0.1736],"force_p95":0.08534,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13238,"mean_force":0.05303,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57289,0.04343,0.17181]},{"body_a":"world","body_b":"grasp_target","contact_count":656.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53411,-0.02353,0.11519]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3771.0,"contact_point_centroid":[0.57484,0.06382,0.17483],"force_p95":0.08979,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10933,"mean_force":0.05868,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5735,0.04468,0.17227]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4820.0,"contact_point_centroid":[0.53099,-0.04583,0.0446],"force_p95":0.08512,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09061,"mean_force":0.04689,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52914,-0.0268,0.04275]}],"total_contact_groups":12},"final_pose_error":0.01948,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63437,0.14846,0.16737],"final_tcp_position":[0.62216,0.14898,0.18862],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.36269,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":117.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.1225,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":464.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53157,-0.02006,0.17697],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":164.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":656.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.53877,-0.027,0.05483],"tcp_start":[0.53157,-0.02006,0.17697],"tcp_to_object_dist_end":0.02969,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54591,-0.02742,0.02523],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.25994,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.17034,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10672.0,"raw_peak_contact_force":0.24381,"subtask_id":"grasp_object","tcp_end":[0.5291,-0.0268,0.0427],"tcp_start":[0.53877,-0.027,0.05483],"tcp_to_object_dist_end":0.02426,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":152.0,"n_steps_budget":1000.0,"object_pos_end":[0.55171,-0.02769,0.12914],"object_pos_start":[0.54591,-0.02742,0.02523],"object_to_goal_dist_end":0.2144,"object_to_goal_dist_start":0.25994,"object_z_max":0.12831,"peak_contact_force":0.0863,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5837.0,"raw_peak_contact_force":0.32484,"subtask_id":"lift_object","tcp_end":[0.53903,-0.02716,0.14683],"tcp_start":[0.5291,-0.0268,0.0427],"tcp_to_object_dist_end":0.02178,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":217.0,"n_steps_budget":1000.0,"object_pos_end":[0.62561,0.12571,0.18329],"object_pos_start":[0.55171,-0.02769,0.12914],"object_to_goal_dist_end":0.04038,"object_to_goal_dist_start":0.2144,"object_z_max":0.18299,"peak_contact_force":0.1014,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8111.0,"raw_peak_contact_force":0.13238,"subtask_id":"approach_goal","tcp_end":[0.61343,0.12643,0.20326],"tcp_start":[0.53903,-0.02716,0.14683],"tcp_to_object_dist_end":0.0234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":120.0,"n_steps_budget":1000.0,"object_pos_end":[0.63437,0.14846,0.16737],"object_pos_start":[0.62561,0.12571,0.18329],"object_to_goal_dist_end":0.0191,"object_to_goal_dist_start":0.04038,"object_z_max":0.18376,"peak_contact_force":0.10887,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3957.0,"raw_peak_contact_force":0.36269,"subtask_id":"place_goal","tcp_end":[0.62216,0.14898,0.18862],"tcp_start":[0.61343,0.12643,0.20326],"tcp_to_object_dist_end":0.02451,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```