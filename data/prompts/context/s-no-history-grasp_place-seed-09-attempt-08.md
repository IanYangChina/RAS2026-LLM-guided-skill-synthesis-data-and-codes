## Search State

- **Seed**: 9
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
- Frozen realised-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`
- Frozen object start: [0.5370249203970084, -0.021318279091244466, 0.03]
- Frozen task target: [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]
- Goal object position: (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6103148150051562, 0.2277534082920179, 0.2074111944405348)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5370249203970084, -0.021318279091244466, 0.03)
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
  frozen_object_start: [0.537, -0.0213, 0.03]
  frozen_task_target: [0.6103, 0.2278, 0.2074]
  frozen_object_starts: {'grasp_target': [0.5370249203970084, -0.021318279091244466, 0.03]}
  frozen_targets: {'place_target': [0.6103148150051562, 0.2277534082920179, 0.2074111944405348]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8

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
| `object` | offset from object initial position (0.5370249203970084, -0.021318279091244466, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6103148150051562, 0.2277534082920179, 0.2074111944405348) | final destination targets |
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

## Current Skill (Q=-0.296) — your mutation base

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
  weight: 0.3
- id: lift_clearance
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: reach_goal
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
    - 0.1
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    approach_z:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_object
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
    - 0.02
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    descend_z:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
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
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: lift_clearance
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    goal_approach_z:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_goal
- id: descend_goal
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
    - 0.03
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    goal_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: grasp_held
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=1, strategy=offset_target, offset=[0.005, 0.0, 0.0]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.12], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - goal_approach_z: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - goal_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=grasp_held, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=1, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: -0.296
- **task_score** (E): 0.307
- **fitness_score**: 0.624  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.920

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1586 |
| descend_1 | 1.00 | 1.00 | 0.0986 |
| grasp_1 | 1.00 | 1.00 | 0.0120 |
| lift_1 | 1.00 | 1.00 | 0.1042 |
| approach_goal | 1.00 | 1.00 | 0.1410 |
| descend_goal | 1.00 | 1.00 | 0.0702 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.506, -0.013, 0.147) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / time_limit | (0.506, -0.013, 0.147)→(0.510, -0.017, 0.048) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, -0.017, 0.048)→(0.502, -0.017, 0.039) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 41.667 | 0.132 | 0.162 |
| lift_1 | lift | 1.00 / time_limit | (0.502, -0.017, 0.039)→(0.498, -0.017, 0.143) | (0.515, -0.016, 0.026)→(0.508, -0.016, 0.122) | 0.270→0.239 | 1.00 / 28.333 | 0.100 | 0.487 |
| approach_goal | approach | 1.00 / time_limit | (0.498, -0.017, 0.143)→(0.562, 0.082, 0.207) | (0.508, -0.016, 0.122)→(0.568, 0.078, 0.056) | 0.239→0.175 | 1.00 / 9.333 | 0.108 | 1.200 |
| descend_goal | descend | 1.00 / time_limit | (0.562, 0.082, 0.207)→(0.593, 0.138, 0.187) | (0.568, 0.078, 0.056)→(0.574, 0.086, 0.016) | 0.175→0.189 | 1.00 / 8.000 | 6499.232 | 0.587 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.475
- phase_score: 0.595
- phase_breakdown.reach_goal_score: 0.496
- phase_breakdown.lift_clearance_score: 0.589
- phase_breakdown.reach_object_score: 0.763
- grasp_place_fitness: 0.708

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.708
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.475
- **Median Q (composite search score)**: -0.322
- **K-run variance**: 0.0037
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.270


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `425c48e82220fc6e1b680086671cf7dd2586733ee271dec2149f96a25d69d0c6`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `58e88c03db0a62276863b22a53636bc89fead3e4bc7f4d35fd72d2282ace32bf`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.808,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.1057,"approach_1.phase_time":5.23809,"approach_1.speed":0.09645,"approach_goal.goal_approach_z":0.16588,"approach_goal.phase_time":5.78687,"approach_goal.speed":0.15831,"descend_1.descend_z":0.02273,"descend_1.phase_time":6.20761,"descend_1.speed":0.12057,"descend_goal.goal_z_offset":0.03488,"descend_goal.phase_time":8.1629,"descend_goal.speed":0.0802,"grasp_1.phase_time":6.07849,"lift_1.lift_height":0.1445,"lift_1.phase_time":5.13374,"lift_1.speed":0.06187},"optimized_scores":{"best_composite_score":-0.3532,"best_fitness_score":0.5668,"best_task_score":0.18754},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":163.0,"contact_point_centroid":[0.56109,0.07305,-0.0081],"force_p95":1.27076,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.71672,"mean_force":0.43294,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54716,0.06466,0.20838]},{"body_a":"world","body_b":"grasp_target","contact_count":368.0,"contact_point_centroid":[0.53228,-0.0208,-0.00145],"force_p95":0.26656,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52668,"mean_force":0.10594,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52067,-0.02089,0.03726]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17984.0,"contact_point_centroid":[0.51995,-0.00174,0.08252],"force_p95":0.08195,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31667,"mean_force":0.05645,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51901,-0.02085,0.08013]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19236.0,"contact_point_centroid":[0.51994,-0.03988,0.08146],"force_p95":0.07775,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29855,"mean_force":0.05334,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51902,-0.02085,0.07947]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11458.0,"contact_point_centroid":[0.53144,0.02992,0.15755],"force_p95":0.12351,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25675,"mean_force":0.07127,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5273,0.01134,0.15717]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10430.0,"contact_point_centroid":[0.53066,-0.00873,0.15667],"force_p95":0.13926,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23072,"mean_force":0.07814,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52685,0.01001,0.15596]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.0212,-0.00204],"force_p95":0.1348,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16355,"mean_force":0.12606,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5247,-0.02097,0.03787]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.53702,-0.02132,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51439,-0.01016,0.21632]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.56115,0.07288,-0.00201],"force_p95":0.12289,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12476,"mean_force":0.12114,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.55713,0.09832,0.2101]},{"body_a":"world","body_b":"grasp_target","contact_count":3556.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52811,-0.01953,0.0922]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4112.0,"contact_point_centroid":[0.52414,-0.00174,0.03919],"force_p95":0.07657,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12255,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52347,-0.02095,0.03645]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4888.0,"contact_point_centroid":[0.52418,-0.04002,0.03827],"force_p95":0.06886,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08992,"mean_force":0.04471,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52347,-0.02095,0.03645]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4221.0,"contact_point_centroid":[0.55778,0.09884,0.21243],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01584,"mean_force":0.01047,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.55728,0.09883,0.21011]}],"total_contact_groups":13},"final_pose_error":0.11049,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.56115,0.07288,0.01602],"final_tcp_position":[0.56893,0.12888,0.21546],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.71672,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52664,-0.01749,0.15878],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13322,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":889.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3556.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53168,-0.02111,0.04599],"tcp_start":[0.52664,-0.01749,0.15878],"tcp_to_object_dist_end":0.02068,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53691,-0.02085,0.02584],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31648,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13243,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10800.0,"raw_peak_contact_force":0.16355,"tcp_end":[0.52344,-0.02095,0.03641],"tcp_start":[0.53168,-0.02111,0.04599],"tcp_to_object_dist_end":0.01712,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52822,-0.02069,0.11315],"object_pos_start":[0.53691,-0.02085,0.02584],"object_to_goal_dist_end":0.27812,"object_to_goal_dist_start":0.31648,"object_z_max":0.11304,"peak_contact_force":0.09323,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37588.0,"raw_peak_contact_force":0.52668,"subtask_id":"lift_clearance","tcp_end":[0.51917,-0.02085,0.13144],"tcp_start":[0.52344,-0.02095,0.03641],"tcp_to_object_dist_end":0.02041,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56142,0.07323,0.00995],"object_pos_start":[0.52822,-0.02069,0.11315],"object_to_goal_dist_end":0.25546,"object_to_goal_dist_start":0.27812,"object_z_max":0.17159,"peak_contact_force":0.07464,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22051.0,"raw_peak_contact_force":1.71672,"subtask_id":"reach_goal","tcp_end":[0.54797,0.06675,0.21039],"tcp_start":[0.51917,-0.02085,0.13144],"tcp_to_object_dist_end":0.20099,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56115,0.07288,0.01602],"object_pos_start":[0.56142,0.07323,0.00995],"object_to_goal_dist_end":0.25107,"object_to_goal_dist_start":0.25546,"object_z_max":0.01662,"peak_contact_force":0.12263,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8221.0,"raw_peak_contact_force":0.12476,"subtask_id":"reach_goal","tcp_end":[0.56893,0.12888,0.21546],"tcp_start":[0.54797,0.06675,0.21039],"tcp_to_object_dist_end":0.2073,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86325,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.10327,"approach_1.phase_time":5.35238,"approach_1.speed":0.12977,"approach_goal.goal_approach_z":0.14787,"approach_goal.phase_time":4.22645,"approach_goal.speed":0.19153,"descend_1.descend_z":0.02769,"descend_1.phase_time":9.45801,"descend_1.speed":0.11958,"descend_goal.goal_z_offset":0.02671,"descend_goal.phase_time":4.58312,"descend_goal.speed":0.10443,"grasp_1.phase_time":3.77693,"lift_1.lift_height":0.14104,"lift_1.phase_time":6.99045,"lift_1.speed":0.06463},"optimized_scores":{"best_composite_score":-0.32249,"best_fitness_score":0.59751,"best_task_score":0.25843},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1165.0,"contact_point_centroid":[0.57878,0.05362,-0.00284],"force_p95":0.44857,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.6671,"mean_force":0.16014,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57117,0.05734,0.21538]},{"body_a":"world","body_b":"grasp_target","contact_count":359.0,"contact_point_centroid":[0.54125,-0.02844,-0.00145],"force_p95":0.22812,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48332,"mean_force":0.10152,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52911,-0.02853,0.04177]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17364.0,"contact_point_centroid":[0.52873,-0.00941,0.08848],"force_p95":0.0851,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.317,"mean_force":0.05845,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52741,-0.02847,0.08637]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18526.0,"contact_point_centroid":[0.52868,-0.04746,0.08623],"force_p95":0.08299,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30061,"mean_force":0.0556,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52742,-0.02847,0.08449]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7804.0,"contact_point_centroid":[0.5444,0.0175,0.16141],"force_p95":0.10891,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28302,"mean_force":0.07498,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53902,-0.00096,0.16068]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6923.0,"contact_point_centroid":[0.54263,-0.02196,0.15957],"force_p95":0.14389,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28237,"mean_force":0.08374,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53779,-0.00326,0.15858]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54561,-0.0291,-0.00206],"force_p95":0.13996,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18099,"mean_force":0.12742,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53312,-0.02866,0.04236]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.5456,-0.02923,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51669,-0.01277,0.22173]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4106.0,"contact_point_centroid":[0.53262,-0.00941,0.04364],"force_p95":0.07771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13092,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53189,-0.02862,0.0409]},{"body_a":"world","body_b":"grasp_target","contact_count":3788.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53492,-0.02609,0.09857]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5788,0.05364,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.59864,0.11058,0.21129]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4905.0,"contact_point_centroid":[0.53264,-0.0477,0.0427],"force_p95":0.06986,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08683,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53189,-0.02862,0.0409]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1002.0,"contact_point_centroid":[0.57323,0.06025,0.22043],"force_p95":0.0125,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01607,"mean_force":0.01071,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57279,0.06025,0.21813]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4315.0,"contact_point_centroid":[0.59907,0.11051,0.21357],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01269,"mean_force":0.01034,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.59859,0.1105,0.21131]}],"total_contact_groups":14},"final_pose_error":0.02244,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.5788,0.05364,0.01602],"final_tcp_position":[0.6196,0.14723,0.19973],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":9748.71401,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53163,-0.02263,0.16438],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13922,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":947.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3788.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54013,-0.02888,0.05077],"tcp_start":[0.53163,-0.02263,0.16438],"tcp_to_object_dist_end":0.02535,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54551,-0.02861,0.02578],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26063,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13685,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10811.0,"raw_peak_contact_force":0.18099,"tcp_end":[0.53186,-0.02862,0.04086],"tcp_start":[0.54013,-0.02888,0.05077],"tcp_to_object_dist_end":0.02034,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53656,-0.02834,0.11735],"object_pos_start":[0.54551,-0.02861,0.02578],"object_to_goal_dist_end":0.22399,"object_to_goal_dist_start":0.26063,"object_z_max":0.11724,"peak_contact_force":0.0994,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36249.0,"raw_peak_contact_force":0.48332,"subtask_id":"lift_clearance","tcp_end":[0.52761,-0.02847,0.14014],"tcp_start":[0.53186,-0.02862,0.04086],"tcp_to_object_dist_end":0.02449,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5788,0.05364,0.01602],"object_pos_start":[0.53656,-0.02834,0.11735],"object_to_goal_dist_end":0.20297,"object_to_goal_dist_start":0.22399,"object_z_max":0.16268,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16894.0,"raw_peak_contact_force":1.6671,"subtask_id":"reach_goal","tcp_end":[0.57972,0.07271,0.22986],"tcp_start":[0.52761,-0.02847,0.14014],"tcp_to_object_dist_end":0.21469,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5788,0.05364,0.01602],"object_pos_start":[0.5788,0.05364,0.01602],"object_to_goal_dist_end":0.20297,"object_to_goal_dist_start":0.20297,"object_z_max":0.01602,"peak_contact_force":9748.71401,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8315.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.6196,0.14723,0.19973],"tcp_start":[0.57972,0.07271,0.22986],"tcp_to_object_dist_end":0.21018,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`; realized-scene SHA-256: `776f3cbcac69f75f44cb26f0b1a492bbf1ced59f3c5fca79400c3f557c2ce565`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46286,-7e-05,0.03]},{"name":"goal","value":[0.61015,0.15287,0.12219]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.46286,-7e-05,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61015,0.15287,0.12219]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90244,"average_solve_count":123.0,"average_success_count":123.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.08212,"approach_1.phase_time":3.80655,"approach_1.speed":0.11348,"approach_goal.goal_approach_z":0.07714,"approach_goal.phase_time":5.35953,"approach_goal.speed":0.20188,"descend_1.descend_z":0.02005,"descend_1.phase_time":5.3342,"descend_1.speed":0.13062,"descend_goal.goal_z_offset":0.02035,"descend_goal.phase_time":6.07943,"descend_goal.speed":0.06202,"grasp_1.phase_time":9.44822,"lift_1.lift_height":0.1285,"lift_1.phase_time":3.97674,"lift_1.speed":0.09047},"optimized_scores":{"best_composite_score":-0.21236,"best_fitness_score":0.70764,"best_task_score":0.47467},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3478.0,"contact_point_centroid":[0.5825,0.13142,-0.00225],"force_p95":0.12872,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.51418,"mean_force":0.13601,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.57571,0.12505,0.15764]},{"body_a":"world","body_b":"grasp_target","contact_count":210.0,"contact_point_centroid":[0.45972,1e-05,-0.00115],"force_p95":0.22787,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45098,"mean_force":0.07061,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4491,-0.00022,0.04229]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12908.0,"contact_point_centroid":[0.44926,0.01872,0.09403],"force_p95":0.10113,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30036,"mean_force":0.06555,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44699,-0.00023,0.09198]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13817.0,"contact_point_centroid":[0.44918,-0.01908,0.09104],"force_p95":0.09926,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27184,"mean_force":0.06189,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44701,-0.00023,0.08942]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":404.0,"contact_point_centroid":[0.56561,0.09065,0.17234],"force_p95":0.16452,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25625,"mean_force":0.12226,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.55922,0.10869,0.17715]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9754.0,"contact_point_centroid":[0.5017,0.02984,0.16639],"force_p95":0.13571,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21522,"mean_force":0.0943,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.4958,0.04834,0.16652]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":511.0,"contact_point_centroid":[0.56506,0.12654,0.17162],"force_p95":0.13527,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20749,"mean_force":0.09236,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.5593,0.10897,0.17631]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10886.0,"contact_point_centroid":[0.50151,0.06631,0.16613],"force_p95":0.13392,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19973,"mean_force":0.08472,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.4954,0.048,0.16641]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46285,-4e-05,-0.00202],"force_p95":0.12805,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14255,"mean_force":0.12435,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45196,-0.00019,0.04176]},{"body_a":"world","body_b":"grasp_target","contact_count":3120.0,"contact_point_centroid":[0.46286,-7e-05,-0.00195],"force_p95":0.12744,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4793,-5e-05,0.20689]},{"body_a":"world","body_b":"grasp_target","contact_count":1628.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45801,-0.00011,0.08038]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4389.0,"contact_point_centroid":[0.45091,0.01907,0.04313],"force_p95":0.07357,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09431,"mean_force":0.04927,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45088,-0.0002,0.04071]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5091.0,"contact_point_centroid":[0.45079,-0.01928,0.04269],"force_p95":0.06445,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08836,"mean_force":0.04273,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45088,-0.0002,0.04071]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3425.0,"contact_point_centroid":[0.57721,0.12603,0.15899],"force_p95":0.01108,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01498,"mean_force":0.01051,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.5768,0.12602,0.15677]}],"total_contact_groups":14},"final_pose_error":0.02551,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.58256,0.13144,0.01602],"final_tcp_position":[0.59003,0.13771,0.14653],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":9748.86065,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":781.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3120.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46069,-9e-05,0.11662],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09063,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":407.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1628.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45823,-0.00012,0.04788],"tcp_start":[0.46069,-9e-05,0.11662],"tcp_to_object_dist_end":0.02235,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46276,-2e-05,0.02592],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23316,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12809,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11280.0,"raw_peak_contact_force":0.14255,"tcp_end":[0.45085,-0.0002,0.04068],"tcp_start":[0.45823,-0.00012,0.04788],"tcp_to_object_dist_end":0.01897,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":842.0,"n_steps_budget":900.0,"object_pos_end":[0.4594,-0.00013,0.13584],"object_pos_start":[0.46276,-2e-05,0.02592],"object_to_goal_dist_end":0.21522,"object_to_goal_dist_start":0.23316,"object_z_max":0.13574,"peak_contact_force":0.10883,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26935.0,"raw_peak_contact_force":0.45098,"subtask_id":"lift_clearance","tcp_end":[0.44718,-0.00022,0.15869],"tcp_start":[0.45085,-0.0002,0.04068],"tcp_to_object_dist_end":0.02592,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56472,0.10797,0.14338],"object_pos_start":[0.4594,-0.00013,0.13584],"object_to_goal_dist_end":0.06729,"object_to_goal_dist_start":0.21522,"object_z_max":0.14337,"peak_contact_force":0.12576,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20640.0,"raw_peak_contact_force":0.21522,"subtask_id":"reach_goal","tcp_end":[0.55885,0.10745,0.18056],"tcp_start":[0.44718,-0.00022,0.15869],"tcp_to_object_dist_end":0.03765,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58256,0.13144,0.01602],"object_pos_start":[0.56472,0.10797,0.14338],"object_to_goal_dist_end":0.11177,"object_to_goal_dist_start":0.06729,"object_z_max":0.14338,"peak_contact_force":9748.86065,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7818.0,"raw_peak_contact_force":1.51418,"subtask_id":"reach_goal","tcp_end":[0.59003,0.13771,0.14653],"tcp_start":[0.55885,0.10745,0.18056],"tcp_to_object_dist_end":0.13088,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```