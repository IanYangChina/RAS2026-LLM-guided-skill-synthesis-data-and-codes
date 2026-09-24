## Search State

- **Seed**: 1
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
- Frozen realised-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`
- Frozen object start: [0.5011821624700257, 0.045046369632593536, 0.03]
- Frozen task target: [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]
- Goal object position: (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5011821624700257, 0.045046369632593536, 0.03)
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
  frozen_object_start: [0.5012, 0.045, 0.03]
  frozen_task_target: [0.5644, 0.2449, 0.1468]
  frozen_object_starts: {'grasp_target': [0.5011821624700257, 0.045046369632593536, 0.03]}
  frozen_targets: {'place_target': [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.934, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5011821624700257, 0.045046369632593536, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5644159612719634, 0.2448649447137244, 0.1467747178015728) | final destination targets |
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

## Current Skill (Q=0.162) — your mutation base

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
- id: grasp_point
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.2
- id: object_lifted
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: near_goal
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.2
- id: placed_at_goal
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
    - 0.12
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_above_object
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
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    grasp_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
  subtask_id: grasp_point
- id: grasp
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
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
    grasp_retry_offset_x:
      type: scalar
      range:
      - -0.005
      - 0.005
      default: 0.0
      binds_to:
      - path: retry.offset.x
        mode: add
    grasp_retry_offset_y:
      type: scalar
      range:
      - -0.005
      - 0.005
      default: 0.0
      binds_to:
      - path: retry.offset.y
        mode: add
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.8
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: grasp_point
- id: lift_object
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_z
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    lift_distance:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: object_lifted
- id: transport_to_goal
  type: approach
  generator: linear_cartesian
  control: impedance_control
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
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: near_goal
- id: place_at_goal
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    place_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    place_offset_z:
      type: scalar
      range:
      - 0.02
      - 0.07
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: add
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: placed_at_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.12], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_offset_x: status=consumed; consumers=target.offset.x (add)
    - grasp_offset_y: status=consumed; consumers=target.offset.y (add)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03]
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_retry_offset_x: status=consumed; consumers=retry.offset.x (add)
    - grasp_retry_offset_y: status=consumed; consumers=retry.offset.y (add)
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.8
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=replace_offset_projection, sign=positive}, tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **place_at_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_offset_x: status=consumed; consumers=target.offset.x (add)
    - place_offset_y: status=consumed; consumers=target.offset.y (add)
    - place_offset_z: status=consumed; consumers=target.offset.z (add)
    - place_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.162
- **task_score** (E): 0.934
- **fitness_score**: 0.932  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.770

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1532 |
| descend_to_grasp | 1.00 | 1.00 | 0.0989 |
| grasp | 1.00 | 1.00 | 0.0108 |
| lift_object | 1.00 | 1.00 | 0.1279 |
| transport_to_goal | 1.00 | 1.00 | 0.2445 |
| place_at_goal | 1.00 | 0.67 | 0.0535 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.476, -0.000, 0.153) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.476, -0.000, 0.153)→(0.478, 0.000, 0.055) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.478, 0.000, 0.055)→(0.470, 0.000, 0.047) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.025) | 0.278→0.278 | 1.00 / 43.000 | 0.161 | 0.209 |
| lift_object | lift | 1.00 / step_budget | (0.470, 0.000, 0.047)→(0.467, -0.000, 0.175) | (0.479, -0.000, 0.025)→(0.471, -0.000, 0.149) | 0.278→0.250 | 1.00 / 32.333 | 0.090 | 0.403 |
| transport_to_goal | approach | 1.00 / step_budget | (0.467, -0.000, 0.175)→(0.599, 0.192, 0.238) | (0.471, -0.000, 0.149)→(0.604, 0.192, 0.206) | 0.250→0.058 | 1.00 / 26.333 | 0.103 | 0.189 |
| place_at_goal | descend | 1.00 / step_budget | (0.599, 0.192, 0.238)→(0.604, 0.207, 0.188) | (0.604, 0.192, 0.206)→(0.610, 0.205, 0.144) | 0.058→0.020 | 0.67 / 19.333 | 0.068 | 0.238 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.391
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.696
- phase_breakdown.near_goal_score: 0.671
- phase_breakdown.reach_above_object_score: 0.906
- phase_breakdown.object_lifted_score: 0.702
- phase_breakdown.grasp_point_score: 0.726
- phase_breakdown.placed_at_goal_score: 0.475
- grasp_place_fitness: 0.969

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.969
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.196
- **K-run variance**: 0.0026
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.274


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8110053be9072e64e15984c6424e4a66fe19af4b6c37a60139a43e94cc34ad53`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `46ef03f7b16015a0d14bf26d80c05d326b92c02b0bf759391930f5ab902d1933`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23488,"average_solve_count":281.0,"average_success_count":281.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.07113,"descend_to_grasp.descend_speed":0.03243,"descend_to_grasp.grasp_offset_x":0.00261,"descend_to_grasp.grasp_offset_y":0.00382,"grasp.grasp_retry_offset_x":0.00076,"grasp.grasp_retry_offset_y":7e-05,"lift_object.lift_distance":0.15503,"lift_object.lift_speed":0.04165,"place_at_goal.place_offset_x":-0.00344,"place_at_goal.place_offset_y":8e-05,"place_at_goal.place_offset_z":0.03204,"place_at_goal.place_speed":0.02815,"transport_to_goal.transport_speed":0.08265},"optimized_scores":{"best_composite_score":0.19618,"best_fitness_score":0.96618,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":122.0,"contact_point_centroid":[0.49732,0.04796,-0.0015],"force_p95":0.38235,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41192,"mean_force":0.10647,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48995,0.04734,0.04625]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12767.0,"contact_point_centroid":[0.48844,0.06632,0.11628],"force_p95":0.08331,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27845,"mean_force":0.05918,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48747,0.04711,0.11459]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15512.0,"contact_point_centroid":[0.48769,0.02814,0.11518],"force_p95":0.07728,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25056,"mean_force":0.05012,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48747,0.04711,0.11322]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04523,-0.00221],"force_p95":0.1799,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23702,"mean_force":0.13792,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49245,0.0476,0.04596]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3017.0,"contact_point_centroid":[0.55552,0.25401,0.21129],"force_p95":0.08281,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2061,"mean_force":0.05843,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.55599,0.23476,0.21121]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3511.0,"contact_point_centroid":[0.55557,0.21584,0.21161],"force_p95":0.06826,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16756,"mean_force":0.04565,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.55598,0.23477,0.21115]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4074.0,"contact_point_centroid":[0.49235,0.06678,0.04707],"force_p95":0.08296,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15789,"mean_force":0.05232,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4913,0.04749,0.0447]},{"body_a":"world","body_b":"grasp_target","contact_count":3176.0,"contact_point_centroid":[0.50118,0.04505,-0.00195],"force_p95":0.12742,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49738,0.02149,0.22309]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49713,0.04616,0.08632]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12577.0,"contact_point_centroid":[0.5222,0.12338,0.21037],"force_p95":0.07229,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10441,"mean_force":0.04755,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52227,0.14242,0.20923]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11368.0,"contact_point_centroid":[0.52357,0.16446,0.21073],"force_p95":0.07829,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10051,"mean_force":0.05205,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52338,0.14529,0.21007]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5586.0,"contact_point_centroid":[0.4911,0.02834,0.04749],"force_p95":0.07074,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07537,"mean_force":0.04018,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49131,0.04749,0.04471]}],"total_contact_groups":12},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.55993,0.23913,0.15864],"final_tcp_position":[0.55662,0.23974,0.18613],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.41192,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":795.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3176.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.49719,0.04261,0.15161],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12568,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.49898,0.04825,0.05316],"tcp_start":[0.49719,0.04261,0.15161],"tcp_to_object_dist_end":0.02742,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50115,0.0468,0.02525],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24083,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.17253,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11460.0,"raw_peak_contact_force":0.23702,"subtask_id":"grasp_point","tcp_end":[0.49127,0.04748,0.04467],"tcp_start":[0.49898,0.04825,0.05316],"tcp_to_object_dist_end":0.0218,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":751.0,"n_steps_budget":1000.0,"object_pos_end":[0.49286,0.04679,0.16181],"object_pos_start":[0.50115,0.0468,0.02525],"object_to_goal_dist_end":0.21114,"object_to_goal_dist_start":0.24083,"object_z_max":0.16164,"peak_contact_force":0.08163,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28401.0,"raw_peak_contact_force":0.41192,"subtask_id":"object_lifted","tcp_end":[0.48773,0.04714,0.18526],"tcp_start":[0.49127,0.04748,0.04467],"tcp_to_object_dist_end":0.024,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":613.0,"n_steps_budget":1000.0,"object_pos_end":[0.55951,0.23027,0.20871],"object_pos_start":[0.49286,0.04679,0.16181],"object_to_goal_dist_end":0.06382,"object_to_goal_dist_start":0.21114,"object_z_max":0.20864,"peak_contact_force":0.07112,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23945.0,"raw_peak_contact_force":0.10441,"subtask_id":"near_goal","tcp_end":[0.55672,0.23078,0.23512],"tcp_start":[0.48773,0.04714,0.18526],"tcp_to_object_dist_end":0.02656,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":160.0,"n_steps_budget":1000.0,"object_pos_end":[0.55993,0.23913,0.15864],"object_pos_start":[0.55951,0.23027,0.20871],"object_to_goal_dist_end":0.01392,"object_to_goal_dist_start":0.06382,"object_z_max":0.20871,"peak_contact_force":0.08227,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6528.0,"raw_peak_contact_force":0.2061,"subtask_id":"placed_at_goal","tcp_end":[0.55662,0.23974,0.18613],"tcp_start":[0.55672,0.23078,0.23512],"tcp_to_object_dist_end":0.02769,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1efc3ad2e58ea1c47cd56203c4986b53dab7b80d759e458b85d233ccc9cc04bd`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.83077,"average_solve_count":325.0,"average_success_count":325.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.06615,"descend_to_grasp.descend_speed":0.0133,"descend_to_grasp.grasp_offset_x":0.00737,"descend_to_grasp.grasp_offset_y":-0.00197,"grasp.grasp_retry_offset_x":0.00196,"grasp.grasp_retry_offset_y":-0.00099,"lift_object.lift_distance":0.16531,"lift_object.lift_speed":0.04866,"place_at_goal.place_offset_x":0.00138,"place_at_goal.place_offset_y":0.01906,"place_at_goal.place_offset_z":0.03178,"place_at_goal.place_speed":0.03865,"transport_to_goal.transport_speed":0.10053},"optimized_scores":{"best_composite_score":0.19886,"best_fitness_score":0.96886,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":111.0,"contact_point_centroid":[0.47294,-0.02225,-0.00144],"force_p95":0.36909,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43523,"mean_force":0.08537,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.47005,-0.0217,0.0464]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13428.0,"contact_point_centroid":[0.46724,-0.04082,0.11982],"force_p95":0.08361,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29197,"mean_force":0.05675,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46764,-0.02162,0.11809]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15764.0,"contact_point_centroid":[0.46788,-0.00261,0.12043],"force_p95":0.07363,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28644,"mean_force":0.04953,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46764,-0.02162,0.11849]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1781.0,"contact_point_centroid":[0.62778,0.17692,0.24889],"force_p95":0.13827,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26778,"mean_force":0.09777,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.62293,0.15876,0.251]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1606.0,"contact_point_centroid":[0.62766,0.14066,0.24814],"force_p95":0.13508,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25676,"mean_force":0.10361,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.62296,0.15877,0.25111]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.0203,-0.00215],"force_p95":0.16157,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21885,"mean_force":0.13325,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47246,-0.02176,0.04603]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11906.0,"contact_point_centroid":[0.53996,0.04075,0.23284],"force_p95":0.10558,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20499,"mean_force":0.06351,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53912,0.05975,0.23221]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13113.0,"contact_point_centroid":[0.5385,0.07631,0.2319],"force_p95":0.09873,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17688,"mean_force":0.05826,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53697,0.05738,0.23104]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4114.0,"contact_point_centroid":[0.47037,-0.04102,0.04694],"force_p95":0.08135,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15111,"mean_force":0.05204,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47134,-0.02173,0.04488]},{"body_a":"world","body_b":"grasp_target","contact_count":2740.0,"contact_point_centroid":[0.47616,-0.02015,-0.00195],"force_p95":0.12911,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48593,-0.00927,0.22621]},{"body_a":"world","body_b":"grasp_target","contact_count":3752.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47516,-0.02053,0.09528]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5502.0,"contact_point_centroid":[0.47117,-0.00264,0.04762],"force_p95":0.06933,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0707,"mean_force":0.04035,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47135,-0.02173,0.04488]}],"total_contact_groups":12},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63283,0.17121,0.19146],"final_tcp_position":[0.62709,0.1708,0.22507],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.43523,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":686.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2740.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.47386,-0.01882,0.15416],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12816,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":938.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3752.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.47879,-0.02194,0.0526],"tcp_start":[0.47386,-0.01882,0.15416],"tcp_to_object_dist_end":0.02677,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47608,-0.02139,0.02548],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28951,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.15637,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11416.0,"raw_peak_contact_force":0.21885,"subtask_id":"grasp_point","tcp_end":[0.47132,-0.02173,0.04485],"tcp_start":[0.47879,-0.02194,0.0526],"tcp_to_object_dist_end":0.01995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":759.0,"n_steps_budget":1000.0,"object_pos_end":[0.47072,-0.02142,0.17295],"object_pos_start":[0.47608,-0.02139,0.02548],"object_to_goal_dist_end":0.24236,"object_to_goal_dist_start":0.28951,"object_z_max":0.17277,"peak_contact_force":0.08276,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29303.0,"raw_peak_contact_force":0.43523,"subtask_id":"object_lifted","tcp_end":[0.46792,-0.02162,0.19555],"tcp_start":[0.47132,-0.02173,0.04485],"tcp_to_object_dist_end":0.02277,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":758.0,"n_steps_budget":1000.0,"object_pos_end":[0.62856,0.1489,0.24558],"object_pos_start":[0.47072,-0.02142,0.17295],"object_to_goal_dist_end":0.05658,"object_to_goal_dist_start":0.24236,"object_z_max":0.24553,"peak_contact_force":0.12486,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25019.0,"raw_peak_contact_force":0.20499,"subtask_id":"near_goal","tcp_end":[0.62052,0.14877,0.27695],"tcp_start":[0.46792,-0.02162,0.19555],"tcp_to_object_dist_end":0.03239,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":186.0,"n_steps_budget":1000.0,"object_pos_end":[0.63283,0.17121,0.19146],"object_pos_start":[0.62856,0.1489,0.24558],"object_to_goal_dist_end":0.01219,"object_to_goal_dist_start":0.05658,"object_z_max":0.24558,"peak_contact_force":0.12076,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3387.0,"raw_peak_contact_force":0.26778,"subtask_id":"placed_at_goal","tcp_end":[0.62709,0.1708,0.22507],"tcp_start":[0.62052,0.14877,0.27695],"tcp_to_object_dist_end":0.0341,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `37495cb43897015e78e007c86af160d11c8460c1ce7249e5c03dce38206c0daf`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.19549,"average_solve_count":266.0,"average_success_count":266.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.0591,"descend_to_grasp.descend_speed":0.03308,"descend_to_grasp.grasp_offset_x":0.00181,"descend_to_grasp.grasp_offset_y":3e-05,"grasp.grasp_retry_offset_x":0.00216,"grasp.grasp_retry_offset_y":-0.00036,"lift_object.lift_distance":0.10666,"lift_object.lift_speed":0.04815,"place_at_goal.place_offset_x":0.00686,"place_at_goal.place_offset_y":0.00867,"place_at_goal.place_offset_z":0.03482,"place_at_goal.place_speed":0.0324,"transport_to_goal.transport_speed":0.09653},"optimized_scores":{"best_composite_score":0.08946,"best_fitness_score":0.85946,"best_task_score":0.80215},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":110.0,"contact_point_centroid":[0.45553,-0.02489,-0.0014],"force_p95":0.29302,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36125,"mean_force":0.07206,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44737,-0.02569,0.0525]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5463.0,"contact_point_centroid":[0.44611,-0.00678,0.09118],"force_p95":0.11573,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31996,"mean_force":0.08192,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44514,-0.02559,0.09317]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6877.0,"contact_point_centroid":[0.44488,-0.04414,0.09032],"force_p95":0.10714,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3087,"mean_force":0.06717,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.44512,-0.02559,0.09154]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11245.0,"contact_point_centroid":[0.52643,0.06228,0.16633],"force_p95":0.1159,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25834,"mean_force":0.07449,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52634,0.08069,0.1697]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1308.0,"contact_point_centroid":[0.62751,0.18436,0.17506],"force_p95":0.12632,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24032,"mean_force":0.10002,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.62199,0.20224,0.17999]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1184.0,"contact_point_centroid":[0.62744,0.2199,0.17633],"force_p95":0.15402,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23265,"mean_force":0.11391,"phase_index":5.0,"phase_name":"place_at_goal","phase_type":"descend","tcp_position_centroid":[0.62161,0.20175,0.1816]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9191.0,"contact_point_centroid":[0.52647,0.09835,0.16612],"force_p95":0.13987,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22817,"mean_force":0.0899,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52554,0.07966,0.16943]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02631,-0.00209],"force_p95":0.15021,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17175,"mean_force":0.1295,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44966,-0.02577,0.05199]},{"body_a":"world","body_b":"grasp_target","contact_count":2852.0,"contact_point_centroid":[0.45856,-0.02632,-0.00195],"force_p95":0.12892,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47789,-0.01206,0.22654]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4027.0,"contact_point_centroid":[0.44962,-0.00666,0.05077],"force_p95":0.09873,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13395,"mean_force":0.05606,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4486,-0.02573,0.05095]},{"body_a":"world","body_b":"grasp_target","contact_count":2560.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45503,-0.02523,0.10394]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4635.0,"contact_point_centroid":[0.44884,-0.04458,0.0509],"force_p95":0.07717,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08439,"mean_force":0.04697,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4486,-0.02573,0.05095]}],"total_contact_groups":12},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.63825,0.20467,0.08226],"final_tcp_position":[0.62921,0.21113,0.15139],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.36125,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":714.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2852.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_above_object","tcp_end":[0.45739,-0.02456,0.15447],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12847,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":640.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2560.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_point","tcp_end":[0.45583,-0.026,0.0581],"tcp_start":[0.45739,-0.02456,0.15447],"tcp_to_object_dist_end":0.0322,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45848,-0.02576,0.02547],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30342,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.15381,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10462.0,"raw_peak_contact_force":0.17175,"subtask_id":"grasp_point","tcp_end":[0.44858,-0.02573,0.05092],"tcp_start":[0.45583,-0.026,0.0581],"tcp_to_object_dist_end":0.02731,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":446.0,"n_steps_budget":1000.0,"object_pos_end":[0.44885,-0.02583,0.11334],"object_pos_start":[0.45848,-0.02576,0.02547],"object_to_goal_dist_end":0.29605,"object_to_goal_dist_start":0.30342,"object_z_max":0.11316,"peak_contact_force":0.10418,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12450.0,"raw_peak_contact_force":0.36125,"subtask_id":"object_lifted","tcp_end":[0.44493,-0.02557,0.14321],"tcp_start":[0.44858,-0.02573,0.05092],"tcp_to_object_dist_end":0.03013,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":888.0,"n_steps_budget":1000.0,"object_pos_end":[0.62457,0.19605,0.16507],"object_pos_start":[0.44885,-0.02583,0.11334],"object_to_goal_dist_end":0.05267,"object_to_goal_dist_start":0.29605,"object_z_max":0.16504,"peak_contact_force":0.11405,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20436.0,"raw_peak_contact_force":0.25834,"subtask_id":"near_goal","tcp_end":[0.6188,0.19672,0.20246],"tcp_start":[0.44493,-0.02557,0.14321],"tcp_to_object_dist_end":0.03784,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":186.0,"n_steps_budget":1000.0,"object_pos_end":[0.63825,0.20467,0.08226],"object_pos_start":[0.62457,0.19605,0.16507],"object_to_goal_dist_end":0.03307,"object_to_goal_dist_start":0.05267,"object_z_max":0.16507,"peak_contact_force":0.0,"phase_name":"place_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2492.0,"raw_peak_contact_force":0.24032,"subtask_id":"placed_at_goal","tcp_end":[0.62921,0.21113,0.15139],"tcp_start":[0.6188,0.19672,0.20246],"tcp_to_object_dist_end":0.07002,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```