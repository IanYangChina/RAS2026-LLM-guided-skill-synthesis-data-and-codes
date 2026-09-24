## Search State

- **Seed**: 0
- **Iteration**: 12 / 15

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

## Current Skill (Q=0.127) — your mutation base

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

- **Composite score**: 0.127
- **task_score** (E): 0.336
- **fitness_score**: 0.627  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1079 |
| descend_grasp | 1.00 | 1.00 | 0.1395 |
| grasp_1 | 1.00 | 1.00 | 0.0123 |
| lift_object | 1.00 | 1.00 | 0.1155 |
| transport_to_goal | 1.00 | 1.00 | 0.2022 |
| place_release | 1.00 | 1.00 | 0.0222 |
| retract_after_place | 1.00 | 1.00 | 0.0867 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, -0.001, 0.198) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.495, -0.001, 0.198)→(0.493, 0.001, 0.058) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 27.129 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.493, 0.001, 0.058)→(0.485, 0.000, 0.049) | (0.497, 0.001, 0.026)→(0.497, 0.000, 0.025) | 0.265→0.266 | 1.00 / 42.667 | 0.165 | 0.211 |
| lift_object | lift | 1.00 / step_budget | (0.485, 0.000, 0.049)→(0.481, 0.000, 0.165) | (0.497, 0.000, 0.025)→(0.494, 0.000, 0.136) | 0.266→0.220 | 1.00 / 22.000 | 0.126 | 0.401 |
| transport_to_goal | approach | 1.00 / step_budget | (0.481, 0.000, 0.165)→(0.573, 0.171, 0.181) | (0.494, 0.000, 0.136)→(0.579, 0.165, 0.105) | 0.220→0.085 | 1.00 / 12.333 | 0.119 | 0.660 |
| place_release | release | 1.00 / step_budget | (0.573, 0.171, 0.181)→(0.568, 0.170, 0.202) | (0.579, 0.165, 0.105)→(0.571, 0.163, 0.021) | 0.085→0.168 | 1.00 / 3.000 | 0.245 | 1.101 |
| retract_after_place | retract | 1.00 / step_budget | (0.568, 0.170, 0.202)→(0.565, 0.169, 0.289) | (0.571, 0.163, 0.021)→(0.563, 0.163, 0.023) | 0.168→0.167 | 1.00 / 4.000 | 0.123 | 0.242 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.435
- phase_score: 0.612
- phase_breakdown.grasp_contact_score: 0.720
- phase_breakdown.place_goal_score: 0.900
- phase_breakdown.lift_clear_score: 0.002
- phase_breakdown.reach_object_score: 0.090
- grasp_place_fitness: 0.676

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.676
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.435
- **Median Q (composite search score)**: 0.116
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.364


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90196,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.09022,"descend_grasp.descend_height":0.01429,"grasp_1.grasp_time":1.31664,"lift_object.lift_distance":0.12127,"place_release.release_time":0.69385,"retract_after_place.retract_distance":0.1347,"transport_to_goal.transport_z":-0.00518},"optimized_scores":{"best_composite_score":0.09051,"best_fitness_score":0.59051,"best_task_score":0.26571},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":140.0,"contact_point_centroid":[0.53563,0.13454,-0.00944],"force_p95":1.3825,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.73072,"mean_force":0.524,"phase_index":5.0,"phase_name":"place_release","phase_type":"release","tcp_position_centroid":[0.54148,0.13657,0.2204]},{"body_a":"world","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.51129,-0.02133,-0.00144],"force_p95":0.33949,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37667,"mean_force":0.07481,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49902,-0.02192,0.05146]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4918.0,"contact_point_centroid":[0.4989,-0.00286,0.09299],"force_p95":0.13802,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32955,"mean_force":0.0724,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49672,-0.02185,0.09336]},{"body_a":"world","body_b":"grasp_target","contact_count":1505.0,"contact_point_centroid":[0.5276,0.13291,-0.00207],"force_p95":0.19988,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29348,"mean_force":0.12538,"phase_index":6.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.53928,0.13595,0.28707]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5503.0,"contact_point_centroid":[0.4989,-0.04036,0.09427],"force_p95":0.11244,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26645,"mean_force":0.06666,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49672,-0.02185,0.09415]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5303.0,"contact_point_centroid":[0.52331,0.03336,0.17247],"force_p95":0.12772,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2352,"mean_force":0.08982,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51803,0.05148,0.17408]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":603.0,"contact_point_centroid":[0.5503,0.1559,0.1981],"force_p95":0.12772,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22195,"mean_force":0.08358,"phase_index":5.0,"phase_name":"place_release","phase_type":"release","tcp_position_centroid":[0.54482,0.13766,0.20197]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51376,-0.02301,-0.00211],"force_p95":0.15703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2002,"mean_force":0.13084,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50147,-0.02198,0.0512]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4554.0,"contact_point_centroid":[0.52572,0.078,0.17373],"force_p95":0.1387,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19467,"mean_force":0.10173,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52072,0.05966,0.177]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":533.0,"contact_point_centroid":[0.54993,0.11917,0.1973],"force_p95":0.13951,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18221,"mean_force":0.09214,"phase_index":5.0,"phase_name":"place_release","phase_type":"release","tcp_position_centroid":[0.54475,0.13764,0.20185]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4344.0,"contact_point_centroid":[0.50094,-0.00274,0.05035],"force_p95":0.08631,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14313,"mean_force":0.05271,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50033,-0.02195,0.04995]},{"body_a":"world","body_b":"grasp_target","contact_count":1236.0,"contact_point_centroid":[0.5137,-0.02302,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50356,-0.00956,0.22072]},{"body_a":"world","body_b":"grasp_target","contact_count":604.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50795,-0.02095,0.09982]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4947.0,"contact_point_centroid":[0.50088,-0.04096,0.05042],"force_p95":0.07039,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07315,"mean_force":0.04352,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50034,-0.02195,0.04995]}],"total_contact_groups":14},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.52659,0.13263,0.02602],"final_tcp_position":[0.53967,0.13602,0.34257],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":310.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1236.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50862,-0.01982,0.13883],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11297,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":151.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":604.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.50876,-0.02213,0.05966],"tcp_start":[0.50862,-0.01982,0.13883],"tcp_to_object_dist_end":0.03401,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5137,-0.02229,0.02552],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.2655,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.15865,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11091.0,"raw_peak_contact_force":0.2002,"subtask_id":"grasp_contact","tcp_end":[0.5003,-0.02195,0.04991],"tcp_start":[0.50876,-0.02213,0.05966],"tcp_to_object_dist_end":0.02784,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":327.0,"n_steps_budget":780.0,"object_pos_end":[0.50838,-0.02298,0.12195],"object_pos_start":[0.5137,-0.02229,0.02552],"object_to_goal_dist_end":0.20638,"object_to_goal_dist_start":0.2655,"object_z_max":0.12169,"peak_contact_force":0.13646,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10502.0,"raw_peak_contact_force":0.37667,"subtask_id":"lift_clear","tcp_end":[0.49658,-0.02184,0.15166],"tcp_start":[0.5003,-0.02195,0.04991],"tcp_to_object_dist_end":0.03198,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":515.0,"n_steps_budget":1000.0,"object_pos_end":[0.55202,0.1364,0.16925],"object_pos_start":[0.50838,-0.02298,0.12195],"object_to_goal_dist_end":0.05494,"object_to_goal_dist_start":0.20638,"object_z_max":0.16916,"peak_contact_force":0.12451,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9857.0,"raw_peak_contact_force":0.2352,"subtask_id":"place_goal","tcp_end":[0.54649,0.13751,0.20494],"tcp_start":[0.49658,-0.02184,0.15166],"tcp_to_object_dist_end":0.03614,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53977,0.13998,0.02084],"object_pos_start":[0.55202,0.1364,0.16925],"object_to_goal_dist_end":0.202,"object_to_goal_dist_start":0.05494,"object_z_max":0.16925,"peak_contact_force":0.30044,"phase_name":"place_release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1276.0,"raw_peak_contact_force":1.73072,"tcp_end":[0.54143,0.13656,0.22769],"tcp_start":[0.54649,0.13751,0.20494],"tcp_to_object_dist_end":0.20688,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":395.0,"n_steps_budget":840.0,"object_pos_end":[0.52659,0.13263,0.02602],"object_pos_start":[0.53977,0.13998,0.02084],"object_to_goal_dist_end":0.1988,"object_to_goal_dist_start":0.202,"object_z_max":0.02804,"peak_contact_force":0.12264,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1505.0,"raw_peak_contact_force":0.29348,"tcp_end":[0.53967,0.13602,0.34257],"tcp_start":[0.54143,0.13656,0.22769],"tcp_to_object_dist_end":0.31684,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90385,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.205,"descend_grasp.descend_height":0.01359,"grasp_1.grasp_time":1.6595,"lift_object.lift_distance":0.11327,"place_release.release_time":0.99857,"retract_after_place.retract_distance":0.10445,"transport_to_goal.transport_z":0.02949},"optimized_scores":{"best_composite_score":0.17554,"best_fitness_score":0.67554,"best_task_score":0.43472},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":168.0,"contact_point_centroid":[0.54752,0.22688,-0.00737],"force_p95":1.16579,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.44221,"mean_force":0.41562,"phase_index":5.0,"phase_name":"place_release","phase_type":"release","tcp_position_centroid":[0.55018,0.22787,0.17857]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.49906,0.04117,-0.00162],"force_p95":0.32564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40929,"mean_force":0.07673,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48751,0.04226,0.05139]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3512.0,"contact_point_centroid":[0.48799,0.02314,0.08847],"force_p95":0.14309,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37695,"mean_force":0.08852,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4854,0.04207,0.09019]},{"body_a":"world","body_b":"grasp_target","contact_count":1179.0,"contact_point_centroid":[0.53749,0.22884,-0.00205],"force_p95":0.20122,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.31086,"mean_force":0.12808,"phase_index":6.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.54763,0.22671,0.23188]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":501.0,"contact_point_centroid":[0.55874,0.24818,0.15835],"force_p95":0.15917,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30718,"mean_force":0.10304,"phase_index":5.0,"phase_name":"place_release","phase_type":"release","tcp_position_centroid":[0.55371,0.22964,0.163]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5352.0,"contact_point_centroid":[0.48691,0.0604,0.09323],"force_p95":0.11298,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29223,"mean_force":0.06403,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48536,0.04207,0.09279]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":598.0,"contact_point_centroid":[0.55868,0.2117,0.15911],"force_p95":0.11434,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24819,"mean_force":0.07999,"phase_index":5.0,"phase_name":"place_release","phase_type":"release","tcp_position_centroid":[0.55383,0.2297,0.16321]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04498,-0.00225],"force_p95":0.19238,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.239,"mean_force":0.14001,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48999,0.0425,0.05074]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4867.0,"contact_point_centroid":[0.52546,0.12208,0.15024],"force_p95":0.13961,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22921,"mean_force":0.10748,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52077,0.14041,0.15357]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5912.0,"contact_point_centroid":[0.52025,0.14593,0.1498],"force_p95":0.13431,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22314,"mean_force":0.09142,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51588,0.12779,0.15179]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3624.0,"contact_point_centroid":[0.49065,0.02324,0.04953],"force_p95":0.11007,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14031,"mean_force":0.06221,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48888,0.0424,0.04955]},{"body_a":"world","body_b":"grasp_target","contact_count":484.0,"contact_point_centroid":[0.50118,0.04505,-0.00174],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12364,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49901,0.01458,0.27585]},{"body_a":"world","body_b":"grasp_target","contact_count":1440.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49701,0.03715,0.15446]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5392.0,"contact_point_centroid":[0.48864,0.06122,0.05063],"force_p95":0.07291,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07819,"mean_force":0.03987,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48889,0.0424,0.04956]}],"total_contact_groups":14},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.53641,0.22912,0.02602],"final_tcp_position":[0.5477,0.2267,0.27284],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.44221,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":122.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12255,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":484.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.4985,0.03142,0.24933],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":360.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1440.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_contact","tcp_end":[0.49713,0.0431,0.05883],"tcp_start":[0.4985,0.03142,0.24933],"tcp_to_object_dist_end":0.03312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50116,0.04314,0.02498],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24398,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.1936,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10816.0,"raw_peak_contact_force":0.239,"subtask_id":"grasp_contact","tcp_end":[0.48885,0.0424,0.04952],"tcp_start":[0.49713,0.0431,0.05883],"tcp_to_object_dist_end":0.02746,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":296.0,"n_steps_budget":720.0,"object_pos_end":[0.49733,0.04385,0.11423],"object_pos_start":[0.50116,0.04314,0.02498],"object_to_goal_dist_end":0.2144,"object_to_goal_dist_start":0.24398,"object_z_max":0.11396,"peak_contact_force":0.14101,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8950.0,"raw_peak_contact_force":0.40929,"subtask_id":"lift_clear","tcp_end":[0.48515,0.04205,0.14315],"tcp_start":[0.48885,0.0424,0.04952],"tcp_to_object_dist_end":0.03143,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":589.0,"n_steps_budget":1000.0,"object_pos_end":[0.56055,0.23126,0.13069],"object_pos_start":[0.49733,0.04385,0.11423],"object_to_goal_dist_end":0.02141,"object_to_goal_dist_start":0.2144,"object_z_max":0.13067,"peak_contact_force":0.14167,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10779.0,"raw_peak_contact_force":0.22921,"subtask_id":"place_goal","tcp_end":[0.55569,0.22988,0.16648],"tcp_start":[0.48515,0.04205,0.14315],"tcp_to_object_dist_end":0.03615,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54898,0.22163,0.02579],"object_pos_start":[0.56055,0.23126,0.13069],"object_to_goal_dist_end":0.12416,"object_to_goal_dist_start":0.02141,"object_z_max":0.13069,"peak_contact_force":0.31166,"phase_name":"place_release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1267.0,"raw_peak_contact_force":1.44221,"tcp_end":[0.55011,0.22785,0.18804],"tcp_start":[0.55569,0.22988,0.16648],"tcp_to_object_dist_end":0.16238,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":310.0,"n_steps_budget":660.0,"object_pos_end":[0.53641,0.22912,0.02602],"object_pos_start":[0.54898,0.22163,0.02579],"object_to_goal_dist_end":0.12496,"object_to_goal_dist_start":0.12416,"object_z_max":0.02739,"peak_contact_force":0.12267,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1179.0,"raw_peak_contact_force":0.31086,"tcp_end":[0.5477,0.2267,0.27284],"tcp_start":[0.55011,0.22785,0.18804],"tcp_to_object_dist_end":0.24709,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91018,"average_solve_count":167.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.15509,"descend_grasp.descend_height":0.01069,"grasp_1.grasp_time":1.43605,"lift_object.lift_distance":0.17057,"place_release.release_time":0.8663,"retract_after_place.retract_distance":0.08,"transport_to_goal.transport_z":-0.01205},"optimized_scores":{"best_composite_score":0.11601,"best_fitness_score":0.61601,"best_task_score":0.30764},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":215.0,"contact_point_centroid":[0.62455,0.12764,-0.00652],"force_p95":1.2854,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.51509,"mean_force":0.34874,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.61071,0.14011,0.17203]},{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.47412,-0.01889,-0.00139],"force_p95":0.39605,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41672,"mean_force":0.09555,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46374,-0.01924,0.04902]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6415.0,"contact_point_centroid":[0.52854,0.02893,0.18529],"force_p95":0.11984,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26563,"mean_force":0.07659,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52242,0.0472,0.18561]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7958.0,"contact_point_centroid":[0.46345,-0.0381,0.1143],"force_p95":0.10441,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26273,"mean_force":0.06376,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46152,-0.01916,0.11342]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7259.0,"contact_point_centroid":[0.46362,-0.00016,0.1149],"force_p95":0.10844,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26147,"mean_force":0.06866,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46152,-0.01916,0.11417]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5096.0,"contact_point_centroid":[0.52499,0.06183,0.18657],"force_p95":0.15022,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25563,"mean_force":0.09195,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5186,0.04315,0.18622]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47618,-0.02009,-0.00208],"force_p95":0.14449,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19448,"mean_force":0.12846,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.466,-0.01929,0.04872]},{"body_a":"world","body_b":"grasp_target","contact_count":740.0,"contact_point_centroid":[0.47616,-0.02015,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12329,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48957,-0.00745,0.25396]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.62537,0.12827,-0.00195],"force_p95":0.12711,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12886,"mean_force":0.11964,"phase_index":5.0,"phase_name":"place_release","phase_type":"release","tcp_position_centroid":[0.61297,0.14622,0.17146]},{"body_a":"world","body_b":"grasp_target","contact_count":1136.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47503,-0.01757,0.13063]},{"body_a":"world","body_b":"grasp_target","contact_count":960.0,"contact_point_centroid":[0.62537,0.12827,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.60878,0.14501,0.22049]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4830.0,"contact_point_centroid":[0.46442,-1e-05,0.04801],"force_p95":0.06912,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10643,"mean_force":0.04513,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46493,-0.01926,0.04765]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5420.0,"contact_point_centroid":[0.46426,-0.03848,0.0484],"force_p95":0.06543,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06796,"mean_force":0.04083,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46493,-0.01926,0.04765]},{"body_a":"left_finger","body_b":"right_finger","contact_count":206.0,"contact_point_centroid":[0.61568,0.14712,0.17009],"force_p95":0.0156,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0165,"mean_force":0.01131,"phase_index":5.0,"phase_name":"place_release","phase_type":"release","tcp_position_centroid":[0.61558,0.14711,0.16757]}],"total_contact_groups":14},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62537,0.12827,0.01602],"final_tcp_position":[0.60849,0.1449,0.25121],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.51509,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":186.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":740.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.47876,-0.01582,0.20442],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17847,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":284.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1136.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_contact","tcp_end":[0.47292,-0.01943,0.05604],"tcp_start":[0.47876,-0.01582,0.20442],"tcp_to_object_dist_end":0.0302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4761,-0.01954,0.02571],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28821,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14314,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12050.0,"raw_peak_contact_force":0.19448,"subtask_id":"grasp_contact","tcp_end":[0.4649,-0.01926,0.04762],"tcp_start":[0.47292,-0.01943,0.05604],"tcp_to_object_dist_end":0.0246,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":464.0,"n_steps_budget":1000.0,"object_pos_end":[0.47569,-0.0195,0.17171],"object_pos_start":[0.4761,-0.01954,0.02571],"object_to_goal_dist_end":0.23774,"object_to_goal_dist_start":0.28821,"object_z_max":0.17143,"peak_contact_force":0.10056,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15291.0,"raw_peak_contact_force":0.41672,"subtask_id":"lift_clear","tcp_end":[0.46172,-0.01916,0.19871],"tcp_start":[0.4649,-0.01926,0.04762],"tcp_to_object_dist_end":0.0304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":637.0,"n_steps_budget":1000.0,"object_pos_end":[0.62564,0.12719,0.0151],"object_pos_start":[0.47569,-0.0195,0.17171],"object_to_goal_dist_end":0.17792,"object_to_goal_dist_start":0.23774,"object_z_max":0.17195,"peak_contact_force":0.09138,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11726.0,"raw_peak_contact_force":1.51509,"subtask_id":"place_goal","tcp_end":[0.61723,0.14699,0.17102],"tcp_start":[0.46172,-0.01916,0.19871],"tcp_to_object_dist_end":0.1574,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62537,0.12827,0.01602],"object_pos_start":[0.62564,0.12719,0.0151],"object_to_goal_dist_end":0.17683,"object_to_goal_dist_start":0.17792,"object_z_max":0.01665,"peak_contact_force":0.12263,"phase_name":"place_release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1006.0,"raw_peak_contact_force":0.12886,"tcp_end":[0.61135,0.14573,0.19098],"tcp_start":[0.61723,0.14699,0.17102],"tcp_to_object_dist_end":0.17638,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":240.0,"n_steps_budget":600.0,"object_pos_end":[0.62537,0.12827,0.01602],"object_pos_start":[0.62537,0.12827,0.01602],"object_to_goal_dist_end":0.17683,"object_to_goal_dist_start":0.17683,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":960.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60849,0.1449,0.25121],"tcp_start":[0.61135,0.14573,0.19098],"tcp_to_object_dist_end":0.23638,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```