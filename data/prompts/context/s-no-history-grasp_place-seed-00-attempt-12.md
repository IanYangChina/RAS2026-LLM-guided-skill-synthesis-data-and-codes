## Search State

- **Seed**: 0
- **Iteration**: 13 / 15

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

## Current Skill (Q=-0.120) — your mutation base

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

- **Composite score**: -0.120
- **task_score** (E): 0.335
- **fitness_score**: 0.630  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.750

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.0714 |
| descend_grasp | 1.00 | 1.00 | 0.1784 |
| grasp_1 | 1.00 | 1.00 | 0.0123 |
| lift_object | 1.00 | 1.00 | 0.1098 |
| transport_to_goal | 1.00 | 0.33 | 0.2098 |
| place_release | 1.00 | 1.00 | 0.0219 |
| retract_after_place | 1.00 | 1.00 | 0.1122 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.001, 0.234) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_grasp | descend | 1.00 / step_budget | (0.496, 0.001, 0.234)→(0.493, 0.001, 0.056) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.493, 0.001, 0.056)→(0.485, 0.000, 0.047) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 | 1.00 / 45.000 | 0.155 | 0.212 |
| lift_object | lift | 1.00 / step_budget | (0.485, 0.000, 0.047)→(0.481, 0.000, 0.157) | (0.497, 0.001, 0.026)→(0.495, 0.000, 0.130) | 0.266→0.221 | 1.00 / 23.667 | 0.106 | 0.450 |
| transport_to_goal | approach | 1.00 / step_budget | (0.481, 0.000, 0.157)→(0.574, 0.173, 0.218) | (0.495, 0.000, 0.130)→(0.577, 0.166, 0.099) | 0.221→0.092 | 0.33 / 2.667 | 0.041 | 0.686 |
| place_release | release | 1.00 / step_budget | (0.574, 0.173, 0.218)→(0.570, 0.171, 0.239) | (0.577, 0.166, 0.099)→(0.584, 0.172, 0.019) | 0.092→0.169 | 1.00 / 4.000 | 0.124 | 1.218 |
| retract_after_place | retract | 1.00 / step_budget | (0.570, 0.171, 0.239)→(0.568, 0.171, 0.351) | (0.584, 0.172, 0.019)→(0.584, 0.172, 0.019) | 0.169→0.169 | 1.00 / 4.000 | 0.123 | 0.124 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.446
- phase_score: 0.598
- phase_breakdown.grasp_contact_score: 0.686
- phase_breakdown.place_goal_score: 0.782
- phase_breakdown.lift_clear_score: 0.466
- phase_breakdown.reach_object_score: 0.118
- grasp_place_fitness: 0.686

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.686
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.446
- **Median Q (composite search score)**: -0.132
- **K-run variance**: 0.0018
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.369


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80882,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.18553,"approach_object.approach_speed":0.0608,"descend_grasp.descend_height":0.01228,"descend_grasp.descend_speed":0.09067,"grasp_1.grasp_time":0.54401,"lift_object.lift_distance":0.11545,"lift_object.lift_speed":0.22403,"place_release.release_time":0.55272,"retract_after_place.retract_distance":0.12837,"retract_after_place.retract_speed":0.29978,"transport_to_goal.transport_speed":0.3124,"transport_to_goal.transport_z":0.0082},"optimized_scores":{"best_composite_score":-0.16517,"best_fitness_score":0.58483,"best_task_score":0.24864},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":562.0,"contact_point_centroid":[0.54624,0.11843,-0.00383],"force_p95":0.76405,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.49931,"mean_force":0.19477,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5394,0.11543,0.20609]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.51096,-0.02144,-0.00139],"force_p95":0.39389,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4054,"mean_force":0.08951,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49911,-0.0219,0.04919]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2909.0,"contact_point_centroid":[0.5142,0.03954,0.15981],"force_p95":0.14248,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2971,"mean_force":0.08556,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50819,0.021,0.16059]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4438.0,"contact_point_centroid":[0.49947,-0.00287,0.08954],"force_p95":0.11358,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29347,"mean_force":0.07336,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49691,-0.02183,0.08905]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4857.0,"contact_point_centroid":[0.49936,-0.04073,0.08963],"force_p95":0.11053,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28339,"mean_force":0.06833,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49692,-0.02183,0.08894]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2792.0,"contact_point_centroid":[0.51327,-0.00038,0.15894],"force_p95":0.14501,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27238,"mean_force":0.08653,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50733,0.0182,0.15931]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51372,-0.02294,-0.00209],"force_p95":0.14885,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20166,"mean_force":0.12958,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50153,-0.02196,0.04906]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4342.0,"contact_point_centroid":[0.50104,-0.00274,0.04899],"force_p95":0.0745,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1432,"mean_force":0.04951,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5004,-0.02193,0.04781]},{"body_a":"world","body_b":"grasp_target","contact_count":576.0,"contact_point_centroid":[0.5137,-0.02302,-0.00178],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12347,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50316,-0.00773,0.26822]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54612,0.11858,-0.00199],"force_p95":0.12272,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12305,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_release","phase_type":"release","tcp_position_centroid":[0.54353,0.13777,0.21968]},{"body_a":"world","body_b":"grasp_target","contact_count":1328.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.50741,-0.01936,0.14562]},{"body_a":"world","body_b":"grasp_target","contact_count":1428.0,"contact_point_centroid":[0.54612,0.11858,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.54035,0.13681,0.29375]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4949.0,"contact_point_centroid":[0.50098,-0.04109,0.04892],"force_p95":0.071,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07277,"mean_force":0.04437,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5004,-0.02193,0.04781]},{"body_a":"left_finger","body_b":"right_finger","contact_count":364.0,"contact_point_centroid":[0.54288,0.12462,0.21293],"force_p95":0.01391,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01567,"mean_force":0.01102,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54252,0.12462,0.21062]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.54604,0.13856,0.21719],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01095,"mean_force":0.00996,"phase_index":5.0,"phase_name":"place_release","phase_type":"release","tcp_position_centroid":[0.5458,0.13855,0.21495]}],"total_contact_groups":15},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.54612,0.11858,0.01602],"final_tcp_position":[0.54064,0.13684,0.34842],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":1.49931,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":145.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":576.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.50752,-0.0167,0.2331],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20726,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":332.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1328.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_contact","tcp_end":[0.50884,-0.0221,0.0575],"tcp_start":[0.50752,-0.0167,0.2331],"tcp_to_object_dist_end":0.03187,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51364,-0.02226,0.02566],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26539,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.14668,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11091.0,"raw_peak_contact_force":0.20166,"subtask_id":"grasp_contact","tcp_end":[0.50037,-0.02193,0.04777],"tcp_start":[0.50884,-0.0221,0.0575],"tcp_to_object_dist_end":0.02579,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":299.0,"n_steps_budget":600.0,"object_pos_end":[0.5106,-0.02216,0.11632],"object_pos_start":[0.51364,-0.02226,0.02566],"object_to_goal_dist_end":0.20801,"object_to_goal_dist_start":0.26539,"object_z_max":0.11605,"peak_contact_force":0.10607,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9372.0,"raw_peak_contact_force":0.4054,"subtask_id":"lift_clear","tcp_end":[0.49668,-0.02182,0.14358],"tcp_start":[0.50037,-0.02193,0.04777],"tcp_to_object_dist_end":0.03061,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":474.0,"n_steps_budget":1000.0,"object_pos_end":[0.54612,0.11858,0.016],"object_pos_start":[0.5106,-0.02216,0.11632],"object_to_goal_dist_end":0.20878,"object_to_goal_dist_start":0.20801,"object_z_max":0.14816,"peak_contact_force":0.12309,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6627.0,"raw_peak_contact_force":1.49931,"subtask_id":"place_goal","tcp_end":[0.54705,0.13828,0.21725],"tcp_start":[0.49668,-0.02182,0.14358],"tcp_to_object_dist_end":0.20221,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54612,0.11858,0.01602],"object_pos_start":[0.54612,0.11858,0.016],"object_to_goal_dist_end":0.20876,"object_to_goal_dist_start":0.20878,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12305,"tcp_end":[0.54223,0.13735,0.23998],"tcp_start":[0.54705,0.13828,0.21725],"tcp_to_object_dist_end":0.22478,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":357.0,"n_steps_budget":600.0,"object_pos_end":[0.54612,0.11858,0.01602],"object_pos_start":[0.54612,0.11858,0.01602],"object_to_goal_dist_end":0.20876,"object_to_goal_dist_start":0.20876,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1428.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.54064,0.13684,0.34842],"tcp_start":[0.54223,0.13735,0.23998],"tcp_to_object_dist_end":0.33295,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.10656,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.1907,"approach_object.approach_speed":0.09313,"descend_grasp.descend_height":0.01007,"descend_grasp.descend_speed":0.10379,"grasp_1.grasp_time":1.84504,"lift_object.lift_distance":0.13821,"lift_object.lift_speed":0.14468,"place_release.release_time":0.66508,"retract_after_place.retract_distance":0.14156,"retract_after_place.retract_speed":0.30168,"transport_to_goal.transport_speed":0.31838,"transport_to_goal.transport_z":0.06857},"optimized_scores":{"best_composite_score":-0.06449,"best_fitness_score":0.68551,"best_task_score":0.44573},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":690.0,"contact_point_centroid":[0.55863,0.25351,-0.00341],"force_p95":0.67758,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.67221,"mean_force":0.18263,"phase_index":5.0,"phase_name":"place_release","phase_type":"release","tcp_position_centroid":[0.55229,0.22897,0.20666]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.49882,0.04232,-0.00158],"force_p95":0.40184,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50888,"mean_force":0.09615,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48752,0.04239,0.04756]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5970.0,"contact_point_centroid":[0.48796,0.06114,0.09781],"force_p95":0.11232,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32994,"mean_force":0.06692,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48543,0.04219,0.09644]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5385.0,"contact_point_centroid":[0.48738,0.02323,0.09823],"force_p95":0.11395,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31178,"mean_force":0.07084,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4854,0.04219,0.09745]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4437.0,"contact_point_centroid":[0.51836,0.13814,0.17707],"force_p95":0.13984,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25965,"mean_force":0.09757,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51346,0.11991,0.1792]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50126,0.04489,-0.00221],"force_p95":0.17904,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2383,"mean_force":0.13759,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48991,0.04261,0.04732]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4392.0,"contact_point_centroid":[0.51981,0.10542,0.17765],"force_p95":0.14099,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23545,"mean_force":0.09837,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51499,0.12381,0.18013]},{"body_a":"world","body_b":"grasp_target","contact_count":572.0,"contact_point_centroid":[0.50118,0.04505,-0.00178],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12348,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49905,0.01546,0.2694]},{"body_a":"world","body_b":"grasp_target","contact_count":1636.0,"contact_point_centroid":[0.55866,0.25359,-0.00199],"force_p95":0.123,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12451,"mean_force":0.12262,"phase_index":6.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.54964,0.22764,0.28639]},{"body_a":"world","body_b":"grasp_target","contact_count":1364.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.49701,0.03805,0.14618]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4802.0,"contact_point_centroid":[0.48804,0.02323,0.04821],"force_p95":0.07366,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11788,"mean_force":0.04519,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4888,0.04251,0.04613]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5858.0,"contact_point_centroid":[0.4893,0.06181,0.04889],"force_p95":0.07159,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07434,"mean_force":0.03866,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4888,0.04251,0.04614]}],"total_contact_groups":12},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.55866,0.25359,0.02602],"final_tcp_position":[0.55008,0.22775,0.34779],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.67221,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":144.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":572.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.49863,0.03311,0.23621],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21054,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":341.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1364.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_contact","tcp_end":[0.4971,0.04322,0.05542],"tcp_start":[0.49863,0.03311,0.23621],"tcp_to_object_dist_end":0.02974,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50118,0.04334,0.02526],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24368,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.1748,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12460.0,"raw_peak_contact_force":0.2383,"subtask_id":"grasp_contact","tcp_end":[0.48877,0.04251,0.0461],"tcp_start":[0.4971,0.04322,0.05542],"tcp_to_object_dist_end":0.02427,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":357.0,"n_steps_budget":630.0,"object_pos_end":[0.49965,0.0429,0.13718],"object_pos_start":[0.50118,0.04334,0.02526],"object_to_goal_dist_end":0.21231,"object_to_goal_dist_start":0.24368,"object_z_max":0.13692,"peak_contact_force":0.10503,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11431.0,"raw_peak_contact_force":0.50888,"subtask_id":"lift_clear","tcp_end":[0.48538,0.04219,0.16462],"tcp_start":[0.48877,0.04251,0.0461],"tcp_to_object_dist_end":0.03093,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":510.0,"n_steps_budget":1000.0,"object_pos_end":[0.55944,0.23533,0.10174],"object_pos_start":[0.49965,0.0429,0.13718],"object_to_goal_dist_end":0.04631,"object_to_goal_dist_start":0.21231,"object_z_max":0.16171,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8829.0,"raw_peak_contact_force":0.25965,"subtask_id":"place_goal","tcp_end":[0.55632,0.23037,0.20463],"tcp_start":[0.48538,0.04219,0.16462],"tcp_to_object_dist_end":0.10306,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55863,0.25358,0.02602],"object_pos_start":[0.55944,0.23533,0.10174],"object_to_goal_dist_end":0.12121,"object_to_goal_dist_start":0.04631,"object_z_max":0.10174,"peak_contact_force":0.12446,"phase_name":"place_release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":690.0,"raw_peak_contact_force":1.67221,"tcp_end":[0.55144,0.22855,0.22611],"tcp_start":[0.55632,0.23037,0.20463],"tcp_to_object_dist_end":0.20179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":409.0,"n_steps_budget":600.0,"object_pos_end":[0.55866,0.25359,0.02602],"object_pos_start":[0.55863,0.25358,0.02602],"object_to_goal_dist_end":0.12121,"object_to_goal_dist_start":0.12121,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1636.0,"raw_peak_contact_force":0.12451,"tcp_end":[0.55008,0.22775,0.34779],"tcp_start":[0.55144,0.22855,0.22611],"tcp_to_object_dist_end":0.32292,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82069,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_height":0.185,"approach_object.approach_speed":0.18767,"descend_grasp.descend_height":0.01003,"descend_grasp.descend_speed":0.06778,"grasp_1.grasp_time":1.3889,"lift_object.lift_distance":0.13436,"lift_object.lift_speed":0.11545,"place_release.release_time":0.54912,"retract_after_place.retract_distance":0.12648,"retract_after_place.retract_speed":0.22107,"transport_to_goal.transport_speed":0.36811,"transport_to_goal.transport_z":0.05361},"optimized_scores":{"best_composite_score":-0.13182,"best_fitness_score":0.61818,"best_task_score":0.31029},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":500.0,"contact_point_centroid":[0.64801,0.1431,-0.00423],"force_p95":0.91134,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.8576,"mean_force":0.22091,"phase_index":5.0,"phase_name":"place_release","phase_type":"release","tcp_position_centroid":[0.61545,0.14825,0.23405]},{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.47411,-0.01888,-0.00141],"force_p95":0.41385,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43662,"mean_force":0.10408,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46372,-0.01917,0.04826]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6207.0,"contact_point_centroid":[0.54015,0.04239,0.19105],"force_p95":0.14219,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30012,"mean_force":0.09165,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53526,0.06058,0.1929]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5393.0,"contact_point_centroid":[0.53715,0.07582,0.18928],"force_p95":0.1572,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28753,"mean_force":0.10521,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53223,0.0574,0.19154]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5743.0,"contact_point_centroid":[0.46315,-5e-05,0.09913],"force_p95":0.10789,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26743,"mean_force":0.06593,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46156,-0.0191,0.09828]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6290.0,"contact_point_centroid":[0.46305,-0.0381,0.09897],"force_p95":0.10335,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26706,"mean_force":0.06129,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46156,-0.0191,0.09799]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47618,-0.02009,-0.00208],"force_p95":0.1461,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19628,"mean_force":0.12885,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46596,-0.01922,0.04801]},{"body_a":"world","body_b":"grasp_target","contact_count":536.0,"contact_point_centroid":[0.47616,-0.02015,-0.00176],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12354,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49066,-0.00676,0.26847]},{"body_a":"world","body_b":"grasp_target","contact_count":1584.0,"contact_point_centroid":[0.64784,0.14277,-0.00199],"force_p95":0.12298,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12408,"mean_force":0.12266,"phase_index":6.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.61353,0.1476,0.30354]},{"body_a":"world","body_b":"grasp_target","contact_count":1404.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_grasp","phase_type":"descend","tcp_position_centroid":[0.47585,-0.0169,0.14497]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4830.0,"contact_point_centroid":[0.46441,5e-05,0.04754],"force_p95":0.06952,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10738,"mean_force":0.04511,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46489,-0.0192,0.04693]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5418.0,"contact_point_centroid":[0.46424,-0.03842,0.04791],"force_p95":0.06575,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06931,"mean_force":0.04087,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46489,-0.0192,0.04694]}],"total_contact_groups":12},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.64784,0.14277,0.01602],"final_tcp_position":[0.61398,0.14766,0.35728],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.8576,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":135.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":536.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.48063,-0.01456,0.23365],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20775,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":351.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1404.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_contact","tcp_end":[0.47287,-0.01936,0.05531],"tcp_start":[0.48063,-0.01456,0.23365],"tcp_to_object_dist_end":0.02948,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47609,-0.0195,0.02569],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.2882,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14452,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12048.0,"raw_peak_contact_force":0.19628,"subtask_id":"grasp_contact","tcp_end":[0.46486,-0.0192,0.0469],"tcp_start":[0.47287,-0.01936,0.05531],"tcp_to_object_dist_end":0.024,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":346.0,"n_steps_budget":750.0,"object_pos_end":[0.47588,-0.01938,0.13624],"object_pos_start":[0.47609,-0.0195,0.02569],"object_to_goal_dist_end":0.24284,"object_to_goal_dist_start":0.2882,"object_z_max":0.13597,"peak_contact_force":0.10599,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12107.0,"raw_peak_contact_force":0.43662,"subtask_id":"lift_clear","tcp_end":[0.46149,-0.01909,0.16182],"tcp_start":[0.46486,-0.0192,0.0469],"tcp_to_object_dist_end":0.02935,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":612.0,"n_steps_budget":1000.0,"object_pos_end":[0.62551,0.14323,0.18035],"object_pos_start":[0.47588,-0.01938,0.13624],"object_to_goal_dist_end":0.01957,"object_to_goal_dist_start":0.24284,"object_z_max":0.18865,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11600.0,"raw_peak_contact_force":0.30012,"subtask_id":"place_goal","tcp_end":[0.61983,0.14926,0.23079],"tcp_start":[0.46149,-0.01909,0.16182],"tcp_to_object_dist_end":0.05111,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6479,0.14275,0.01602],"object_pos_start":[0.62551,0.14323,0.18035],"object_to_goal_dist_end":0.17555,"object_to_goal_dist_start":0.01957,"object_z_max":0.18035,"peak_contact_force":0.12421,"phase_name":"place_release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":500.0,"raw_peak_contact_force":1.8576,"tcp_end":[0.61524,0.14817,0.2507],"tcp_start":[0.61983,0.14926,0.23079],"tcp_to_object_dist_end":0.23701,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":396.0,"n_steps_budget":600.0,"object_pos_end":[0.64784,0.14277,0.01602],"object_pos_start":[0.6479,0.14275,0.01602],"object_to_goal_dist_end":0.17554,"object_to_goal_dist_start":0.17555,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1584.0,"raw_peak_contact_force":0.12408,"tcp_end":[0.61398,0.14766,0.35728],"tcp_start":[0.61524,0.14817,0.2507],"tcp_to_object_dist_end":0.34298,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```