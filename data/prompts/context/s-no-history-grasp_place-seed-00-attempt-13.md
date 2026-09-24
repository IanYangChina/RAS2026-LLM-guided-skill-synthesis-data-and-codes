## Search State

- **Seed**: 0
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
- Frozen realised-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`
- Frozen object start: [0.5136961687321454, -0.02302132862361297, 0.03]
- Frozen task target: [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]
- Goal object position: (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5136961687321454, -0.02302132862361297, 0.03)
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
  frozen_object_start: [0.5137, -0.023, 0.03]
  frozen_task_target: [0.5541, 0.1517, 0.222]
  frozen_object_starts: {'grasp_target': [0.5136961687321454, -0.02302132862361297, 0.03]}
  frozen_targets: {'place_target': [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea

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
| `object` | offset from object initial position (0.5136961687321454, -0.02302132862361297, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5540973523936195, 0.15165276355285293, 0.22199053588004086) | final destination targets |
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

## Current Skill (Q=-0.258) — your mutation base

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
  weight: 0.2
- id: grasp_contact
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.03
  weight: 0.2
- id: lift_clear
  offset:
  - 0.0
  - 0.0
  - 0.222
  weight: 0.1
- id: place_goal
  target_entity: object
  metric: goal_progress
  weight: 0.5
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
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_object
- id: descend_grasp
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_height:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: grasp_contact
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
  parameters:
    grasp_time:
      type: scalar
      range:
      - 0.2
      - 2.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: grasp_contact
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
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_distance:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: lift_clear
- id: transport_to_goal
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
    transport_z:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: place_goal
- id: place_release
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    release_time:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.3
      binds_to:
      - path: duration.max_time
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
- id: retract_after_place
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_distance:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_time: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=1, strategy=repeat
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - retries: max_attempts=0, strategy=repeat
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_z: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat
- **place_release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_time: status=consumed; consumers=duration.max_time (replace)
  - retries: max_attempts=0, strategy=repeat
- **retract_after_place** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: -0.258
- **task_score** (E): 0.324
- **fitness_score**: 0.622  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.880

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.0755 |
| descend_grasp | 1.00 | 1.00 | 0.1737 |
| grasp_1 | 1.00 | 1.00 | 0.0123 |
| lift_object | 1.00 | 1.00 | 0.1299 |
| transport_to_goal | 1.00 | 1.00 | 0.2110 |
| descend_place | 1.00 | 1.00 | 0.0316 |
| place_release | 1.00 | 1.00 | 0.0214 |
| retract_after_place | 1.00 | 1.00 | 0.0925 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, -0.001, 0.231) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 15.738 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.495, -0.001, 0.231)→(0.493, 0.000, 0.057) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.493, 0.000, 0.057)→(0.485, 0.000, 0.048) | (0.497, 0.001, 0.026)→(0.497, 0.000, 0.025) | 0.265→0.266 | 1.00 / 43.333 | 0.160 | 0.212 |
| lift_object | lift | 1.00 / step_budget | (0.485, 0.000, 0.048)→(0.481, 0.000, 0.178) | (0.497, 0.000, 0.025)→(0.490, 0.001, 0.151) | 0.266→0.216 | 1.00 / 32.333 | 0.100 | 0.392 |
| transport_to_goal | approach | 1.00 / step_budget | (0.481, 0.000, 0.178)→(0.575, 0.172, 0.232) | (0.490, 0.001, 0.151)→(0.571, 0.170, 0.078) | 0.216→0.119 | 1.00 / 8.333 | 0.398 | 1.204 |
| descend_place | descend | 1.00 / step_budget | (0.575, 0.172, 0.232)→(0.577, 0.178, 0.202) | (0.571, 0.170, 0.078)→(0.572, 0.171, 0.081) | 0.119→0.108 | 1.00 / 9.333 | 91002.187 | 0.410 |
| place_release | release | 1.00 / step_budget | (0.577, 0.178, 0.202)→(0.572, 0.177, 0.223) | (0.572, 0.171, 0.081)→(0.572, 0.175, 0.016) | 0.108→0.172 | 1.00 / 4.000 | 0.113 | 0.760 |
| retract_after_place | retract | 1.00 / step_budget | (0.572, 0.177, 0.223)→(0.570, 0.176, 0.315) | (0.572, 0.175, 0.016)→(0.572, 0.175, 0.016) | 0.172→0.172 | 1.00 / 4.000 | 0.123 | 0.125 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.416
- phase_score: 0.344
- phase_breakdown.grasp_contact_score: 0.710
- phase_breakdown.place_goal_score: 0.334
- phase_breakdown.lift_clear_score: 0.208
- phase_breakdown.reach_object_score: 0.069
- grasp_place_fitness: 0.667

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.667
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.416
- **Median Q (composite search score)**: -0.267
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.330


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `096c354712624ed6bd8f9b9cbbbc2b7d35a94d9c1517cfb8353e2e383be5aaf0`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3798aa6551d21849355469c7d63897f628ac7de9267c18bb4301fe6cfaae0164`; realized-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5137,-0.02302,0.03]},{"name":"goal","value":[0.5541,0.15165,0.22199]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5137,-0.02302,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5541,0.15165,0.22199]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56977,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.18746,"approach_object.approach_speed":0.1422,"descend_grasp.descend_height":0.01253,"descend_grasp.descend_speed":0.12104,"descend_place.descend_place_speed":0.06917,"descend_place.place_height":0.01363,"grasp_1.grasp_time":1.30488,"lift_object.lift_distance":0.15884,"lift_object.lift_speed":0.05708,"place_release.release_time":0.33168,"retract_after_place.retract_distance":0.11802,"retract_after_place.retract_speed":0.13175,"transport_to_goal.transport_speed":0.20716,"transport_to_goal.transport_z_offset":0.05974},"optimized_scores":{"best_composite_score":-0.29275,"best_fitness_score":0.58725,"best_task_score":0.25322},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":248.0,"contact_point_centroid":[0.55757,0.1543,-0.00736],"force_p95":1.4943,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.0332,"mean_force":0.34891,"phase_index":6.0,"phase_name":"place_release","phase_type":"release","tcp_position_centroid":[0.54464,0.14362,0.26]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":222.0,"contact_point_centroid":[0.5537,0.12662,0.24017],"force_p95":0.29162,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40635,"mean_force":0.16284,"phase_index":6.0,"phase_name":"place_release","phase_type":"release","tcp_position_centroid":[0.54782,0.14471,0.24462]},{"body_a":"world","body_b":"grasp_target","contact_count":87.0,"contact_point_centroid":[0.51125,-0.02158,-0.00144],"force_p95":0.32524,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39604,"mean_force":0.0967,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49943,-0.02191,0.04912]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9734.0,"contact_point_centroid":[0.49754,-0.0409,0.11704],"force_p95":0.08239,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27615,"mean_force":0.05483,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49701,-0.02184,0.11621]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8712.0,"contact_point_centroid":[0.49765,-0.0027,0.11747],"force_p95":0.08426,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27419,"mean_force":0.0598,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.497,-0.02184,0.11657]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":426.0,"contact_point_centroid":[0.55332,0.16179,0.24015],"force_p95":0.1493,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27401,"mean_force":0.08835,"phase_index":6.0,"phase_name":"place_release","phase_type":"release","tcp_position_centroid":[0.54767,0.14466,0.2443]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":522.0,"contact_point_centroid":[0.55376,0.1597,0.25566],"force_p95":0.12921,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23473,"mean_force":0.10153,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54821,0.1416,0.25927]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5868.0,"contact_point_centroid":[0.52035,0.06456,0.21808],"force_p95":0.13521,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2201,"mean_force":0.08251,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51706,0.04581,0.21915]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6436.0,"contact_point_centroid":[0.52156,0.02967,0.21999],"force_p95":0.12232,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21363,"mean_force":0.07278,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51782,0.04818,0.22038]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51372,-0.02294,-0.00209],"force_p95":0.14854,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20164,"mean_force":0.12955,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50175,-0.02197,0.04908]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":410.0,"contact_point_centroid":[0.55364,0.12333,0.25609],"force_p95":0.15563,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18682,"mean_force":0.12533,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54816,0.14139,0.26007]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4342.0,"contact_point_centroid":[0.50118,-0.00275,0.04901],"force_p95":0.0745,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14345,"mean_force":0.0495,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50061,-0.02194,0.04783]},{"body_a":"world","body_b":"grasp_target","contact_count":536.0,"contact_point_centroid":[0.5137,-0.02302,-0.00176],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12354,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50336,-0.00772,0.26902]},{"body_a":"world","body_b":"grasp_target","contact_count":1328.0,"contact_point_centroid":[0.55774,0.15453,-0.00195],"force_p95":0.1265,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13047,"mean_force":0.12144,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.54298,0.1431,0.31793]},{"body_a":"world","body_b":"grasp_target","contact_count":1316.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50748,-0.01931,0.14658]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4950.0,"contact_point_centroid":[0.50113,-0.0411,0.04894],"force_p95":0.07093,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07268,"mean_force":0.04436,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50062,-0.02194,0.04783]}],"total_contact_groups":16},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.55774,0.15453,0.01602],"final_tcp_position":[0.54324,0.14312,0.36762],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":2.0332,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":135.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":536.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50769,-0.01661,0.23492],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20908,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":329.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1316.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_contact","tcp_end":[0.50903,-0.02212,0.0575],"tcp_start":[0.50769,-0.01661,0.23492],"tcp_to_object_dist_end":0.03184,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51364,-0.02227,0.02566],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26539,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.14642,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11092.0,"raw_peak_contact_force":0.20164,"subtask_id":"grasp_contact","tcp_end":[0.50058,-0.02194,0.04779],"tcp_start":[0.50903,-0.02212,0.0575],"tcp_to_object_dist_end":0.0257,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":484.0,"n_steps_budget":1000.0,"object_pos_end":[0.505,-0.02204,0.16067],"object_pos_start":[0.51364,-0.02227,0.02566],"object_to_goal_dist_end":0.19063,"object_to_goal_dist_start":0.26539,"object_z_max":0.16041,"peak_contact_force":0.07787,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18533.0,"raw_peak_contact_force":0.39604,"subtask_id":"lift_clear","tcp_end":[0.49719,-0.02184,0.1871],"tcp_start":[0.50058,-0.02194,0.04779],"tcp_to_object_dist_end":0.02756,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":486.0,"n_steps_budget":1000.0,"object_pos_end":[0.55363,0.138,0.23326],"object_pos_start":[0.505,-0.02204,0.16067],"object_to_goal_dist_end":0.01771,"object_to_goal_dist_start":0.19063,"object_z_max":0.23315,"peak_contact_force":0.12812,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12304.0,"raw_peak_contact_force":0.2201,"subtask_id":"place_goal","tcp_end":[0.54767,0.13871,0.26827],"tcp_start":[0.49719,-0.02184,0.1871],"tcp_to_object_dist_end":0.03553,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":58.0,"n_steps_budget":1000.0,"object_pos_end":[0.5566,0.14369,0.21189],"object_pos_start":[0.55363,0.138,0.23326],"object_to_goal_dist_end":0.01311,"object_to_goal_dist_start":0.01771,"object_z_max":0.23327,"peak_contact_force":0.15609,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":932.0,"raw_peak_contact_force":0.23473,"tcp_end":[0.54912,0.1448,0.24764],"tcp_start":[0.54767,0.13871,0.26827],"tcp_to_object_dist_end":0.03655,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55783,0.1554,0.01618],"object_pos_start":[0.5566,0.14369,0.21189],"object_to_goal_dist_end":0.20588,"object_to_goal_dist_start":0.01311,"object_z_max":0.21189,"peak_contact_force":0.09325,"phase_name":"place_release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":896.0,"raw_peak_contact_force":2.0332,"tcp_end":[0.5446,0.14361,0.26941],"tcp_start":[0.54912,0.1448,0.24764],"tcp_to_object_dist_end":0.25385,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":332.0,"n_steps_budget":600.0,"object_pos_end":[0.55774,0.15453,0.01602],"object_pos_start":[0.55783,0.1554,0.01618],"object_to_goal_dist_end":0.20602,"object_to_goal_dist_start":0.20588,"object_z_max":0.01688,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1328.0,"raw_peak_contact_force":0.13047,"tcp_end":[0.54324,0.14312,0.36762],"tcp_start":[0.5446,0.14361,0.26941],"tcp_to_object_dist_end":0.35208,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `ed2df336ade3d991e9495251c8398520a59dd014a70bd2d7bb71dc7aefccaa8a`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62694,"average_solve_count":193.0,"average_success_count":193.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.22082,"approach_object.approach_speed":0.12819,"descend_grasp.descend_height":0.01284,"descend_grasp.descend_speed":0.06263,"descend_place.descend_place_speed":0.06076,"descend_place.place_height":0.00933,"grasp_1.grasp_time":1.16971,"lift_object.lift_distance":0.1241,"lift_object.lift_speed":0.07894,"place_release.release_time":0.48244,"retract_after_place.retract_distance":0.11612,"retract_after_place.retract_speed":0.11395,"transport_to_goal.transport_speed":0.18874,"transport_to_goal.transport_z_offset":0.0123},"optimized_scores":{"best_composite_score":-0.2127,"best_fitness_score":0.6673,"best_task_score":0.41619},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":111.0,"contact_point_centroid":[0.55083,0.24343,-0.00721],"force_p95":1.00276,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.23744,"mean_force":0.48795,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55356,0.22404,0.15149]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.4989,0.04159,-0.00161],"force_p95":0.32145,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42139,"mean_force":0.07936,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48739,0.04217,0.05036]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3331.0,"contact_point_centroid":[0.51437,0.09372,0.14775],"force_p95":0.156,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37795,"mean_force":0.1116,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51004,0.11228,0.15048]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5292.0,"contact_point_centroid":[0.48703,0.02297,0.095],"force_p95":0.13881,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35904,"mean_force":0.07089,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48506,0.04197,0.09504]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5772.0,"contact_point_centroid":[0.48712,0.06053,0.09565],"force_p95":0.11747,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30126,"mean_force":0.06724,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48509,0.04197,0.09493]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5013,0.04496,-0.00224],"force_p95":0.18981,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24071,"mean_force":0.13945,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48983,0.04241,0.04988]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4705.0,"contact_point_centroid":[0.51577,0.13289,0.14941],"force_p95":0.1286,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21736,"mean_force":0.08119,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51103,0.11498,0.15044]},{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.55054,0.24599,-0.004],"force_p95":0.13723,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16926,"mean_force":0.09241,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.55548,0.23121,0.15008]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4095.0,"contact_point_centroid":[0.48912,0.02307,0.04955],"force_p95":0.09369,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14245,"mean_force":0.05553,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48872,0.04231,0.04868]},{"body_a":"world","body_b":"grasp_target","contact_count":404.0,"contact_point_centroid":[0.50118,0.04505,-0.00169],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12388,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49918,0.01361,0.28243]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55058,0.246,-0.00195],"force_p95":0.12408,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12447,"mean_force":0.12145,"phase_index":6.0,"phase_name":"place_release","phase_type":"release","tcp_position_centroid":[0.55234,0.23262,0.15059]},{"body_a":"world","body_b":"grasp_target","contact_count":1604.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49697,0.0362,0.16099]},{"body_a":"world","body_b":"grasp_target","contact_count":1396.0,"contact_point_centroid":[0.55058,0.246,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.54821,0.23069,0.21823]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5223.0,"contact_point_centroid":[0.48883,0.06135,0.04992],"force_p95":0.07616,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08184,"mean_force":0.04193,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48872,0.04231,0.04869]},{"body_a":"left_finger","body_b":"right_finger","contact_count":175.0,"contact_point_centroid":[0.55543,0.23384,0.14778],"force_p95":0.01561,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01651,"mean_force":0.01148,"phase_index":6.0,"phase_name":"place_release","phase_type":"release","tcp_position_centroid":[0.55468,0.2338,0.14572]}],"total_contact_groups":15},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.55058,0.246,0.01602],"final_tcp_position":[0.54832,0.23068,0.26702],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.23744,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":102.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24189,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12227,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":404.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49874,0.02969,0.26266],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":401.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24189,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1604.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_contact","tcp_end":[0.49694,0.04299,0.05791],"tcp_start":[0.49874,0.02969,0.26266],"tcp_to_object_dist_end":0.03223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50125,0.04322,0.02507],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24385,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.19034,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11118.0,"raw_peak_contact_force":0.24071,"subtask_id":"grasp_contact","tcp_end":[0.48869,0.0423,0.04865],"tcp_start":[0.49694,0.04299,0.05791],"tcp_to_object_dist_end":0.02673,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":340.0,"n_steps_budget":990.0,"object_pos_end":[0.49761,0.04362,0.12476],"object_pos_start":[0.50125,0.04322,0.02507],"object_to_goal_dist_end":0.21319,"object_to_goal_dist_start":0.24385,"object_z_max":0.12449,"peak_contact_force":0.13987,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11152.0,"raw_peak_contact_force":0.42139,"subtask_id":"lift_clear","tcp_end":[0.48495,0.04196,0.15335],"tcp_start":[0.48869,0.0423,0.04865],"tcp_to_object_dist_end":0.03131,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":501.0,"n_steps_budget":1000.0,"object_pos_end":[0.55107,0.24596,0.00548],"object_pos_start":[0.49761,0.04362,0.12476],"object_to_goal_dist_end":0.14192,"object_to_goal_dist_start":0.21319,"object_z_max":0.12502,"peak_contact_force":0.18177,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8147.0,"raw_peak_contact_force":1.23744,"subtask_id":"place_goal","tcp_end":[0.5554,0.22903,0.15149],"tcp_start":[0.48495,0.04196,0.15335],"tcp_to_object_dist_end":0.14705,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":37.0,"n_steps_budget":1000.0,"object_pos_end":[0.55061,0.24607,0.01608],"object_pos_start":[0.55107,0.24596,0.00548],"object_to_goal_dist_end":0.13143,"object_to_goal_dist_start":0.14192,"object_z_max":0.016,"peak_contact_force":0.09817,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":148.0,"raw_peak_contact_force":0.16926,"tcp_end":[0.55662,0.23422,0.14913],"tcp_start":[0.5554,0.22903,0.15149],"tcp_to_object_dist_end":0.13371,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55058,0.246,0.01602],"object_pos_start":[0.55061,0.24607,0.01608],"object_to_goal_dist_end":0.13149,"object_to_goal_dist_start":0.13143,"object_z_max":0.01649,"peak_contact_force":0.12263,"phase_name":"place_release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":975.0,"raw_peak_contact_force":0.12447,"tcp_end":[0.55075,0.23186,0.17054],"tcp_start":[0.55662,0.23422,0.14913],"tcp_to_object_dist_end":0.15516,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":349.0,"n_steps_budget":660.0,"object_pos_end":[0.55058,0.246,0.01602],"object_pos_start":[0.55058,0.246,0.01602],"object_to_goal_dist_end":0.13149,"object_to_goal_dist_start":0.13149,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1396.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54832,0.23068,0.26702],"tcp_start":[0.55075,0.23186,0.17054],"tcp_to_object_dist_end":0.25148,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `291bc6f2bd023fc25503740a7343328e565e43fc71fa3c9c5d2fdbe2d4351fd2`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.12195,"average_solve_count":287.0,"average_success_count":287.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.14544,"approach_object.approach_speed":0.11903,"descend_grasp.descend_height":0.01107,"descend_grasp.descend_speed":0.04157,"descend_place.descend_place_speed":0.07181,"descend_place.place_height":0.0068,"grasp_1.grasp_time":0.96517,"lift_object.lift_distance":0.16529,"lift_object.lift_speed":0.02089,"place_release.release_time":0.99909,"retract_after_place.retract_distance":0.10252,"retract_after_place.retract_speed":0.11347,"transport_to_goal.transport_speed":0.24999,"transport_to_goal.transport_z_offset":0.09998},"optimized_scores":{"best_composite_score":-0.2671,"best_fitness_score":0.6129,"best_task_score":0.30278},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":46.0,"contact_point_centroid":[0.60803,0.13127,-0.00911],"force_p95":1.81652,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.154,"mean_force":1.16662,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.61909,0.14783,0.2759]},{"body_a":"world","body_b":"grasp_target","contact_count":584.0,"contact_point_centroid":[0.6082,0.12272,-0.00357],"force_p95":0.36587,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.82664,"mean_force":0.13882,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.62254,0.15233,0.24459]},{"body_a":"world","body_b":"grasp_target","contact_count":98.0,"contact_point_centroid":[0.47262,-0.01912,-0.00154],"force_p95":0.32399,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35978,"mean_force":0.15305,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46353,-0.01924,0.04887]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6715.0,"contact_point_centroid":[0.51947,0.06302,0.22114],"force_p95":0.12329,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33408,"mean_force":0.07796,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51983,0.04412,0.22292]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8169.0,"contact_point_centroid":[0.5226,0.02938,0.22305],"force_p95":0.11092,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26969,"mean_force":0.06481,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52352,0.04799,0.22489]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10138.0,"contact_point_centroid":[0.46134,-0.03816,0.12006],"force_p95":0.0797,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22294,"mean_force":0.05298,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46123,-0.01916,0.11909]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8629.0,"contact_point_centroid":[0.46215,0.0,0.11985],"force_p95":0.08388,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21434,"mean_force":0.06063,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46124,-0.01916,0.11899]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47618,-0.0201,-0.00207],"force_p95":0.14442,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19415,"mean_force":0.12841,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46572,-0.01929,0.04911]},{"body_a":"world","body_b":"grasp_target","contact_count":804.0,"contact_point_centroid":[0.47616,-0.02015,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12324,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48921,-0.00765,0.24896]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.60832,0.12301,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12279,"mean_force":0.12261,"phase_index":6.0,"phase_name":"place_release","phase_type":"release","tcp_position_centroid":[0.62173,0.15463,0.20908]},{"body_a":"world","body_b":"grasp_target","contact_count":1128.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.4745,-0.01773,0.12657]},{"body_a":"world","body_b":"grasp_target","contact_count":1304.0,"contact_point_centroid":[0.60832,0.12301,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.61831,0.15352,0.2694]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4831.0,"contact_point_centroid":[0.46418,-1e-05,0.04855],"force_p95":0.06892,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10556,"mean_force":0.04513,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46464,-0.01926,0.04804]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5419.0,"contact_point_centroid":[0.46401,-0.03848,0.04893],"force_p95":0.06555,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06885,"mean_force":0.04083,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46465,-0.01926,0.04804]},{"body_a":"left_finger","body_b":"right_finger","contact_count":496.0,"contact_point_centroid":[0.62352,0.15291,0.23988],"force_p95":0.01327,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01607,"mean_force":0.01094,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.623,0.1529,0.23748]},{"body_a":"left_finger","body_b":"right_finger","contact_count":217.0,"contact_point_centroid":[0.62468,0.15539,0.2078],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.0102,"phase_index":6.0,"phase_name":"place_release","phase_type":"release","tcp_position_centroid":[0.62404,0.15537,0.2055]}],"total_contact_groups":16},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.60832,0.12301,0.01602],"final_tcp_position":[0.61847,0.1535,0.31134],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273006.30814,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":202.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":46.96896,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":804.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47817,-0.01617,0.19455],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16859,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":282.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1128.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.47262,-0.01943,0.05641],"tcp_start":[0.47817,-0.01617,0.19455],"tcp_to_object_dist_end":0.03061,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4761,-0.01955,0.02572],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28822,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14313,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12050.0,"raw_peak_contact_force":0.19415,"subtask_id":"grasp_contact","tcp_end":[0.46462,-0.01926,0.04801],"tcp_start":[0.47262,-0.01943,0.05641],"tcp_to_object_dist_end":0.02508,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":506.0,"n_steps_budget":1000.0,"object_pos_end":[0.46798,-0.01928,0.16869],"object_pos_start":[0.4761,-0.01955,0.02572],"object_to_goal_dist_end":0.24294,"object_to_goal_dist_start":0.28822,"object_z_max":0.16841,"peak_contact_force":0.08086,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18865.0,"raw_peak_contact_force":0.35978,"subtask_id":"lift_clear","tcp_end":[0.46139,-0.01916,0.19365],"tcp_start":[0.46462,-0.01926,0.04801],"tcp_to_object_dist_end":0.02581,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":638.0,"n_steps_budget":1000.0,"object_pos_end":[0.60977,0.12719,-0.00405],"object_pos_start":[0.46798,-0.01928,0.16869],"object_to_goal_dist_end":0.19788,"object_to_goal_dist_start":0.24294,"object_z_max":0.2239,"peak_contact_force":0.88268,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14930.0,"raw_peak_contact_force":2.154,"subtask_id":"place_goal","tcp_end":[0.62046,0.14936,0.27663],"tcp_start":[0.46139,-0.01916,0.19365],"tcp_to_object_dist_end":0.28176,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":146.0,"n_steps_budget":1000.0,"object_pos_end":[0.60832,0.12301,0.016],"object_pos_start":[0.60977,0.12719,-0.00405],"object_to_goal_dist_end":0.17923,"object_to_goal_dist_start":0.19788,"object_z_max":0.01677,"peak_contact_force":273006.30814,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1080.0,"raw_peak_contact_force":0.82664,"tcp_end":[0.62573,0.15574,0.20985],"tcp_start":[0.62046,0.14936,0.27663],"tcp_to_object_dist_end":0.19736,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60832,0.12301,0.01602],"object_pos_start":[0.60832,0.12301,0.016],"object_to_goal_dist_end":0.17921,"object_to_goal_dist_start":0.17923,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12279,"tcp_end":[0.6204,0.15419,0.2285],"tcp_start":[0.62573,0.15574,0.20985],"tcp_to_object_dist_end":0.2151,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":326.0,"n_steps_budget":600.0,"object_pos_end":[0.60832,0.12301,0.01602],"object_pos_start":[0.60832,0.12301,0.01602],"object_to_goal_dist_end":0.17921,"object_to_goal_dist_start":0.17921,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1304.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61847,0.1535,0.31134],"tcp_start":[0.6204,0.15419,0.2285],"tcp_to_object_dist_end":0.29707,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```