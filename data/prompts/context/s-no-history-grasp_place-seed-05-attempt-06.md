## Search State

- **Seed**: 5
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

## Current Skill (Q=0.193) — your mutation base

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
  control: position_control
  termination: time_limit
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
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
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
    tolerance: 0.015
    orientation:
      mode: keep_current
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
      - 0.3
      - 1.5
      default: 0.5
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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings: none
- **release_object** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
- **retract_after_place** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.193
- **task_score** (E): 0.391
- **fitness_score**: 0.673  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1553 |
| descend_to_grasp | 1.00 | 1.00 | 0.1086 |
| grasp_action | 1.00 | 1.00 | 0.0126 |
| lift_object | 1.00 | 1.00 | 0.1075 |
| approach_goal | 1.00 | 1.00 | 0.1931 |
| descend_to_place | 1.00 | 1.00 | 0.0269 |
| release_object | 1.00 | 1.00 | 0.0207 |
| retract_after_place | 1.00 | 1.00 | 0.0507 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.148) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, 0.016, 0.148)→(0.510, 0.018, 0.040) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_action | grasp | 1.00 / step_budget | (0.510, 0.018, 0.040)→(0.502, 0.017, 0.030) | (0.516, 0.018, 0.026)→(0.516, 0.017, 0.026) | 0.236→0.237 | 1.00 / 41.000 | 0.151 | 0.224 |
| lift_object | lift | 1.00 / time_limit | (0.502, 0.017, 0.030)→(0.511, 0.017, 0.138) | (0.516, 0.017, 0.026)→(0.528, 0.017, 0.124) | 0.237→0.195 | 1.00 / 22.667 | 56508.312 | 0.597 |
| approach_goal | approach | 1.00 / step_budget | (0.511, 0.017, 0.138)→(0.596, 0.168, 0.205) | (0.528, 0.017, 0.124)→(0.604, 0.167, 0.051) | 0.195→0.126 | 1.00 / 11.000 | 0.348 | 1.156 |
| descend_to_place | descend | 1.00 / step_budget | (0.596, 0.168, 0.205)→(0.599, 0.174, 0.179) | (0.604, 0.167, 0.051)→(0.606, 0.169, 0.054) | 0.126→0.114 | 1.00 / 11.000 | 182005.734 | 0.393 |
| release_object | release | 1.00 / step_budget | (0.599, 0.174, 0.179)→(0.593, 0.172, 0.198) | (0.606, 0.169, 0.054)→(0.605, 0.170, 0.016) | 0.114→0.152 | 1.00 / 4.000 | 0.117 | 0.578 |
| retract_after_place | retract | 1.00 / step_budget | (0.593, 0.172, 0.198)→(0.601, 0.177, 0.248) | (0.605, 0.170, 0.016)→(0.605, 0.171, 0.016) | 0.152→0.152 | 1.00 / 4.000 | 0.123 | 0.124 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.540
- phase_score: 0.562
- phase_breakdown.approach_object_score: 0.671
- phase_breakdown.place_object_score: 0.137
- phase_breakdown.lift_object_score: 0.384
- phase_breakdown.approach_goal_score: 0.673
- phase_breakdown.descend_to_grasp_score: 0.799
- grasp_place_fitness: 0.747

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.747
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.540
- **Median Q (composite search score)**: 0.209
- **K-run variance**: 0.0046
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.352


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62286,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.06403,"approach_object.approach_speed":0.10949,"grasp_action.grasp_duration":1.21477,"lift_object.lift_height":0.12111,"lift_object.lift_speed":0.14058,"release_object.release_duration":1.01419},"optimized_scores":{"best_composite_score":0.26668,"best_fitness_score":0.74668,"best_task_score":0.54042},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":65.0,"contact_point_centroid":[0.5966,0.17849,-0.00805],"force_p95":1.26004,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.43967,"mean_force":0.76512,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.58991,0.16212,0.14761]},{"body_a":"world","body_b":"grasp_target","contact_count":288.0,"contact_point_centroid":[0.52832,0.02907,-0.00159],"force_p95":0.30564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59443,"mean_force":0.1058,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5142,0.02906,0.03069]},{"body_a":"world","body_b":"grasp_target","contact_count":308.0,"contact_point_centroid":[0.59884,0.18502,-0.00353],"force_p95":0.2662,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45514,"mean_force":0.12413,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5923,0.16831,0.1346]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8542.0,"contact_point_centroid":[0.52046,0.04779,0.07003],"force_p95":0.10674,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30847,"mean_force":0.06964,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51735,0.02897,0.06817]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7996.0,"contact_point_centroid":[0.52081,0.01012,0.07248],"force_p95":0.10998,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30411,"mean_force":0.07264,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51758,0.02897,0.07027]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03049,-0.00214],"force_p95":0.16471,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24374,"mean_force":0.13374,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.51743,0.0293,0.03112]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3453.0,"contact_point_centroid":[0.55278,0.05976,0.13379],"force_p95":0.17501,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23193,"mean_force":0.10428,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54749,0.07803,0.13551]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3948.0,"contact_point_centroid":[0.5554,0.10323,0.13399],"force_p95":0.14633,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21438,"mean_force":0.09474,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55094,0.0851,0.13637]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4058.0,"contact_point_centroid":[0.51719,0.01001,0.03252],"force_p95":0.08135,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14988,"mean_force":0.05193,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.51622,0.02922,0.02977]},{"body_a":"world","body_b":"grasp_target","contact_count":1196.0,"contact_point_centroid":[0.5305,0.03079,-0.00189],"force_p95":0.13615,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51052,0.01267,0.22511]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59881,0.18466,-0.00198],"force_p95":0.12481,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12814,"mean_force":0.12292,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58885,0.17055,0.11914]},{"body_a":"world","body_b":"grasp_target","contact_count":1008.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52282,0.02795,0.09368]},{"body_a":"world","body_b":"grasp_target","contact_count":860.0,"contact_point_centroid":[0.59881,0.18466,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.59051,0.17284,0.16359]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5016.0,"contact_point_centroid":[0.51711,0.04839,0.03157],"force_p95":0.07403,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08641,"mean_force":0.04467,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.51623,0.02922,0.02978]},{"body_a":"left_finger","body_b":"right_finger","contact_count":107.0,"contact_point_centroid":[0.59378,0.17067,0.12664],"force_p95":0.0151,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01598,"mean_force":0.01276,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59331,0.17064,0.12402]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.59228,0.1716,0.11707],"force_p95":0.01136,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01142,"mean_force":0.01017,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59187,0.17157,0.11493]}],"total_contact_groups":16},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59881,0.18466,0.01602],"final_tcp_position":[0.59572,0.17608,0.18919],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273009.10542,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":300.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1196.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52302,0.02627,0.14797],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1008.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_to_grasp","tcp_end":[0.52483,0.02977,0.03963],"tcp_start":[0.52302,0.02627,0.14797],"tcp_to_object_dist_end":0.01478,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53041,0.02929,0.02552],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18483,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15599,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10874.0,"raw_peak_contact_force":0.24374,"tcp_end":[0.51619,0.02921,0.02974],"tcp_start":[0.52483,0.02977,0.03963],"tcp_to_object_dist_end":0.01483,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.54245,0.02924,0.11857],"object_pos_start":[0.53041,0.02929,0.02552],"object_to_goal_dist_end":0.16094,"object_to_goal_dist_start":0.18483,"object_z_max":0.11843,"peak_contact_force":0.11224,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16826.0,"raw_peak_contact_force":0.59443,"subtask_id":"lift_object","tcp_end":[0.52533,0.02902,0.1324],"tcp_start":[0.51619,0.02921,0.02974],"tcp_to_object_dist_end":0.022,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":483.0,"n_steps_budget":1000.0,"object_pos_end":[0.59831,0.17936,0.00146],"object_pos_start":[0.54245,0.02924,0.11857],"object_to_goal_dist_end":0.10668,"object_to_goal_dist_start":0.16094,"object_z_max":0.11995,"peak_contact_force":0.48588,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7466.0,"raw_peak_contact_force":1.43967,"subtask_id":"approach_goal","tcp_end":[0.59133,0.16493,0.14805],"tcp_start":[0.52533,0.02902,0.1324],"tcp_to_object_dist_end":0.14746,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":77.0,"n_steps_budget":1000.0,"object_pos_end":[0.59886,0.18486,0.01633],"object_pos_start":[0.59831,0.17936,0.00146],"object_to_goal_dist_end":0.09202,"object_to_goal_dist_start":0.10668,"object_z_max":0.01661,"peak_contact_force":273009.10542,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":415.0,"raw_peak_contact_force":0.45514,"subtask_id":"place_object","tcp_end":[0.59406,0.17198,0.11887],"tcp_start":[0.59133,0.16493,0.14805],"tcp_to_object_dist_end":0.10345,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59881,0.18466,0.01602],"object_pos_start":[0.59886,0.18486,0.01633],"object_to_goal_dist_end":0.09231,"object_to_goal_dist_start":0.09202,"object_z_max":0.01633,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12814,"tcp_end":[0.58701,0.16994,0.13897],"tcp_start":[0.59406,0.17198,0.11887],"tcp_to_object_dist_end":0.12439,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":215.0,"n_steps_budget":600.0,"object_pos_end":[0.59881,0.18466,0.01602],"object_pos_start":[0.59881,0.18466,0.01602],"object_to_goal_dist_end":0.09231,"object_to_goal_dist_start":0.09231,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":860.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59572,0.17608,0.18919],"tcp_start":[0.58701,0.16994,0.13897],"tcp_to_object_dist_end":0.17341,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80676,"average_solve_count":207.0,"average_success_count":207.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.07242,"approach_object.approach_speed":0.08525,"grasp_action.grasp_duration":1.45175,"lift_object.lift_height":0.11299,"lift_object.lift_speed":0.17754,"release_object.release_duration":0.93914},"optimized_scores":{"best_composite_score":0.10251,"best_fitness_score":0.58251,"best_task_score":0.20949},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":90.0,"contact_point_centroid":[0.59229,0.15406,-0.00998],"force_p95":1.48359,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.81426,"mean_force":0.76355,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5794,0.17486,0.28026]},{"body_a":"world","body_b":"grasp_target","contact_count":288.0,"contact_point_centroid":[0.50175,-0.01503,-0.00147],"force_p95":0.28618,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56493,"mean_force":0.09871,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48881,-0.01513,0.03199]},{"body_a":"world","body_b":"grasp_target","contact_count":228.0,"contact_point_centroid":[0.59258,0.15418,-0.00476],"force_p95":0.2778,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42627,"mean_force":0.10502,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58109,0.1794,0.27302]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8457.0,"contact_point_centroid":[0.49415,0.00388,0.07063],"force_p95":0.1067,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31103,"mean_force":0.0686,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49171,-0.01507,0.06839]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9350.0,"contact_point_centroid":[0.49395,-0.0339,0.06846],"force_p95":0.10227,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28515,"mean_force":0.06327,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49155,-0.01507,0.06678]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7658.0,"contact_point_centroid":[0.53531,0.08311,0.18664],"force_p95":0.13324,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23493,"mean_force":0.09021,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53056,0.06478,0.18814]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7665.0,"contact_point_centroid":[0.53543,0.04642,0.18677],"force_p95":0.12943,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18995,"mean_force":0.09023,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5306,0.06476,0.18819]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01551,-0.00205],"force_p95":0.13723,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17746,"mean_force":0.12665,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.49193,-0.01518,0.03231]},{"body_a":"world","body_b":"grasp_target","contact_count":1156.0,"contact_point_centroid":[0.50382,-0.01567,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12305,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49954,-0.00641,0.22612]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59262,0.15473,-0.00195],"force_p95":0.12857,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13027,"mean_force":0.12269,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57889,0.18076,0.2611]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4101.0,"contact_point_centroid":[0.49127,0.00404,0.03386],"force_p95":0.07716,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12308,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.49077,-0.01517,0.0311]},{"body_a":"world","body_b":"grasp_target","contact_count":1028.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49853,-0.01427,0.09455]},{"body_a":"world","body_b":"grasp_target","contact_count":776.0,"contact_point_centroid":[0.59262,0.15472,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.58022,0.18281,0.30412]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4904.0,"contact_point_centroid":[0.49132,-0.03425,0.03295],"force_p95":0.06924,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09203,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.49078,-0.01517,0.0311]},{"body_a":"left_finger","body_b":"right_finger","contact_count":177.0,"contact_point_centroid":[0.58138,0.17998,0.27237],"force_p95":0.01415,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01509,"mean_force":0.01174,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58129,0.17996,0.27002]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.58106,0.18152,0.25921],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.011,"mean_force":0.01003,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58067,0.1815,0.25688]}],"total_contact_groups":16},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.59262,0.15472,0.01602],"final_tcp_position":[0.58355,0.18548,0.32863],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273007.9517,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":290.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1156.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50022,-0.01334,0.14921],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12327,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":257.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_to_grasp","tcp_end":[0.49905,-0.01525,0.04001],"tcp_start":[0.50022,-0.01334,0.14921],"tcp_to_object_dist_end":0.01478,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5037,-0.01507,0.02582],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31201,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13409,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10805.0,"raw_peak_contact_force":0.17746,"tcp_end":[0.49074,-0.01516,0.03107],"tcp_start":[0.49905,-0.01525,0.04001],"tcp_to_object_dist_end":0.01397,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.51518,-0.0149,0.11229],"object_pos_start":[0.5037,-0.01507,0.02582],"object_to_goal_dist_end":0.25404,"object_to_goal_dist_start":0.31201,"object_z_max":0.11217,"peak_contact_force":1573.09317,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18095.0,"raw_peak_contact_force":0.56493,"subtask_id":"lift_object","tcp_end":[0.49874,-0.01501,0.1258],"tcp_start":[0.49074,-0.01516,0.03107],"tcp_to_object_dist_end":0.02128,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":876.0,"n_steps_budget":1000.0,"object_pos_end":[0.59294,0.15884,-0.00445],"object_pos_start":[0.51518,-0.0149,0.11229],"object_to_goal_dist_end":0.25425,"object_to_goal_dist_start":0.25404,"object_z_max":0.23353,"peak_contact_force":0.45901,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15413.0,"raw_peak_contact_force":1.81426,"subtask_id":"approach_goal","tcp_end":[0.58045,0.17726,0.28226],"tcp_start":[0.49874,-0.01501,0.1258],"tcp_to_object_dist_end":0.28757,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":57.0,"n_steps_budget":1000.0,"object_pos_end":[0.59263,0.1548,0.01687],"object_pos_start":[0.59294,0.15884,-0.00445],"object_to_goal_dist_end":0.23361,"object_to_goal_dist_start":0.25425,"object_z_max":0.01687,"peak_contact_force":273007.9517,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":405.0,"raw_peak_contact_force":0.42627,"subtask_id":"place_object","tcp_end":[0.58207,0.18179,0.2608],"tcp_start":[0.58045,0.17726,0.28226],"tcp_to_object_dist_end":0.24564,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59262,0.15472,0.01602],"object_pos_start":[0.59263,0.1548,0.01687],"object_to_goal_dist_end":0.23446,"object_to_goal_dist_start":0.23361,"object_z_max":0.01687,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.13027,"tcp_end":[0.5779,0.18034,0.28093],"tcp_start":[0.58207,0.18179,0.2608],"tcp_to_object_dist_end":0.26655,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":194.0,"n_steps_budget":600.0,"object_pos_end":[0.59262,0.15472,0.01602],"object_pos_start":[0.59262,0.15472,0.01602],"object_to_goal_dist_end":0.23446,"object_to_goal_dist_start":0.23446,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":776.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58355,0.18548,0.32863],"tcp_start":[0.5779,0.18034,0.28093],"tcp_to_object_dist_end":0.31425,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94406,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.17955,"approach_object.approach_speed":0.10647,"grasp_action.grasp_duration":1.72228,"lift_object.lift_height":0.14448,"lift_object.lift_speed":0.16261,"release_object.release_duration":0.57214},"optimized_scores":{"best_composite_score":0.20868,"best_fitness_score":0.68868,"best_task_score":0.42284},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":200.0,"contact_point_centroid":[0.61779,0.17242,-0.00577],"force_p95":1.203,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.4746,"mean_force":0.35889,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61295,0.16504,0.16687]},{"body_a":"world","body_b":"grasp_target","contact_count":238.0,"contact_point_centroid":[0.50972,0.03735,-0.00153],"force_p95":0.33494,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63185,"mean_force":0.10426,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49732,0.03762,0.03179]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":646.0,"contact_point_centroid":[0.62247,0.18453,0.14787],"force_p95":0.30073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.50609,"mean_force":0.11509,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61661,0.16624,0.15031]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":582.0,"contact_point_centroid":[0.62198,0.14816,0.14869],"force_p95":0.25771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44525,"mean_force":0.11129,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61681,0.16631,0.15063]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8301.0,"contact_point_centroid":[0.50321,0.01863,0.08268],"force_p95":0.1085,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32083,"mean_force":0.07024,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50039,0.03752,0.08044]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8912.0,"contact_point_centroid":[0.50278,0.05639,0.07925],"force_p95":0.10729,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32062,"mean_force":0.06716,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50012,0.03752,0.07741]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":679.0,"contact_point_centroid":[0.62261,0.18231,0.17169],"force_p95":0.1459,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29732,"mean_force":0.10175,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61672,0.16376,0.17267]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":620.0,"contact_point_centroid":[0.6222,0.14545,0.17093],"force_p95":0.14665,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28363,"mean_force":0.10735,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61684,0.1639,0.1719]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51258,0.03936,-0.00217],"force_p95":0.17357,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25086,"mean_force":0.13591,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50029,0.03789,0.03189]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4750.0,"contact_point_centroid":[0.56785,0.08224,0.16967],"force_p95":0.12968,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21324,"mean_force":0.09259,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56183,0.10091,0.16789]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5803.0,"contact_point_centroid":[0.56919,0.12133,0.1691],"force_p95":0.11231,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19157,"mean_force":0.07841,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.56352,0.10288,0.16833]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3773.0,"contact_point_centroid":[0.50031,0.0186,0.03363],"force_p95":0.08629,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15546,"mean_force":0.05546,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.49912,0.0378,0.03063]},{"body_a":"world","body_b":"grasp_target","contact_count":1188.0,"contact_point_centroid":[0.51251,0.03972,-0.00189],"force_p95":0.13631,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50307,0.01635,0.22523]},{"body_a":"world","body_b":"grasp_target","contact_count":908.0,"contact_point_centroid":[0.62231,0.17242,-0.00197],"force_p95":0.12601,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12746,"mean_force":0.12021,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.61688,0.16759,0.1999]},{"body_a":"world","body_b":"grasp_target","contact_count":1016.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50642,0.0361,0.09385]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4960.0,"contact_point_centroid":[0.49987,0.05695,0.03247],"force_p95":0.07654,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08517,"mean_force":0.04533,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.49913,0.0378,0.03064]}],"total_contact_groups":16},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62231,0.17242,0.01602],"final_tcp_position":[0.62234,0.17043,0.22606],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":298.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1188.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50759,0.03394,0.14805],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":254.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_to_grasp","tcp_end":[0.50749,0.03846,0.03986],"tcp_start":[0.50759,0.03394,0.14805],"tcp_to_object_dist_end":0.01478,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.03794,0.02543],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21371,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.16167,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10533.0,"raw_peak_contact_force":0.25086,"tcp_end":[0.49909,0.03779,0.03059],"tcp_start":[0.50749,0.03846,0.03986],"tcp_to_object_dist_end":0.01431,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.52537,0.03793,0.1397],"object_pos_start":[0.51243,0.03794,0.02543],"object_to_goal_dist_end":0.16908,"object_to_goal_dist_start":0.21371,"object_z_max":0.13953,"peak_contact_force":167951.73011,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17451.0,"raw_peak_contact_force":0.63185,"subtask_id":"lift_object","tcp_end":[0.50781,0.03763,0.15469],"tcp_start":[0.49909,0.03779,0.03059],"tcp_to_object_dist_end":0.02309,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":460.0,"n_steps_budget":1000.0,"object_pos_end":[0.62065,0.16158,0.15692],"object_pos_start":[0.52537,0.03793,0.1397],"object_to_goal_dist_end":0.01758,"object_to_goal_dist_start":0.16908,"object_z_max":0.15689,"peak_contact_force":0.09865,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10553.0,"raw_peak_contact_force":0.21324,"subtask_id":"approach_goal","tcp_end":[0.61532,0.16144,0.18377],"tcp_start":[0.50781,0.03763,0.15469],"tcp_to_object_dist_end":0.02737,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":72.0,"n_steps_budget":1000.0,"object_pos_end":[0.62624,0.16724,0.12811],"object_pos_start":[0.62065,0.16158,0.15692],"object_to_goal_dist_end":0.01777,"object_to_goal_dist_start":0.01758,"object_z_max":0.15692,"peak_contact_force":0.14529,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1299.0,"raw_peak_contact_force":0.29732,"subtask_id":"place_object","tcp_end":[0.61937,0.16689,0.15588],"tcp_start":[0.61532,0.16144,0.18377],"tcp_to_object_dist_end":0.02862,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62221,0.17123,0.01477],"object_pos_start":[0.62624,0.16724,0.12811],"object_to_goal_dist_end":0.13037,"object_to_goal_dist_start":0.01777,"object_z_max":0.12811,"peak_contact_force":0.10551,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1428.0,"raw_peak_contact_force":1.4746,"tcp_end":[0.6129,0.16503,0.1748],"tcp_start":[0.61937,0.16689,0.15588],"tcp_to_object_dist_end":0.16042,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":227.0,"n_steps_budget":600.0,"object_pos_end":[0.62231,0.17242,0.01602],"object_pos_start":[0.62221,0.17123,0.01477],"object_to_goal_dist_end":0.12911,"object_to_goal_dist_start":0.13037,"object_z_max":0.01646,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":908.0,"raw_peak_contact_force":0.12746,"tcp_end":[0.62234,0.17043,0.22606],"tcp_start":[0.6129,0.16503,0.1748],"tcp_to_object_dist_end":0.21005,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```