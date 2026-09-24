## Search State

- **Seed**: 8
- **Iteration**: 7 / 15

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

## Current Skill (Q=-0.061) — your mutation base

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
    - 0.0
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
- id: release
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
    orientation:
      mode: keep_current
  parameters:
    release_duration:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.3
      binds_to:
      - path: duration.max_time
        mode: replace
  subtask_id: place_goal
- id: retract
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_place_speed: status=consumed; consumers=generator.speed (replace)
    - place_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.061
- **task_score** (E): 0.291
- **fitness_score**: 0.619  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.680

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1587 |
| descend_to_grasp | 1.00 | 1.00 | 0.1040 |
| grasp | 1.00 | 1.00 | 0.0125 |
| lift | 1.00 | 1.00 | 0.1146 |
| approach_goal | 1.00 | 1.00 | 0.2343 |
| descend_to_place | 1.00 | 0.67 | 0.0307 |
| release | 1.00 | 1.00 | 0.0201 |
| retract | 1.00 | 1.00 | 0.0802 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.148) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.516, -0.001, 0.148)→(0.516, -0.001, 0.044) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 6.689 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.516, -0.001, 0.044)→(0.508, -0.001, 0.034) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 43.000 | 0.149 | 0.218 |
| lift | lift | 1.00 / step_budget | (0.508, -0.001, 0.034)→(0.516, -0.001, 0.149) | (0.522, -0.001, 0.026)→(0.529, -0.001, 0.136) | 0.289→0.234 | 1.00 / 33.333 | 0.089 | 0.467 |
| approach_goal | approach | 1.00 / step_budget | (0.516, -0.001, 0.149)→(0.601, 0.195, 0.241) | (0.529, -0.001, 0.136)→(0.608, 0.196, 0.221) | 0.234→0.020 | 1.00 / 31.667 | 0.113 | 0.133 |
| descend_to_place | descend | 1.00 / step_budget | (0.601, 0.195, 0.241)→(0.603, 0.202, 0.211) | (0.608, 0.196, 0.221)→(0.615, 0.198, 0.150) | 0.020→0.057 | 0.67 / 22.000 | 0.056 | 0.212 |
| release | release | 1.00 / step_budget | (0.603, 0.202, 0.211)→(0.598, 0.200, 0.230) | (0.615, 0.198, 0.150)→(0.612, 0.199, 0.015) | 0.057→0.190 | 1.00 / 3.667 | 0.161 | 1.775 |
| retract | retract | 1.00 / step_budget | (0.598, 0.200, 0.230)→(0.596, 0.199, 0.311) | (0.612, 0.199, 0.015)→(0.607, 0.201, 0.019) | 0.190→0.187 | 1.00 / 4.000 | 0.123 | 0.172 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.340
- phase_score: 0.569
- phase_breakdown.place_goal_score: 0.568
- phase_breakdown.lift_object_score: 0.352
- phase_breakdown.approach_object_score: 0.673
- phase_breakdown.approach_goal_score: 0.673
- phase_breakdown.grasp_object_score: 0.579
- grasp_place_fitness: 0.641

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.641
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.340
- **Median Q (composite search score)**: -0.063
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.403


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.72651,"average_solve_count":479.0,"average_success_count":479.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.01526,"approach_object.approach_speed":0.09247,"descend_to_grasp.descend_speed":0.00849,"descend_to_grasp.grasp_offset_z":0.00058,"descend_to_place.descend_place_speed":0.09132,"descend_to_place.place_tolerance":0.04847,"lift.lift_height":0.14591,"lift.lift_speed":0.02416,"release.release_duration":0.56027,"retract.retract_speed":0.03508},"optimized_scores":{"best_composite_score":-0.0804,"best_fitness_score":0.5996,"best_task_score":0.23906},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":153.0,"contact_point_centroid":[0.5842,0.2211,-0.00914],"force_p95":1.57182,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.72866,"mean_force":0.52954,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5721,0.22188,0.25105]},{"body_a":"world","body_b":"grasp_target","contact_count":110.0,"contact_point_centroid":[0.47915,0.04621,-0.00168],"force_p95":0.46114,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53356,"mean_force":0.21672,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46926,0.04661,0.02818]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48277,0.0484,-0.00219],"force_p95":0.17544,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26438,"mean_force":0.13695,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47144,0.04685,0.02839]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9053.0,"contact_point_centroid":[0.47242,0.06564,0.08948],"force_p95":0.07935,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25485,"mean_force":0.05234,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47225,0.04646,0.08767]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9322.0,"contact_point_centroid":[0.4721,0.02731,0.08862],"force_p95":0.07611,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.217,"mean_force":0.05,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.47217,0.04646,0.08685]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1052.0,"contact_point_centroid":[0.57466,0.20409,0.23445],"force_p95":0.07975,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17082,"mean_force":0.05084,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57496,0.2233,0.23294]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1283.0,"contact_point_centroid":[0.57523,0.24234,0.23339],"force_p95":0.07227,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15921,"mean_force":0.04349,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57497,0.22331,0.23296]},{"body_a":"world","body_b":"grasp_target","contact_count":1200.0,"contact_point_centroid":[0.4827,0.04873,-0.00189],"force_p95":0.13608,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49078,0.02004,0.22555]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1868.0,"contact_point_centroid":[0.57556,0.23987,0.25352],"force_p95":0.07444,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13486,"mean_force":0.05127,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57476,0.22068,0.25256]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4993.0,"contact_point_centroid":[0.47012,0.0275,0.0302],"force_p95":0.07154,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12853,"mean_force":0.04309,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47031,0.04674,0.02725]},{"body_a":"world","body_b":"grasp_target","contact_count":1368.0,"contact_point_centroid":[0.58646,0.22109,-0.00207],"force_p95":0.12441,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12502,"mean_force":0.11761,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.57039,0.22105,0.29587]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1703.0,"contact_point_centroid":[0.5756,0.20157,0.25501],"force_p95":0.07962,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12457,"mean_force":0.05408,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57474,0.22063,0.25288]},{"body_a":"world","body_b":"grasp_target","contact_count":1664.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47862,0.04442,0.09137]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17286.0,"contact_point_centroid":[0.52608,0.11639,0.2111],"force_p95":0.06943,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08862,"mean_force":0.04637,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52619,0.13554,0.20909]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5484.0,"contact_point_centroid":[0.47004,0.06611,0.02958],"force_p95":0.07319,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08402,"mean_force":0.04172,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47032,0.04674,0.02726]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16714.0,"contact_point_centroid":[0.52569,0.15401,0.21021],"force_p95":0.0697,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08114,"mean_force":0.04824,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52577,0.13481,0.20861]}],"total_contact_groups":16},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58646,0.22109,0.01602],"final_tcp_position":[0.57055,0.22103,0.33723],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":19.82089,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":301.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1200.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48209,0.04168,0.14841],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12259,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":416.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":19.82089,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1664.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.47814,0.0475,0.03523],"tcp_start":[0.48209,0.04168,0.14841],"tcp_to_object_dist_end":0.01035,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4826,0.04693,0.02536],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29159,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16687,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12277.0,"raw_peak_contact_force":0.26438,"subtask_id":"grasp_object","tcp_end":[0.47029,0.04673,0.02723],"tcp_start":[0.47814,0.0475,0.03523],"tcp_to_object_dist_end":0.01246,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":451.0,"n_steps_budget":1000.0,"object_pos_end":[0.48849,0.04664,0.14735],"object_pos_start":[0.4826,0.04693,0.02536],"object_to_goal_dist_end":0.22099,"object_to_goal_dist_start":0.29159,"object_z_max":0.14707,"peak_contact_force":0.07778,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18485.0,"raw_peak_contact_force":0.53356,"subtask_id":"lift_object","tcp_end":[0.47778,0.04655,0.15192],"tcp_start":[0.47029,0.04673,0.02723],"tcp_to_object_dist_end":0.01165,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":806.0,"n_steps_budget":1000.0,"object_pos_end":[0.58255,0.21809,0.25485],"object_pos_start":[0.48849,0.04664,0.14735],"object_to_goal_dist_end":0.02665,"object_to_goal_dist_start":0.22099,"object_z_max":0.25473,"peak_contact_force":0.06838,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34000.0,"raw_peak_contact_force":0.08862,"subtask_id":"approach_goal","tcp_end":[0.57394,0.21815,0.26567],"tcp_start":[0.47778,0.04655,0.15192],"tcp_to_object_dist_end":0.01382,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":94.0,"n_steps_budget":1000.0,"object_pos_end":[0.58654,0.22359,0.22534],"object_pos_start":[0.58255,0.21809,0.25485],"object_to_goal_dist_end":0.00872,"object_to_goal_dist_start":0.02665,"object_z_max":0.25489,"peak_contact_force":0.08052,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3571.0,"raw_peak_contact_force":0.13486,"subtask_id":"place_goal","tcp_end":[0.5765,0.22382,0.23698],"tcp_start":[0.57394,0.21815,0.26567],"tcp_to_object_dist_end":0.01538,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58573,0.22109,0.00855],"object_pos_start":[0.58654,0.22359,0.22534],"object_to_goal_dist_end":0.2221,"object_to_goal_dist_start":0.00872,"object_z_max":0.22534,"peak_contact_force":0.08506,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2488.0,"raw_peak_contact_force":1.72866,"subtask_id":"place_goal","tcp_end":[0.57208,0.22187,0.25712],"tcp_start":[0.5765,0.22382,0.23698],"tcp_to_object_dist_end":0.24894,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":342.0,"n_steps_budget":1000.0,"object_pos_end":[0.58646,0.22109,0.01602],"object_pos_start":[0.58573,0.22109,0.00855],"object_to_goal_dist_end":0.21465,"object_to_goal_dist_start":0.2221,"object_z_max":0.01668,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1368.0,"raw_peak_contact_force":0.12502,"tcp_end":[0.57055,0.22103,0.33723],"tcp_start":[0.57208,0.22187,0.25712],"tcp_to_object_dist_end":0.3216,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.71429,"average_solve_count":448.0,"average_success_count":448.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.07225,"approach_object.approach_speed":0.06778,"descend_to_grasp.descend_speed":0.03868,"descend_to_grasp.grasp_offset_z":0.01501,"descend_to_place.descend_place_speed":0.00597,"descend_to_place.place_tolerance":0.02297,"lift.lift_height":0.1596,"lift.lift_speed":0.01846,"release.release_duration":0.13504,"retract.retract_speed":0.17446},"optimized_scores":{"best_composite_score":-0.06287,"best_fitness_score":0.61713,"best_task_score":0.29526},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":153.0,"contact_point_centroid":[0.59333,0.2219,-0.00947],"force_p95":1.45067,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.81461,"mean_force":0.49948,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60008,0.21961,0.22499]},{"body_a":"world","body_b":"grasp_target","contact_count":112.0,"contact_point_centroid":[0.53374,-0.0205,-0.00156],"force_p95":0.34516,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38903,"mean_force":0.15676,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52162,-0.02065,0.03987]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1112.0,"contact_point_centroid":[0.60662,0.2402,0.21018],"force_p95":0.07917,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29089,"mean_force":0.04989,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60327,0.22109,0.20874]},{"body_a":"world","body_b":"grasp_target","contact_count":1173.0,"contact_point_centroid":[0.58801,0.22338,-0.00211],"force_p95":0.21848,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2693,"mean_force":0.12642,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.59802,0.21868,0.2742]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9267.0,"contact_point_centroid":[0.52576,-0.00146,0.10271],"force_p95":0.07979,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24052,"mean_force":0.05596,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5253,-0.02059,0.10014]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1072.0,"contact_point_centroid":[0.60602,0.20219,0.21031],"force_p95":0.08074,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23649,"mean_force":0.04955,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60332,0.22111,0.20887]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9906.0,"contact_point_centroid":[0.52559,-0.03966,0.10089],"force_p95":0.078,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23392,"mean_force":0.05333,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52516,-0.02059,0.09875]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1895.0,"contact_point_centroid":[0.60567,0.23608,0.23243],"force_p95":0.08733,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19071,"mean_force":0.06316,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60344,0.21694,0.23109]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53704,-0.02118,-0.00206],"force_p95":0.14047,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18238,"mean_force":0.1275,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52395,-0.0207,0.04057]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2160.0,"contact_point_centroid":[0.60563,0.19814,0.23176],"force_p95":0.07971,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17487,"mean_force":0.05465,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60344,0.21696,0.231]},{"body_a":"world","body_b":"grasp_target","contact_count":1252.0,"contact_point_centroid":[0.53702,-0.02132,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51299,-0.00879,0.22511]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4104.0,"contact_point_centroid":[0.52367,-0.00147,0.04189],"force_p95":0.07775,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13082,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52274,-0.02067,0.03917]},{"body_a":"world","body_b":"grasp_target","contact_count":1332.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52824,-0.0195,0.09746]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14967.0,"contact_point_centroid":[0.56812,0.08032,0.2059],"force_p95":0.07674,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09322,"mean_force":0.05287,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56702,0.0994,0.20367]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15324.0,"contact_point_centroid":[0.56881,0.12076,0.2065],"force_p95":0.07563,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09112,"mean_force":0.05152,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56771,0.10171,0.20443]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4912.0,"contact_point_centroid":[0.52366,-0.03976,0.04097],"force_p95":0.06989,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08208,"mean_force":0.04467,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52274,-0.02067,0.03918]}],"total_contact_groups":16},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.58657,0.22356,0.02602],"final_tcp_position":[0.59822,0.2187,0.31237],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.81461,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":314.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1252.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52841,-0.01826,0.14772],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12205,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":333.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1332.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53114,-0.02082,0.04901],"tcp_start":[0.52841,-0.01826,0.14772],"tcp_to_object_dist_end":0.02374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53693,-0.02067,0.02578],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31637,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13718,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10816.0,"raw_peak_contact_force":0.18238,"subtask_id":"grasp_object","tcp_end":[0.52271,-0.02067,0.03914],"tcp_start":[0.53114,-0.02082,0.04901],"tcp_to_object_dist_end":0.01952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":501.0,"n_steps_budget":1000.0,"object_pos_end":[0.5418,-0.02059,0.14897],"object_pos_start":[0.53693,-0.02067,0.02578],"object_to_goal_dist_end":0.26417,"object_to_goal_dist_start":0.31637,"object_z_max":0.14872,"peak_contact_force":0.08248,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19285.0,"raw_peak_contact_force":0.38903,"subtask_id":"lift_object","tcp_end":[0.53191,-0.02059,0.16618],"tcp_start":[0.52271,-0.02067,0.03914],"tcp_to_object_dist_end":0.01984,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":814.0,"n_steps_budget":1000.0,"object_pos_end":[0.60917,0.2143,0.22201],"object_pos_start":[0.5418,-0.02059,0.14897],"object_to_goal_dist_end":0.01989,"object_to_goal_dist_start":0.26417,"object_z_max":0.22193,"peak_contact_force":0.07091,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":30291.0,"raw_peak_contact_force":0.09322,"subtask_id":"approach_goal","tcp_end":[0.60379,0.21436,0.2442],"tcp_start":[0.53191,-0.02059,0.16618],"tcp_to_object_dist_end":0.02284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":124.0,"n_steps_budget":1000.0,"object_pos_end":[0.61154,0.2216,0.19027],"object_pos_start":[0.60917,0.2143,0.22201],"object_to_goal_dist_end":0.01825,"object_to_goal_dist_start":0.01989,"object_z_max":0.22201,"peak_contact_force":0.0874,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4055.0,"raw_peak_contact_force":0.19071,"subtask_id":"place_goal","tcp_end":[0.605,0.22157,0.21315],"tcp_start":[0.60379,0.21436,0.2442],"tcp_to_object_dist_end":0.0238,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6,0.21727,0.0207],"object_pos_start":[0.61154,0.2216,0.19027],"object_to_goal_dist_end":0.18729,"object_to_goal_dist_start":0.01825,"object_z_max":0.19027,"peak_contact_force":0.27576,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2337.0,"raw_peak_contact_force":1.81461,"subtask_id":"place_goal","tcp_end":[0.60005,0.2196,0.23224],"tcp_start":[0.605,0.22157,0.21315],"tcp_to_object_dist_end":0.21155,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":314.0,"n_steps_budget":600.0,"object_pos_end":[0.58657,0.22356,0.02602],"object_pos_start":[0.6,0.21727,0.0207],"object_to_goal_dist_end":0.18299,"object_to_goal_dist_start":0.18729,"object_z_max":0.02846,"peak_contact_force":0.12269,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1173.0,"raw_peak_contact_force":0.2693,"tcp_end":[0.59822,0.2187,0.31237],"tcp_start":[0.60005,0.2196,0.23224],"tcp_to_object_dist_end":0.28663,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58794,"average_solve_count":199.0,"average_success_count":199.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.approach_goal_speed":0.08253,"approach_object.approach_speed":0.1066,"descend_to_grasp.descend_speed":0.05128,"descend_to_grasp.grasp_offset_z":0.01319,"descend_to_place.descend_place_speed":0.03888,"descend_to_place.place_tolerance":0.02942,"lift.lift_height":0.12146,"lift.lift_speed":0.12519,"release.release_duration":0.5607,"retract.retract_speed":0.13311},"optimized_scores":{"best_composite_score":-0.0389,"best_fitness_score":0.6411,"best_task_score":0.33982},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":763.0,"contact_point_centroid":[0.64909,0.15738,-0.00352],"force_p95":0.67834,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.78244,"mean_force":0.19039,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62223,0.15883,0.18238]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.54385,-0.02819,-0.00136],"force_p95":0.44384,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47971,"mean_force":0.09054,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53003,-0.02826,0.03837]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":97.0,"contact_point_centroid":[0.63075,0.17261,0.2055],"force_p95":0.24831,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31172,"mean_force":0.17887,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62452,0.1546,0.21085]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4438.0,"contact_point_centroid":[0.53605,-0.00928,0.07933],"force_p95":0.11022,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2976,"mean_force":0.07366,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53311,-0.02819,0.07692]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4806.0,"contact_point_centroid":[0.53606,-0.04699,0.07752],"force_p95":0.10701,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2836,"mean_force":0.06968,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.533,-0.02819,0.07587]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":218.0,"contact_point_centroid":[0.63016,0.13827,0.20445],"force_p95":0.14318,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23922,"mean_force":0.07876,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62453,0.15483,0.20939]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7539.0,"contact_point_centroid":[0.58451,0.07791,0.16712],"force_p95":0.13604,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21641,"mean_force":0.08917,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57878,0.0594,0.16632]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54563,-0.02905,-0.00208],"force_p95":0.14727,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20592,"mean_force":0.12924,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53224,-0.02833,0.03841]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7896.0,"contact_point_centroid":[0.58509,0.04219,0.16769],"force_p95":0.11711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20166,"mean_force":0.08605,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.57942,0.06062,0.16698]},{"body_a":"world","body_b":"grasp_target","contact_count":1240.0,"contact_point_centroid":[0.5456,-0.02923,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51689,-0.01215,0.2245]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4093.0,"contact_point_centroid":[0.53205,-0.00909,0.03968],"force_p95":0.07885,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13545,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.531,-0.0283,0.03696]},{"body_a":"world","body_b":"grasp_target","contact_count":1268.0,"contact_point_centroid":[0.64919,0.15746,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61849,0.15766,0.24135]},{"body_a":"world","body_b":"grasp_target","contact_count":1332.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53631,-0.0268,0.096]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4943.0,"contact_point_centroid":[0.53202,-0.0474,0.03874],"force_p95":0.07108,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08006,"mean_force":0.04464,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53101,-0.0283,0.03697]}],"total_contact_groups":14},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.64919,0.15746,0.01602],"final_tcp_position":[0.61856,0.15763,0.28199],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.78244,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":311.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1240.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53617,-0.02516,0.14694],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12136,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":333.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1332.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_object","tcp_end":[0.53953,-0.02854,0.04711],"tcp_start":[0.53617,-0.02516,0.14694],"tcp_to_object_dist_end":0.02196,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54551,-0.02835,0.0257],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26048,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14262,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10836.0,"raw_peak_contact_force":0.20592,"subtask_id":"grasp_object","tcp_end":[0.53098,-0.02829,0.03693],"tcp_start":[0.53953,-0.02854,0.04711],"tcp_to_object_dist_end":0.01836,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":314.0,"n_steps_budget":600.0,"object_pos_end":[0.55677,-0.02828,0.11222],"object_pos_start":[0.54551,-0.02835,0.0257],"object_to_goal_dist_end":0.21749,"object_to_goal_dist_start":0.26048,"object_z_max":0.11199,"peak_contact_force":0.10588,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9328.0,"raw_peak_contact_force":0.47971,"subtask_id":"lift_object","tcp_end":[0.53975,-0.0282,0.12814],"tcp_start":[0.53098,-0.02829,0.03693],"tcp_to_object_dist_end":0.0233,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":13.0,"n_steps":725.0,"n_steps_budget":1000.0,"object_pos_end":[0.63249,0.15419,0.18713],"object_pos_start":[0.55677,-0.02828,0.11222],"object_to_goal_dist_end":0.01482,"object_to_goal_dist_start":0.21749,"object_z_max":0.18705,"peak_contact_force":0.19895,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15435.0,"raw_peak_contact_force":0.21641,"subtask_id":"approach_goal","tcp_end":[0.62453,0.15378,0.21283],"tcp_start":[0.53975,-0.0282,0.12814],"tcp_to_object_dist_end":0.02691,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":96.0,"n_steps_budget":1000.0,"object_pos_end":[0.64594,0.14846,0.03587],"object_pos_start":[0.63249,0.15419,0.18713],"object_to_goal_dist_end":0.14261,"object_to_goal_dist_start":0.01482,"object_z_max":0.18713,"peak_contact_force":0.0,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":315.0,"raw_peak_contact_force":0.31172,"subtask_id":"place_goal","tcp_end":[0.6267,0.15999,0.18273],"tcp_start":[0.62453,0.15378,0.21283],"tcp_to_object_dist_end":0.14856,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.64919,0.15746,0.01602],"object_pos_start":[0.64594,0.14846,0.03587],"object_to_goal_dist_end":0.1619,"object_to_goal_dist_start":0.14261,"object_z_max":0.03587,"peak_contact_force":0.12264,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":763.0,"raw_peak_contact_force":1.78244,"subtask_id":"place_goal","tcp_end":[0.62089,0.1584,0.20169],"tcp_start":[0.6267,0.15999,0.18273],"tcp_to_object_dist_end":0.18781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":317.0,"n_steps_budget":600.0,"object_pos_end":[0.64919,0.15746,0.01602],"object_pos_start":[0.64919,0.15746,0.01602],"object_to_goal_dist_end":0.1619,"object_to_goal_dist_start":0.1619,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1268.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.61856,0.15763,0.28199],"tcp_start":[0.62089,0.1584,0.20169],"tcp_to_object_dist_end":0.26773,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```