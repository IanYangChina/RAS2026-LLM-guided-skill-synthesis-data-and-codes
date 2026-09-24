## Search State

- **Seed**: 5
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
- Frozen realised-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`
- Frozen object start: [0.530500292374538, 0.030794078973649372, 0.03]
- Frozen task target: [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]
- Goal object position: (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.530500292374538, 0.030794078973649372, 0.03)
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
  frozen_object_start: [0.5305, 0.0308, 0.03]
  frozen_task_target: [0.6015, 0.1786, 0.1081]
  frozen_object_starts: {'grasp_target': [0.530500292374538, 0.030794078973649372, 0.03]}
  frozen_targets: {'place_target': [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d

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
| `object` | offset from object initial position (0.530500292374538, 0.030794078973649372, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.6015325561042142, 0.17858013800881417, 0.10808960535724847) | final destination targets |
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

## Current Skill (Q=0.093) — your mutation base

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
- id: descend_to_grasp
  anchor: object
  weight: 0.2
- id: lift_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.1
- id: approach_goal
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: place_object
  target_entity: object
  metric: goal_progress
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
    entity: grasp_target
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
      - 0.05
      - 0.2
      default: 0.1
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
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.015
    orientation:
      mode: keep_current
  subtask_id: descend_to_grasp
- id: grasp_action
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
    grasp_duration:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
- id: lift_object
  type: lift
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
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
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: lift_object
- id: approach_goal
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
    - 0.05
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_goal
- id: descend_to_place
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
    - 0.01
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    place_z_offset:
      type: scalar
      range:
      - 0.005
      - 0.025
      default: 0.01
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: place_object
- id: release_object
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
    release_duration:
      type: scalar
      range:
      - 0.15
      - 0.4
      default: 0.2
      binds_to:
      - path: duration.max_time
        mode: replace
- id: retract_after_place
  type: retract
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings: none
- **grasp_action** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **lift_object** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **approach_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.01], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract_after_place** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.093
- **task_score** (E): 0.392
- **fitness_score**: 0.673  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1553 |
| descend_to_grasp | 1.00 | 1.00 | 0.1085 |
| grasp_action | 1.00 | 1.00 | 0.0126 |
| lift_object | 1.00 | 1.00 | 0.1100 |
| approach_goal | 1.00 | 1.00 | 0.1936 |
| descend_to_place | 1.00 | 0.67 | 0.0191 |
| release_object | 1.00 | 1.00 | 0.0210 |
| retract_after_place | 1.00 | 1.00 | 0.0418 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.148) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, 0.016, 0.148)→(0.510, 0.018, 0.040) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_action | grasp | 1.00 / step_budget | (0.510, 0.018, 0.040)→(0.502, 0.017, 0.031) | (0.516, 0.018, 0.026)→(0.516, 0.017, 0.026) | 0.236→0.237 | 1.00 / 41.000 | 0.151 | 0.224 |
| lift_object | lift | 1.00 / step_budget | (0.502, 0.017, 0.031)→(0.510, 0.017, 0.140) | (0.516, 0.017, 0.026)→(0.529, 0.017, 0.129) | 0.237→0.194 | 1.00 / 23.333 | 55983.982 | 0.597 |
| approach_goal | approach | 1.00 / step_budget | (0.510, 0.017, 0.140)→(0.596, 0.168, 0.205) | (0.529, 0.017, 0.129)→(0.603, 0.173, 0.139) | 0.194→0.047 | 1.00 / 12.667 | 0.311 | 0.614 |
| descend_to_place | descend | 1.00 / step_budget | (0.596, 0.168, 0.205)→(0.599, 0.174, 0.187) | (0.603, 0.173, 0.139)→(0.605, 0.178, 0.124) | 0.047→0.044 | 0.67 / 6.667 | 0.113 | 0.393 |
| release_object | release | 1.00 / step_budget | (0.599, 0.174, 0.187)→(0.593, 0.172, 0.207) | (0.605, 0.178, 0.124)→(0.604, 0.185, 0.016) | 0.044→0.151 | 1.00 / 4.000 | 0.123 | 1.167 |
| retract_after_place | retract | 1.00 / step_budget | (0.593, 0.172, 0.207)→(0.600, 0.177, 0.248) | (0.604, 0.185, 0.016)→(0.604, 0.185, 0.016) | 0.151→0.151 | 1.00 / 4.000 | 0.123 | 0.125 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.540
- phase_score: 0.588
- phase_breakdown.approach_object_score: 0.672
- phase_breakdown.place_object_score: 0.145
- phase_breakdown.lift_object_score: 0.629
- phase_breakdown.approach_goal_score: 0.674
- phase_breakdown.descend_to_grasp_score: 0.796
- grasp_place_fitness: 0.747

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.747
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.540
- **Median Q (composite search score)**: 0.109
- **K-run variance**: 0.0045
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.255


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `181fdad61feb8a6d3dd6561c82dc2730a5598964bf30fa08b43615687239c379`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `eed1fc17ff57094d5189888f0dc8540ea7c165c4c73333e7487a550c7ded377e`; realized-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69186,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.07952,"approach_object.approach_speed":0.09665,"descend_to_place.place_speed":0.04926,"descend_to_place.place_z_offset":0.02041,"grasp_action.grasp_duration":1.01189,"lift_object.lift_height":0.15106,"lift_object.lift_speed":0.13317,"release_object.release_duration":0.25948},"optimized_scores":{"best_composite_score":0.16664,"best_fitness_score":0.74664,"best_task_score":0.54044},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":45.0,"contact_point_centroid":[0.59594,0.17433,-0.00821],"force_p95":1.4408,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.47443,"mean_force":0.95122,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58956,0.16126,0.15024]},{"body_a":"world","body_b":"grasp_target","contact_count":344.0,"contact_point_centroid":[0.59819,0.18473,-0.00381],"force_p95":0.38034,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63948,"mean_force":0.14253,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59198,0.16799,0.14003]},{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.52781,0.02858,-0.00143],"force_p95":0.58434,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63596,"mean_force":0.12513,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51516,0.02912,0.03146]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5620.0,"contact_point_centroid":[0.52221,0.01019,0.08994],"force_p95":0.11212,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33096,"mean_force":0.07679,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51856,0.02899,0.08779]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5852.0,"contact_point_centroid":[0.52181,0.04779,0.08666],"force_p95":0.11275,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32719,"mean_force":0.07492,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5183,0.02899,0.08474]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3196.0,"contact_point_centroid":[0.55226,0.05734,0.15085],"force_p95":0.17438,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25667,"mean_force":0.10307,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54666,0.07567,0.15247]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03049,-0.00214],"force_p95":0.16474,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24344,"mean_force":0.13375,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.51746,0.02929,0.03134]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3425.0,"contact_point_centroid":[0.55519,0.10104,0.14999],"force_p95":0.14746,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22016,"mean_force":0.09865,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55015,0.08283,0.15215]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4058.0,"contact_point_centroid":[0.51721,0.01001,0.03273],"force_p95":0.08135,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14992,"mean_force":0.05193,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.51625,0.02922,0.02999]},{"body_a":"world","body_b":"grasp_target","contact_count":1208.0,"contact_point_centroid":[0.5305,0.03079,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51055,0.01267,0.22514]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59815,0.18425,-0.00199],"force_p95":0.12436,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12794,"mean_force":0.12291,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58927,0.1709,0.13063]},{"body_a":"world","body_b":"grasp_target","contact_count":1004.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52285,0.02796,0.09377]},{"body_a":"world","body_b":"grasp_target","contact_count":708.0,"contact_point_centroid":[0.59815,0.18425,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.5908,0.17298,0.16932]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5016.0,"contact_point_centroid":[0.51713,0.04839,0.03178],"force_p95":0.07404,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08627,"mean_force":0.04466,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.51626,0.02922,0.03]},{"body_a":"left_finger","body_b":"right_finger","contact_count":131.0,"contact_point_centroid":[0.59371,0.17065,0.13558],"force_p95":0.01519,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01615,"mean_force":0.01238,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59316,0.17063,0.13321]},{"body_a":"left_finger","body_b":"right_finger","contact_count":227.0,"contact_point_centroid":[0.5928,0.17194,0.12882],"force_p95":0.0112,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01123,"mean_force":0.00992,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59227,0.17191,0.12659]}],"total_contact_groups":16},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59815,0.18425,0.01602],"final_tcp_position":[0.59548,0.17592,0.18943],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":303.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1208.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52307,0.0263,0.14786],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":251.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1004.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_to_grasp","tcp_end":[0.52487,0.02977,0.03986],"tcp_start":[0.52307,0.0263,0.14786],"tcp_to_object_dist_end":0.01497,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53041,0.0293,0.02552],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18483,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15604,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10874.0,"raw_peak_contact_force":0.24344,"tcp_end":[0.51622,0.02921,0.02995],"tcp_start":[0.52487,0.02977,0.03986],"tcp_to_object_dist_end":0.01486,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":415.0,"n_steps_budget":720.0,"object_pos_end":[0.54448,0.02935,0.14464],"object_pos_start":[0.53041,0.0293,0.02552],"object_to_goal_dist_end":0.16389,"object_to_goal_dist_start":0.18483,"object_z_max":0.14441,"peak_contact_force":167951.73011,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11551.0,"raw_peak_contact_force":0.63596,"subtask_id":"lift_object","tcp_end":[0.52544,0.02904,0.15745],"tcp_start":[0.51622,0.02921,0.02995],"tcp_to_object_dist_end":0.02295,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":435.0,"n_steps_budget":1000.0,"object_pos_end":[0.59742,0.17786,0.00051],"object_pos_start":[0.54448,0.02935,0.14464],"object_to_goal_dist_end":0.10766,"object_to_goal_dist_start":0.16389,"object_z_max":0.14483,"peak_contact_force":0.67978,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6666.0,"raw_peak_contact_force":1.47443,"subtask_id":"approach_goal","tcp_end":[0.59091,0.16394,0.1502],"tcp_start":[0.52544,0.02904,0.15745],"tcp_to_object_dist_end":0.15048,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":86.0,"n_steps_budget":1000.0,"object_pos_end":[0.5982,0.18445,0.01627],"object_pos_start":[0.59742,0.17786,0.00051],"object_to_goal_dist_end":0.09207,"object_to_goal_dist_start":0.10766,"object_z_max":0.01664,"peak_contact_force":0.1281,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":475.0,"raw_peak_contact_force":0.63948,"subtask_id":"place_object","tcp_end":[0.59408,0.17223,0.12989],"tcp_start":[0.59091,0.16394,0.1502],"tcp_to_object_dist_end":0.11435,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59815,0.18425,0.01602],"object_pos_start":[0.5982,0.18445,0.01627],"object_to_goal_dist_end":0.09231,"object_to_goal_dist_start":0.09207,"object_z_max":0.01627,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12794,"tcp_end":[0.58747,0.1703,0.1504],"tcp_start":[0.59408,0.17223,0.12989],"tcp_to_object_dist_end":0.13553,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":177.0,"n_steps_budget":600.0,"object_pos_end":[0.59815,0.18425,0.01602],"object_pos_start":[0.59815,0.18425,0.01602],"object_to_goal_dist_end":0.09231,"object_to_goal_dist_start":0.09231,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":708.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59548,0.17592,0.18943],"tcp_start":[0.58747,0.1703,0.1504],"tcp_to_object_dist_end":0.17363,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5dcdc1a4e2a8d4c3bb30f9ac92fb306bea0b16a8f449f4d02b0333754e50f910`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3445,"average_solve_count":209.0,"average_success_count":209.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.05786,"approach_object.approach_speed":0.15243,"descend_to_place.place_speed":0.0505,"descend_to_place.place_z_offset":0.01234,"grasp_action.grasp_duration":0.83033,"lift_object.lift_height":0.12636,"lift_object.lift_speed":0.11641,"release_object.release_duration":0.20115},"optimized_scores":{"best_composite_score":0.00399,"best_fitness_score":0.58399,"best_task_score":0.21254},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":339.0,"contact_point_centroid":[0.58526,0.19721,-0.00607],"force_p95":1.13373,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.78951,"mean_force":0.27888,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57797,0.18027,0.27467]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.50147,-0.01497,-0.00133],"force_p95":0.54882,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57141,"mean_force":0.12686,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48976,-0.01515,0.03244]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.58754,0.16381,0.25936],"force_p95":0.27036,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37471,"mean_force":0.18212,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58134,0.18167,0.26508]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":185.0,"contact_point_centroid":[0.58612,0.19819,0.25878],"force_p95":0.16187,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33162,"mean_force":0.0826,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58107,0.18158,0.26432]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5025.0,"contact_point_centroid":[0.49457,0.00394,0.07884],"force_p95":0.10727,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3144,"mean_force":0.06809,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49244,-0.01507,0.07638]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5526.0,"contact_point_centroid":[0.49452,-0.03395,0.07684],"force_p95":0.1033,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28787,"mean_force":0.06325,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49232,-0.01507,0.07514]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":408.0,"contact_point_centroid":[0.58579,0.16105,0.27158],"force_p95":0.19233,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22948,"mean_force":0.12292,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58087,0.17903,0.27614]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":442.0,"contact_point_centroid":[0.58587,0.19723,0.27087],"force_p95":0.13994,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22872,"mean_force":0.11422,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58091,0.17915,0.27568]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01551,-0.00205],"force_p95":0.13725,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17754,"mean_force":0.12665,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.4919,-0.01518,0.03231]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10343.0,"contact_point_centroid":[0.54249,0.10073,0.20578],"force_p95":0.12593,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16919,"mean_force":0.08247,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53816,0.08228,0.20649]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10538.0,"contact_point_centroid":[0.54059,0.05913,0.20223],"force_p95":0.12508,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16341,"mean_force":0.08185,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53609,0.0776,0.20275]},{"body_a":"world","body_b":"grasp_target","contact_count":1088.0,"contact_point_centroid":[0.50382,-0.01567,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49949,-0.00641,0.22601]},{"body_a":"world","body_b":"grasp_target","contact_count":696.0,"contact_point_centroid":[0.58489,0.19685,-0.00196],"force_p95":0.1272,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12826,"mean_force":0.12297,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.58027,0.18272,0.30705]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4101.0,"contact_point_centroid":[0.49125,0.00404,0.03386],"force_p95":0.07717,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12311,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.49074,-0.01516,0.03109]},{"body_a":"world","body_b":"grasp_target","contact_count":1028.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49844,-0.01426,0.09454]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4904.0,"contact_point_centroid":[0.4913,-0.03425,0.03294],"force_p95":0.06925,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09207,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.49075,-0.01516,0.0311]}],"total_contact_groups":16},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58489,0.19686,0.01602],"final_tcp_position":[0.58349,0.18536,0.32853],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.78951,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":273.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1088.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50006,-0.01333,0.1492],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12327,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":257.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_to_grasp","tcp_end":[0.49903,-0.01525,0.04],"tcp_start":[0.50006,-0.01333,0.1492],"tcp_to_object_dist_end":0.01479,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5037,-0.01507,0.02582],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31201,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13411,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10805.0,"raw_peak_contact_force":0.17754,"tcp_end":[0.49072,-0.01516,0.03106],"tcp_start":[0.49903,-0.01525,0.04],"tcp_to_object_dist_end":0.014,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":327.0,"n_steps_budget":660.0,"object_pos_end":[0.5165,-0.01501,0.12328],"object_pos_start":[0.5037,-0.01507,0.02582],"object_to_goal_dist_end":0.24805,"object_to_goal_dist_start":0.31201,"object_z_max":0.12302,"peak_contact_force":0.10855,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10628.0,"raw_peak_contact_force":0.57141,"subtask_id":"lift_object","tcp_end":[0.49842,-0.01502,0.13299],"tcp_start":[0.49072,-0.01516,0.03106],"tcp_to_object_dist_end":0.02052,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":905.0,"n_steps_budget":1000.0,"object_pos_end":[0.58632,0.17699,0.25852],"object_pos_start":[0.5165,-0.01501,0.12328],"object_to_goal_dist_end":0.01476,"object_to_goal_dist_start":0.24805,"object_z_max":0.25839,"peak_contact_force":0.12568,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20881.0,"raw_peak_contact_force":0.16919,"subtask_id":"approach_goal","tcp_end":[0.58043,0.1771,0.28241],"tcp_start":[0.49842,-0.01502,0.13299],"tcp_to_object_dist_end":0.02461,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":12.0,"n_steps":58.0,"n_steps_budget":1000.0,"object_pos_end":[0.58844,0.18133,0.24205],"object_pos_start":[0.58632,0.17699,0.25852],"object_to_goal_dist_end":0.00875,"object_to_goal_dist_start":0.01476,"object_z_max":0.25855,"peak_contact_force":0.21093,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":850.0,"raw_peak_contact_force":0.22948,"subtask_id":"place_object","tcp_end":[0.5819,0.18164,0.26661],"tcp_start":[0.58043,0.1771,0.28241],"tcp_to_object_dist_end":0.02543,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58489,0.19692,0.01677],"object_pos_start":[0.58844,0.18133,0.24205],"object_to_goal_dist_end":0.23155,"object_to_goal_dist_start":0.00875,"object_z_max":0.24205,"peak_contact_force":0.1234,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":600.0,"raw_peak_contact_force":1.78951,"tcp_end":[0.57794,0.18025,0.28702],"tcp_start":[0.5819,0.18164,0.26661],"tcp_to_object_dist_end":0.27086,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":174.0,"n_steps_budget":600.0,"object_pos_end":[0.58489,0.19686,0.01602],"object_pos_start":[0.58489,0.19692,0.01677],"object_to_goal_dist_end":0.2323,"object_to_goal_dist_start":0.23155,"object_z_max":0.01677,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":696.0,"raw_peak_contact_force":0.12826,"tcp_end":[0.58349,0.18536,0.32853],"tcp_start":[0.57794,0.18025,0.28702],"tcp_to_object_dist_end":0.31273,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `53da4dc33bcb1151bde99c46f4ec5d44dda63d23acc62ec623c12d4d0fb32574`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5445,"average_solve_count":191.0,"average_success_count":191.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.06618,"approach_object.approach_speed":0.10465,"descend_to_place.place_speed":0.03228,"descend_to_place.place_z_offset":0.01682,"grasp_action.grasp_duration":1.24253,"lift_object.lift_height":0.12396,"lift_object.lift_speed":0.08475,"release_object.release_duration":0.2293},"optimized_scores":{"best_composite_score":0.10882,"best_fitness_score":0.68882,"best_task_score":0.42312},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":648.0,"contact_point_centroid":[0.62915,0.1727,-0.00364],"force_p95":0.71955,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.58386,"mean_force":0.18552,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61443,0.16589,0.16527]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.51033,0.03672,-0.00149],"force_p95":0.47166,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58376,"mean_force":0.13558,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49809,0.03768,0.03205]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":297.0,"contact_point_centroid":[0.62179,0.18198,0.17198],"force_p95":0.20339,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31084,"mean_force":0.11988,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61676,0.16406,0.17745]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5457.0,"contact_point_centroid":[0.50309,0.05642,0.075],"force_p95":0.10742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30796,"mean_force":0.06704,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50062,0.03753,0.07318]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5031.0,"contact_point_centroid":[0.50337,0.01859,0.07758],"force_p95":0.10946,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3044,"mean_force":0.07072,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50082,0.03753,0.07521]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":259.0,"contact_point_centroid":[0.6218,0.14633,0.17271],"force_p95":0.20717,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2807,"mean_force":0.12408,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61671,0.16399,0.17777]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51258,0.03936,-0.00217],"force_p95":0.17357,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25086,"mean_force":0.13591,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50029,0.03789,0.03189]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6244.0,"contact_point_centroid":[0.56265,0.0786,0.15266],"force_p95":0.14352,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19907,"mean_force":0.09188,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55729,0.09692,0.1529]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6179.0,"contact_point_centroid":[0.56651,0.12007,0.15444],"force_p95":0.13462,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19839,"mean_force":0.0929,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56153,0.10169,0.15499]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3773.0,"contact_point_centroid":[0.50031,0.0186,0.03363],"force_p95":0.08629,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15546,"mean_force":0.05546,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.49912,0.0378,0.03063]},{"body_a":"world","body_b":"grasp_target","contact_count":1188.0,"contact_point_centroid":[0.51251,0.03972,-0.00189],"force_p95":0.13631,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50307,0.01635,0.22523]},{"body_a":"world","body_b":"grasp_target","contact_count":1016.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50642,0.0361,0.09385]},{"body_a":"world","body_b":"grasp_target","contact_count":780.0,"contact_point_centroid":[0.62913,0.17273,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12261,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.61726,0.16787,0.20448]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4960.0,"contact_point_centroid":[0.49987,0.05695,0.03247],"force_p95":0.07654,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08517,"mean_force":0.04533,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.49913,0.0378,0.03064]}],"total_contact_groups":14},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62913,0.17273,0.01602],"final_tcp_position":[0.62218,0.17037,0.22598],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.58386,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":298.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1188.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50759,0.03394,0.14805],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":254.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_to_grasp","tcp_end":[0.50749,0.03846,0.03986],"tcp_start":[0.50759,0.03394,0.14805],"tcp_to_object_dist_end":0.01478,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.03794,0.02543],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21371,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.16167,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10533.0,"raw_peak_contact_force":0.25086,"tcp_end":[0.49909,0.03779,0.03059],"tcp_start":[0.50749,0.03846,0.03986],"tcp_to_object_dist_end":0.01431,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":339.0,"n_steps_budget":900.0,"object_pos_end":[0.52546,0.03788,0.12034],"object_pos_start":[0.51243,0.03794,0.02543],"object_to_goal_dist_end":0.17078,"object_to_goal_dist_start":0.21371,"object_z_max":0.12009,"peak_contact_force":0.10841,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10572.0,"raw_peak_contact_force":0.58376,"subtask_id":"lift_object","tcp_end":[0.50692,0.03759,0.13039],"tcp_start":[0.49909,0.03779,0.03059],"tcp_to_object_dist_end":0.02109,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":605.0,"n_steps_budget":1000.0,"object_pos_end":[0.62415,0.1629,0.15916],"object_pos_start":[0.52546,0.03788,0.12034],"object_to_goal_dist_end":0.01744,"object_to_goal_dist_start":0.17078,"object_z_max":0.1591,"peak_contact_force":0.12859,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12423.0,"raw_peak_contact_force":0.19907,"subtask_id":"approach_goal","tcp_end":[0.6161,0.16269,0.18223],"tcp_start":[0.50692,0.03759,0.13039],"tcp_to_object_dist_end":0.02444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":69.0,"n_steps_budget":1000.0,"object_pos_end":[0.62801,0.16805,0.1127],"object_pos_start":[0.62415,0.1629,0.15916],"object_to_goal_dist_end":0.03264,"object_to_goal_dist_start":0.01744,"object_z_max":0.15916,"peak_contact_force":0.0,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":556.0,"raw_peak_contact_force":0.31084,"subtask_id":"place_object","tcp_end":[0.61959,0.16737,0.16466],"tcp_start":[0.6161,0.16269,0.18223],"tcp_to_object_dist_end":0.05264,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62913,0.17273,0.01601],"object_pos_start":[0.62801,0.16805,0.1127],"object_to_goal_dist_end":0.12902,"object_to_goal_dist_start":0.03264,"object_z_max":0.1127,"peak_contact_force":0.1226,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":648.0,"raw_peak_contact_force":1.58386,"tcp_end":[0.61353,0.16559,0.18404],"tcp_start":[0.61959,0.16737,0.16466],"tcp_to_object_dist_end":0.1689,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":195.0,"n_steps_budget":600.0,"object_pos_end":[0.62913,0.17273,0.01602],"object_pos_start":[0.62913,0.17273,0.01601],"object_to_goal_dist_end":0.12902,"object_to_goal_dist_start":0.12902,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":780.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62218,0.17037,0.22598],"tcp_start":[0.61353,0.16559,0.18404],"tcp_to_object_dist_end":0.21009,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```