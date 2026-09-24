## Search State

- **Seed**: 8
- **Iteration**: 14 / 15

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
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1585 |
| descend_to_grasp | 1.00 | 1.00 | 0.1107 |
| grasp | 1.00 | 1.00 | 0.0126 |
| lift | 1.00 | 1.00 | 0.1447 |
| approach_goal | 1.00 | 1.00 | 0.2308 |
| descend_to_place | 1.00 | 1.00 | 0.0190 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.148) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.516, -0.001, 0.148)→(0.516, -0.001, 0.037) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.516, -0.001, 0.037)→(0.508, -0.001, 0.028) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 43.000 | 0.148 | 0.222 |
| lift | lift | 1.00 / step_budget | (0.508, -0.001, 0.028)→(0.517, -0.001, 0.172) | (0.522, -0.001, 0.026)→(0.531, -0.001, 0.165) | 0.289→0.233 | 1.00 / 32.333 | 0.090 | 0.580 |
| approach_goal | approach | 1.00 / step_budget | (0.517, -0.001, 0.172)→(0.601, 0.195, 0.242) | (0.531, -0.001, 0.165)→(0.610, 0.194, 0.226) | 0.233→0.024 | 1.00 / 29.000 | 0.113 | 0.127 |
| descend_to_place | descend | 1.00 / step_budget | (0.601, 0.195, 0.242)→(0.602, 0.201, 0.224) | (0.610, 0.194, 0.226)→(0.612, 0.201, 0.207) | 0.024→0.008 | 1.00 / 25.000 | 0.118 | 0.205 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.640
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.555
- phase_breakdown.place_goal_score: 0.641
- phase_breakdown.lift_object_score: 0.294
- phase_breakdown.approach_object_score: 0.671
- phase_breakdown.approach_goal_score: 0.673
- phase_breakdown.grasp_object_score: 0.495
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
- **Final σ (mean)**: 0.368


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23431,"average_solve_count":239.0,"average_success_count":239.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.02042,"approach_object.approach_speed":0.1046,"descend_to_grasp.descend_speed":0.0631,"descend_to_grasp.grasp_offset_z":0.0006,"descend_to_place.descend_place_speed":0.07899,"descend_to_place.place_tolerance":0.02276,"lift.lift_height":0.11268,"lift.lift_speed":0.10343},"optimized_scores":{"best_composite_score":0.4601,"best_fitness_score":0.9801,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.48022,0.0462,-0.0015],"force_p95":0.58066,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64008,"mean_force":0.14496,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46937,0.0466,0.02874]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5386.0,"contact_point_centroid":[0.47323,0.06551,0.07012],"force_p95":0.09844,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30313,"mean_force":0.05884,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47181,0.04645,0.0682]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5020.0,"contact_point_centroid":[0.47337,0.02739,0.072],"force_p95":0.10234,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27072,"mean_force":0.06149,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47196,0.04645,0.0695]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48277,0.0484,-0.00219],"force_p95":0.17551,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26456,"mean_force":0.13697,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47145,0.04684,0.02835]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":549.0,"contact_point_centroid":[0.57871,0.23875,0.25574],"force_p95":0.14852,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25532,"mean_force":0.09052,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57511,0.22091,0.2591]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":367.0,"contact_point_centroid":[0.57828,0.20274,0.25633],"force_p95":0.16864,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2403,"mean_force":0.12006,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57504,0.22077,0.25968]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11187.0,"contact_point_centroid":[0.52703,0.11282,0.18889],"force_p95":0.11734,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17415,"mean_force":0.07965,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52339,0.13143,0.18886]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11415.0,"contact_point_centroid":[0.52963,0.15304,0.19205],"force_p95":0.10827,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17037,"mean_force":0.07757,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52513,0.13448,0.19147]},{"body_a":"world","body_b":"grasp_target","contact_count":1188.0,"contact_point_centroid":[0.4827,0.04873,-0.00189],"force_p95":0.13631,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49076,0.02004,0.22555]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4992.0,"contact_point_centroid":[0.47013,0.0275,0.03015],"force_p95":0.07147,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12843,"mean_force":0.04309,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47033,0.04673,0.02721]},{"body_a":"world","body_b":"grasp_target","contact_count":1524.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47873,0.04442,0.09111]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5484.0,"contact_point_centroid":[0.47005,0.06611,0.02953],"force_p95":0.07319,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08408,"mean_force":0.04172,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47033,0.04673,0.02722]}],"total_contact_groups":12},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58604,0.223,0.23014],"final_tcp_position":[0.57624,0.22301,0.2512],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.64008,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":298.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1188.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48208,0.0416,0.14864],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12283,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":381.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1524.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.47822,0.0475,0.03523],"tcp_start":[0.48208,0.0416,0.14864],"tcp_to_object_dist_end":0.01031,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4826,0.04693,0.02536],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.2916,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16693,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12276.0,"raw_peak_contact_force":0.26456,"subtask_id":"grasp_object","tcp_end":[0.4703,0.04673,0.02719],"tcp_start":[0.47822,0.0475,0.03523],"tcp_to_object_dist_end":0.01244,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":293.0,"n_steps_budget":690.0,"object_pos_end":[0.49521,0.04679,0.1139],"object_pos_start":[0.4826,0.04693,0.02536],"object_to_goal_dist_end":0.23292,"object_to_goal_dist_start":0.2916,"object_z_max":0.11364,"peak_contact_force":0.10897,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10484.0,"raw_peak_contact_force":0.64008,"subtask_id":"lift_object","tcp_end":[0.47725,0.04652,0.11902],"tcp_start":[0.4703,0.04673,0.02719],"tcp_to_object_dist_end":0.01868,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":896.0,"n_steps_budget":1000.0,"object_pos_end":[0.58433,0.21925,0.24482],"object_pos_start":[0.49521,0.04679,0.1139],"object_to_goal_dist_end":0.01743,"object_to_goal_dist_start":0.23292,"object_z_max":0.2447,"peak_contact_force":0.15941,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22602.0,"raw_peak_contact_force":0.17415,"subtask_id":"approach_goal","tcp_end":[0.57451,0.21921,0.26482],"tcp_start":[0.47725,0.04652,0.11902],"tcp_to_object_dist_end":0.02229,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":52.0,"n_steps_budget":1000.0,"object_pos_end":[0.58604,0.223,0.23014],"object_pos_start":[0.58433,0.21925,0.24482],"object_to_goal_dist_end":0.00719,"object_to_goal_dist_start":0.01743,"object_z_max":0.24485,"peak_contact_force":0.16498,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":916.0,"raw_peak_contact_force":0.25532,"subtask_id":"place_goal","tcp_end":[0.57624,0.22301,0.2512],"tcp_start":[0.57451,0.21921,0.26482],"tcp_to_object_dist_end":0.02323,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39453,"average_solve_count":256.0,"average_success_count":256.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.09393,"approach_object.approach_speed":0.19387,"descend_to_grasp.descend_speed":0.06575,"descend_to_grasp.grasp_offset_z":0.00102,"descend_to_place.descend_place_speed":0.03307,"descend_to_place.place_tolerance":0.04,"lift.lift_height":0.19986,"lift.lift_speed":0.01584},"optimized_scores":{"best_composite_score":0.45721,"best_fitness_score":0.97721,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":96.0,"contact_point_centroid":[0.5329,-0.02033,-0.0015],"force_p95":0.54,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5696,"mean_force":0.22692,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52151,-0.0207,0.02606]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12461.0,"contact_point_centroid":[0.52613,-0.00147,0.11703],"force_p95":0.0809,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26274,"mean_force":0.05617,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5255,-0.02059,0.11453]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13254.0,"contact_point_centroid":[0.52589,-0.03965,0.11392],"force_p95":0.07724,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25539,"mean_force":0.05358,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5253,-0.02059,0.1118]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02111,-0.00205],"force_p95":0.13941,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18408,"mean_force":0.1273,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52382,-0.02074,0.02665]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1228.0,"contact_point_centroid":[0.60596,0.2354,0.23754],"force_p95":0.08243,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16035,"mean_force":0.05782,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60387,0.21657,0.23708]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":910.0,"contact_point_centroid":[0.6057,0.19767,0.23783],"force_p95":0.09688,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14976,"mean_force":0.0732,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60389,0.21665,0.23685]},{"body_a":"world","body_b":"grasp_target","contact_count":1112.0,"contact_point_centroid":[0.53702,-0.02132,-0.00188],"force_p95":0.13647,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51332,-0.00885,0.22471]},{"body_a":"world","body_b":"grasp_target","contact_count":1464.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52833,-0.01953,0.09023]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4092.0,"contact_point_centroid":[0.52359,-0.00152,0.02797],"force_p95":0.07752,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12113,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52258,-0.02072,0.02526]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11589.0,"contact_point_centroid":[0.56743,0.07513,0.22521],"force_p95":0.09179,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10891,"mean_force":0.06224,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56601,0.0943,0.22342]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14659.0,"contact_point_centroid":[0.56788,0.11733,0.22506],"force_p95":0.07699,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10219,"mean_force":0.04946,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56729,0.09848,0.22415]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4918.0,"contact_point_centroid":[0.52355,-0.03982,0.02704],"force_p95":0.06948,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08805,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52258,-0.02072,0.02526]}],"total_contact_groups":12},"final_pose_error":0.00988,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61578,0.22044,0.21281],"final_tcp_position":[0.60502,0.22048,0.22648],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.5696,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":279.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1112.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52852,-0.01826,0.14771],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12203,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":366.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1464.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53118,-0.02087,0.03506],"tcp_start":[0.52852,-0.01826,0.14771],"tcp_to_object_dist_end":0.01077,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53688,-0.02061,0.02581],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31632,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13562,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10810.0,"raw_peak_contact_force":0.18408,"subtask_id":"grasp_object","tcp_end":[0.52255,-0.02072,0.02522],"tcp_start":[0.53118,-0.02087,0.03506],"tcp_to_object_dist_end":0.01434,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":681.0,"n_steps_budget":1000.0,"object_pos_end":[0.54486,-0.02053,0.20055],"object_pos_start":[0.53688,-0.02061,0.02581],"object_to_goal_dist_end":0.25686,"object_to_goal_dist_start":0.31632,"object_z_max":0.2003,"peak_contact_force":0.08164,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25811.0,"raw_peak_contact_force":0.5696,"subtask_id":"lift_object","tcp_end":[0.5326,-0.02055,0.20637],"tcp_start":[0.52255,-0.02072,0.02522],"tcp_to_object_dist_end":0.01357,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":723.0,"n_steps_budget":1000.0,"object_pos_end":[0.61315,0.21312,0.23286],"object_pos_start":[0.54486,-0.02053,0.20055],"object_to_goal_dist_end":0.0295,"object_to_goal_dist_start":0.25686,"object_z_max":0.23283,"peak_contact_force":0.0937,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26248.0,"raw_peak_contact_force":0.10891,"subtask_id":"approach_goal","tcp_end":[0.60349,0.21317,0.246],"tcp_start":[0.5326,-0.02055,0.20637],"tcp_to_object_dist_end":0.01631,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":70.0,"n_steps_budget":1000.0,"object_pos_end":[0.61578,0.22044,0.21281],"object_pos_start":[0.61315,0.21312,0.23286],"object_to_goal_dist_end":0.01061,"object_to_goal_dist_start":0.0295,"object_z_max":0.23286,"peak_contact_force":0.09502,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2138.0,"raw_peak_contact_force":0.16035,"subtask_id":"place_goal","tcp_end":[0.60502,0.22048,0.22648],"tcp_start":[0.60349,0.21317,0.246],"tcp_to_object_dist_end":0.0174,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15331,"average_solve_count":287.0,"average_success_count":287.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.07059,"approach_object.approach_speed":0.10103,"descend_to_grasp.descend_speed":0.02734,"descend_to_grasp.grasp_offset_z":0.00757,"descend_to_place.descend_place_speed":0.03331,"descend_to_place.place_tolerance":0.02892,"lift.lift_height":0.1851,"lift.lift_speed":0.04482},"optimized_scores":{"best_composite_score":0.45531,"best_fitness_score":0.97531,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":93.0,"contact_point_centroid":[0.5415,-0.02793,-0.00147],"force_p95":0.50568,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53179,"mean_force":0.1784,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52994,-0.02828,0.03239]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10975.0,"contact_point_centroid":[0.53478,-0.00906,0.11387],"force_p95":0.0813,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28251,"mean_force":0.05713,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53402,-0.02818,0.11139]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11747.0,"contact_point_centroid":[0.53447,-0.04723,0.11022],"force_p95":0.07864,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27594,"mean_force":0.05435,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53374,-0.02818,0.10815]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54563,-0.02902,-0.00208],"force_p95":0.14778,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2166,"mean_force":0.12939,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53219,-0.02836,0.03275]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1194.0,"contact_point_centroid":[0.62718,0.13589,0.20652],"force_p95":0.08334,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19821,"mean_force":0.06059,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6245,0.15464,0.20611]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1037.0,"contact_point_centroid":[0.62708,0.17353,0.20768],"force_p95":0.0933,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18464,"mean_force":0.07006,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62446,0.15453,0.20646]},{"body_a":"world","body_b":"grasp_target","contact_count":1244.0,"contact_point_centroid":[0.5456,-0.02923,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51691,-0.01215,0.22451]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4085.0,"contact_point_centroid":[0.53203,-0.00912,0.03402],"force_p95":0.07887,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13554,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53095,-0.02832,0.03131]},{"body_a":"world","body_b":"grasp_target","contact_count":1464.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53624,-0.02679,0.09333]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10645.0,"contact_point_centroid":[0.58175,0.04112,0.20274],"force_p95":0.08472,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09932,"mean_force":0.05693,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58025,0.06012,0.20106]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10738.0,"contact_point_centroid":[0.58309,0.08196,0.20301],"force_p95":0.0824,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09499,"mean_force":0.05589,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58157,0.06299,0.20147]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4944.0,"contact_point_centroid":[0.53198,-0.04743,0.03309],"force_p95":0.07103,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0851,"mean_force":0.04471,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53096,-0.02832,0.03131]}],"total_contact_groups":12},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.63536,0.15853,0.17832],"final_tcp_position":[0.6262,0.15839,0.19545],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.53179,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":312.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1244.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53616,-0.02514,0.14711],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12152,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":366.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1464.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53956,-0.02857,0.04144],"tcp_start":[0.53616,-0.02514,0.14711],"tcp_to_object_dist_end":0.01658,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54549,-0.02831,0.02571],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26045,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14269,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10829.0,"raw_peak_contact_force":0.2166,"subtask_id":"grasp_object","tcp_end":[0.53092,-0.02832,0.03127],"tcp_start":[0.53956,-0.02857,0.04144],"tcp_to_object_dist_end":0.01559,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":607.0,"n_steps_budget":1000.0,"object_pos_end":[0.552,-0.02823,0.18015],"object_pos_start":[0.54549,-0.02831,0.02571],"object_to_goal_dist_end":0.20942,"object_to_goal_dist_start":0.26045,"object_z_max":0.1799,"peak_contact_force":0.08054,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22815.0,"raw_peak_contact_force":0.53179,"subtask_id":"lift_object","tcp_end":[0.54093,-0.02819,0.19148],"tcp_start":[0.53092,-0.02832,0.03127],"tcp_to_object_dist_end":0.01584,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":605.0,"n_steps_budget":1000.0,"object_pos_end":[0.63174,0.15102,0.19921],"object_pos_start":[0.552,-0.02823,0.18015],"object_to_goal_dist_end":0.02629,"object_to_goal_dist_start":0.20942,"object_z_max":0.19918,"peak_contact_force":0.08564,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21383.0,"raw_peak_contact_force":0.09932,"subtask_id":"approach_goal","tcp_end":[0.62362,0.15112,0.21585],"tcp_start":[0.54093,-0.02819,0.19148],"tcp_to_object_dist_end":0.01852,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":74.0,"n_steps_budget":1000.0,"object_pos_end":[0.63536,0.15853,0.17832],"object_pos_start":[0.63174,0.15102,0.19921],"object_to_goal_dist_end":0.00702,"object_to_goal_dist_start":0.02629,"object_z_max":0.19921,"peak_contact_force":0.09389,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2231.0,"raw_peak_contact_force":0.19821,"subtask_id":"place_goal","tcp_end":[0.6262,0.15839,0.19545],"tcp_start":[0.62362,0.15112,0.21585],"tcp_to_object_dist_end":0.01942,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```