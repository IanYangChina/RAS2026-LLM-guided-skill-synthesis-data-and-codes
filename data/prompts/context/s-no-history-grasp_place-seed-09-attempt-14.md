## Search State

- **Seed**: 9
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

## Current Skill (Q=0.396) — your mutation base

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

- **Composite score**: 0.396
- **task_score** (E): 0.850
- **fitness_score**: 0.899  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.670

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1538 |
| descend_1 | 1.00 | 1.00 | 0.1079 |
| grasp_1 | 1.00 | 1.00 | 0.0126 |
| lift_1 | 1.00 | 1.00 | 0.1169 |
| approach_goal | 1.00 | 1.00 | 0.2403 |
| descend_goal | 1.00 | 1.00 | 0.0145 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.015, 0.152) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.510, -0.015, 0.152)→(0.510, -0.016, 0.044) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, -0.016, 0.044)→(0.502, -0.016, 0.035) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 42.000 | 0.136 | 0.176 |
| lift_1 | lift | 1.00 / step_budget | (0.502, -0.016, 0.035)→(0.498, -0.016, 0.152) | (0.515, -0.016, 0.026)→(0.509, -0.016, 0.136) | 0.270→0.233 | 1.00 / 32.333 | 0.089 | 0.543 |
| approach_goal | approach | 1.00 / step_budget | (0.498, -0.016, 0.152)→(0.609, 0.171, 0.239) | (0.509, -0.016, 0.136)→(0.614, 0.171, 0.212) | 0.233→0.046 | 1.00 / 25.000 | 0.109 | 0.188 |
| descend_goal | descend | 1.00 / force_exceeded | (0.609, 0.171, 0.239)→(0.608, 0.172, 0.225) | (0.614, 0.171, 0.212)→(0.612, 0.172, 0.198) | 0.046→0.032 | 1.00 / 28.333 | 59333.249 | 0.261 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.137
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.565
- phase_breakdown.reach_goal_score: 0.429
- phase_breakdown.lift_clearance_score: 0.316
- phase_breakdown.reach_object_score: 0.956
- grasp_place_fitness: 0.979

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.979
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.394
- **K-run variance**: 0.0042
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.347


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.8693,"average_solve_count":329.0,"average_success_count":329.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.14731,"approach_1.speed":0.12541,"approach_goal.goal_approach_z":0.09976,"approach_goal.speed":0.03562,"descend_1.descend_z":0.0016,"descend_1.speed":0.02515,"descend_goal.contact_force_threshold":5.62596,"descend_goal.goal_z_offset":-0.00626,"descend_goal.speed":0.06844,"lift_1.lift_height":0.14295,"lift_1.speed":0.05569},"optimized_scores":{"best_composite_score":0.3937,"best_fitness_score":0.89703,"best_task_score":0.84233},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":111.0,"contact_point_centroid":[0.5331,-0.02025,-0.0013],"force_p95":0.49399,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60027,"mean_force":0.11828,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52128,-0.02067,0.03244]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13063.0,"contact_point_centroid":[0.51954,-0.00151,0.09834],"force_p95":0.0801,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32264,"mean_force":0.05678,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51849,-0.02061,0.09598]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13762.0,"contact_point_centroid":[0.51956,-0.03965,0.09599],"force_p95":0.07818,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30588,"mean_force":0.05455,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51851,-0.02061,0.09396]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2778.0,"contact_point_centroid":[0.60566,0.23651,0.27177],"force_p95":0.08777,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19202,"mean_force":0.05842,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.60365,0.21762,0.27145]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2664.0,"contact_point_centroid":[0.60564,0.19857,0.27168],"force_p95":0.09056,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19179,"mean_force":0.05965,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.60365,0.21767,0.27068]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02114,-0.00206],"force_p95":0.14021,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1824,"mean_force":0.12743,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52389,-0.02072,0.03253]},{"body_a":"world","body_b":"grasp_target","contact_count":1116.0,"contact_point_centroid":[0.53702,-0.02132,-0.00188],"force_p95":0.13645,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51311,-0.00879,0.24485]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4098.0,"contact_point_centroid":[0.52363,-0.00149,0.03386],"force_p95":0.07764,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12394,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52266,-0.0207,0.03114]},{"body_a":"world","body_b":"grasp_target","contact_count":1500.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52853,-0.01946,0.11557]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16990.0,"contact_point_centroid":[0.56115,0.07681,0.22329],"force_p95":0.08227,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09689,"mean_force":0.0568,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55899,0.09566,0.22227]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15387.0,"contact_point_centroid":[0.56289,0.11913,0.22619],"force_p95":0.08959,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09599,"mean_force":0.0622,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56067,0.10014,0.22486]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4916.0,"contact_point_centroid":[0.52361,-0.03979,0.03293],"force_p95":0.06971,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0839,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52267,-0.0207,0.03115]}],"total_contact_groups":12},"final_pose_error":0.05157,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.60496,0.21871,0.23091],"final_tcp_position":[0.60393,0.21923,0.25162],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":287.71107,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":280.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1116.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52847,-0.01819,0.18889],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":375.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1500.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53134,-0.02084,0.04121],"tcp_start":[0.52847,-0.01819,0.18889],"tcp_to_object_dist_end":0.01623,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5369,-0.02063,0.02579],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31634,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13658,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10814.0,"raw_peak_contact_force":0.1824,"tcp_end":[0.52264,-0.02069,0.03111],"tcp_start":[0.53134,-0.02084,0.04121],"tcp_to_object_dist_end":0.01523,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":725.0,"n_steps_budget":1000.0,"object_pos_end":[0.52922,-0.02061,0.14712],"object_pos_start":[0.5369,-0.02063,0.02579],"object_to_goal_dist_end":0.26814,"object_to_goal_dist_start":0.31634,"object_z_max":0.14697,"peak_contact_force":0.08038,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26936.0,"raw_peak_contact_force":0.60027,"subtask_id":"lift_clearance","tcp_end":[0.51876,-0.0206,0.15962],"tcp_start":[0.52264,-0.02069,0.03111],"tcp_to_object_dist_end":0.0163,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":994.0,"n_steps_budget":1000.0,"object_pos_end":[0.61055,0.21614,0.27239],"object_pos_start":[0.52922,-0.02061,0.14712],"object_to_goal_dist_end":0.066,"object_to_goal_dist_start":0.26814,"object_z_max":0.27228,"peak_contact_force":0.08185,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32377.0,"raw_peak_contact_force":0.09689,"subtask_id":"reach_goal","tcp_end":[0.60439,0.21625,0.29214],"tcp_start":[0.51876,-0.0206,0.15962],"tcp_to_object_dist_end":0.02069,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":154.0,"n_steps_budget":1000.0,"object_pos_end":[0.60496,0.21871,0.23091],"object_pos_start":[0.61055,0.21614,0.27239],"object_to_goal_dist_end":0.02574,"object_to_goal_dist_start":0.066,"object_z_max":0.27239,"peak_contact_force":287.71107,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5442.0,"raw_peak_contact_force":0.19202,"subtask_id":"reach_goal","tcp_end":[0.60393,0.21923,0.25162],"tcp_start":[0.60439,0.21625,0.29214],"tcp_to_object_dist_end":0.02075,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57516,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.09322,"approach_1.speed":0.15033,"approach_goal.goal_approach_z":0.09985,"approach_goal.speed":0.20081,"descend_1.descend_z":0.01161,"descend_1.speed":0.06126,"descend_goal.contact_force_threshold":4.44567,"descend_goal.goal_z_offset":-0.1235,"descend_goal.speed":0.11472,"lift_1.lift_height":0.14453,"lift_1.speed":0.04455},"optimized_scores":{"best_composite_score":0.31754,"best_fitness_score":0.82087,"best_task_score":0.70707},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":117.0,"contact_point_centroid":[0.54089,-0.02778,-0.00137],"force_p95":0.41485,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43708,"mean_force":0.11951,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52937,-0.02818,0.04187]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":31.0,"contact_point_centroid":[0.62872,0.17219,0.25847],"force_p95":0.28613,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29535,"mean_force":0.16753,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62465,0.15391,0.26238]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13660.0,"contact_point_centroid":[0.52756,-0.00897,0.10864],"force_p95":0.08157,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2787,"mean_force":0.05691,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52662,-0.02808,0.10623]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14515.0,"contact_point_centroid":[0.52756,-0.04712,0.10599],"force_p95":0.07883,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27075,"mean_force":0.05452,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52663,-0.02808,0.10396]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":32.0,"contact_point_centroid":[0.62877,0.13604,0.25857],"force_p95":0.23582,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25604,"mean_force":0.13409,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.62465,0.15392,0.26238]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7799.0,"contact_point_centroid":[0.57416,0.07443,0.21048],"force_p95":0.12474,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2487,"mean_force":0.07941,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5705,0.0557,0.2107]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8495.0,"contact_point_centroid":[0.574,0.03714,0.21063],"force_p95":0.12119,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2154,"mean_force":0.07332,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57054,0.05577,0.21073]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54563,-0.02906,-0.00209],"force_p95":0.14841,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20527,"mean_force":0.12958,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53198,-0.02826,0.04206]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4094.0,"contact_point_centroid":[0.5319,-0.00901,0.04333],"force_p95":0.07904,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13855,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53076,-0.02822,0.04062]},{"body_a":"world","body_b":"grasp_target","contact_count":1572.0,"contact_point_centroid":[0.5456,-0.02923,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12294,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51738,-0.01276,0.21773]},{"body_a":"world","body_b":"grasp_target","contact_count":820.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53713,-0.02724,0.09334]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4947.0,"contact_point_centroid":[0.53185,-0.04733,0.04239],"force_p95":0.0713,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07567,"mean_force":0.04459,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53076,-0.02822,0.04063]}],"total_contact_groups":12},"final_pose_error":0.20921,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.62981,0.15464,0.2278],"final_tcp_position":[0.62456,0.15417,0.26218],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":394.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1572.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53716,-0.02613,0.13514],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":205.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":820.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5394,-0.02847,0.05102],"tcp_start":[0.53716,-0.02613,0.13514],"tcp_to_object_dist_end":0.02578,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54553,-0.02833,0.02568],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26047,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14382,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10841.0,"raw_peak_contact_force":0.20527,"tcp_end":[0.53073,-0.02822,0.04059],"tcp_start":[0.5394,-0.02847,0.05102],"tcp_to_object_dist_end":0.021,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":761.0,"n_steps_budget":1000.0,"object_pos_end":[0.53466,-0.02808,0.14963],"object_pos_start":[0.54553,-0.02833,0.02568],"object_to_goal_dist_end":0.21826,"object_to_goal_dist_start":0.26047,"object_z_max":0.14947,"peak_contact_force":0.07846,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28292.0,"raw_peak_contact_force":0.43708,"subtask_id":"lift_clearance","tcp_end":[0.52692,-0.02808,0.17074],"tcp_start":[0.53073,-0.02822,0.04059],"tcp_to_object_dist_end":0.02249,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":628.0,"n_steps_budget":1000.0,"object_pos_end":[0.62954,0.1539,0.22804],"object_pos_start":[0.53466,-0.02808,0.14963],"object_to_goal_dist_end":0.0524,"object_to_goal_dist_start":0.21826,"object_z_max":0.22796,"peak_contact_force":0.13469,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16294.0,"raw_peak_contact_force":0.2487,"subtask_id":"reach_goal","tcp_end":[0.62469,0.15372,0.26242],"tcp_start":[0.52692,-0.02808,0.17074],"tcp_to_object_dist_end":0.03471,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.62981,0.15464,0.2278],"object_pos_start":[0.62954,0.1539,0.22804],"object_to_goal_dist_end":0.05199,"object_to_goal_dist_start":0.0524,"object_z_max":0.22804,"peak_contact_force":167951.73011,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":63.0,"raw_peak_contact_force":0.29535,"subtask_id":"reach_goal","tcp_end":[0.62456,0.15417,0.26218],"tcp_start":[0.62469,0.15372,0.26242],"tcp_to_object_dist_end":0.03479,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.11404,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_z":0.08756,"approach_1.speed":0.09335,"approach_goal.goal_approach_z":0.0518,"approach_goal.speed":0.16655,"descend_1.descend_z":8e-05,"descend_1.speed":0.12525,"descend_goal.contact_force_threshold":3.6599,"descend_goal.goal_z_offset":-0.04544,"descend_goal.speed":0.10927,"lift_1.lift_height":0.1061,"lift_1.speed":0.13542},"optimized_scores":{"best_composite_score":0.47537,"best_fitness_score":0.97871,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.46025,1e-05,-0.00129],"force_p95":0.56879,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5916,"mean_force":0.10834,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45016,-0.00023,0.03407]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5965.0,"contact_point_centroid":[0.44954,0.01883,0.07664],"force_p95":0.10549,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32743,"mean_force":0.0667,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44776,-0.00024,0.07429]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":156.0,"contact_point_centroid":[0.60007,0.12426,0.1618],"force_p95":0.17,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29655,"mean_force":0.09559,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.59684,0.14312,0.16255]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6773.0,"contact_point_centroid":[0.4495,-0.01913,0.07451],"force_p95":0.1007,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2871,"mean_force":0.0599,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44779,-0.00024,0.07282]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":180.0,"contact_point_centroid":[0.59919,0.16177,0.16154],"force_p95":0.16268,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23222,"mean_force":0.09742,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.59685,0.1431,0.16262]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7096.0,"contact_point_centroid":[0.53217,0.05922,0.1456],"force_p95":0.11987,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21932,"mean_force":0.08477,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52833,0.0781,0.14454]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8546.0,"contact_point_centroid":[0.53201,0.09621,0.14546],"force_p95":0.10276,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17309,"mean_force":0.06899,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52791,0.07773,0.1444]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46284,-4e-05,-0.00202],"force_p95":0.12814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14079,"mean_force":0.12431,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45236,-0.0002,0.03378]},{"body_a":"world","body_b":"grasp_target","contact_count":1564.0,"contact_point_centroid":[0.46286,-7e-05,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12294,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48149,-5e-05,0.217]},{"body_a":"world","body_b":"grasp_target","contact_count":880.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46029,-0.0001,0.08643]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4389.0,"contact_point_centroid":[0.45122,0.01909,0.03496],"force_p95":0.07393,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09416,"mean_force":0.04934,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45129,-0.00021,0.03276]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5332.0,"contact_point_centroid":[0.45074,-0.01929,0.03446],"force_p95":0.06278,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08675,"mean_force":0.04088,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.45129,-0.00021,0.03276]}],"total_contact_groups":12},"final_pose_error":0.08594,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.60122,0.14382,0.13386],"final_tcp_position":[0.59665,0.1433,0.16109],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":9760.30694,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":392.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1564.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46345,-8e-05,0.13215],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10614,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":880.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45903,-0.00012,0.04032],"tcp_start":[0.46345,-8e-05,0.13215],"tcp_to_object_dist_end":0.01481,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46274,-1e-05,0.02592],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23317,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12824,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11521.0,"raw_peak_contact_force":0.14079,"tcp_end":[0.45126,-0.00021,0.03273],"tcp_start":[0.45903,-0.00012,0.04032],"tcp_to_object_dist_end":0.01335,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":384.0,"n_steps_budget":600.0,"object_pos_end":[0.46451,-0.00013,0.11113],"object_pos_start":[0.46274,-1e-05,0.02592],"object_to_goal_dist_end":0.21153,"object_to_goal_dist_start":0.23317,"object_z_max":0.11096,"peak_contact_force":0.10742,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12822.0,"raw_peak_contact_force":0.5916,"subtask_id":"lift_clearance","tcp_end":[0.44755,-0.00023,0.12447],"tcp_start":[0.45126,-0.00021,0.03273],"tcp_to_object_dist_end":0.02158,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":581.0,"n_steps_budget":1000.0,"object_pos_end":[0.60081,0.14296,0.13642],"object_pos_start":[0.46451,-0.00013,0.11113],"object_to_goal_dist_end":0.0197,"object_to_goal_dist_start":0.21153,"object_z_max":0.13638,"peak_contact_force":0.11086,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15642.0,"raw_peak_contact_force":0.21932,"subtask_id":"reach_goal","tcp_end":[0.59684,0.1427,0.16338],"tcp_start":[0.44755,-0.00023,0.12447],"tcp_to_object_dist_end":0.02725,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":12.0,"n_steps_budget":1000.0,"object_pos_end":[0.60122,0.14382,0.13386],"object_pos_start":[0.60081,0.14296,0.13642],"object_to_goal_dist_end":0.01726,"object_to_goal_dist_start":0.0197,"object_z_max":0.13642,"peak_contact_force":9760.30694,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":336.0,"raw_peak_contact_force":0.29655,"subtask_id":"reach_goal","tcp_end":[0.59665,0.1433,0.16109],"tcp_start":[0.59684,0.1427,0.16338],"tcp_to_object_dist_end":0.02761,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```