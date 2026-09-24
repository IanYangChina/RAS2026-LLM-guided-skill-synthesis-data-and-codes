## Search State

- **Seed**: 5
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
  guards:
  - id: retain_object
    when: during_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
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
    - 0.02
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.02
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
  - guards:
    - id=retain_object, when=during_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=1, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.02], tolerance=0.015
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
| descend_to_grasp | 1.00 | 1.00 | 0.1086 |
| grasp_action | 1.00 | 1.00 | 0.0126 |
| lift_object | 1.00 | 1.00 | 0.1092 |
| approach_goal | 0.67 | 0.33 | 0.1064 |
| descend_to_place | 1.00 | 1.00 | 0.0112 |
| release_object | 1.00 | 1.00 | 0.0209 |
| retract_after_place | 1.00 | 1.00 | 0.0358 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.148) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 16.808 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, 0.016, 0.148)→(0.510, 0.018, 0.040) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_action | grasp | 1.00 / step_budget | (0.510, 0.018, 0.040)→(0.502, 0.017, 0.030) | (0.516, 0.018, 0.026)→(0.516, 0.017, 0.026) | 0.236→0.237 | 1.00 / 41.000 | 0.151 | 0.224 |
| lift_object | lift | 1.00 / step_budget | (0.502, 0.017, 0.030)→(0.510, 0.017, 0.139) | (0.516, 0.017, 0.026)→(0.529, 0.017, 0.128) | 0.237→0.194 | 1.00 / 22.333 | 0.110 | 0.608 |
| approach_goal | approach | 0.67 / step_budget | (0.536, 0.078, 0.189)→(0.594, 0.164, 0.202) | (0.529, 0.017, 0.128)→(0.604, 0.171, 0.098) | 0.194→0.083 | 0.33 / 6.667 | 0.042 | 0.239 |
| descend_to_place | descend | 1.00 / step_budget | (0.594, 0.164, 0.202)→(0.597, 0.170, 0.194) | (0.604, 0.171, 0.097)→(0.606, 0.178, 0.047) | 0.084→0.122 | 1.00 / 6.000 | 3253.946 | 1.279 |
| release_object | release | 1.00 / step_budget | (0.597, 0.170, 0.194)→(0.591, 0.169, 0.214) | (0.606, 0.178, 0.047)→(0.607, 0.179, 0.016) | 0.122→0.151 | 1.00 / 4.000 | 0.123 | 1.055 |
| retract_after_place | retract | 1.00 / step_budget | (0.591, 0.169, 0.214)→(0.600, 0.176, 0.248) | (0.607, 0.179, 0.016)→(0.607, 0.179, 0.016) | 0.151→0.151 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.541
- phase_score: 0.682
- phase_breakdown.approach_object_score: 0.671
- phase_breakdown.place_object_score: 0.683
- phase_breakdown.lift_object_score: 0.498
- phase_breakdown.approach_goal_score: 0.672
- phase_breakdown.descend_to_grasp_score: 0.796
- grasp_place_fitness: 0.747

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.747
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.541
- **Median Q (composite search score)**: 0.109
- **K-run variance**: 0.0045
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.285


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37297,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.05271,"approach_object.approach_speed":0.13232,"descend_to_place.place_speed":0.07279,"descend_to_place.place_z_offset":0.01613,"grasp_action.grasp_duration":0.91906,"lift_object.lift_height":0.13919,"lift_object.lift_speed":0.10912,"release_object.release_duration":0.85167},"optimized_scores":{"best_composite_score":0.16697,"best_fitness_score":0.74697,"best_task_score":0.54115},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":584.0,"contact_point_centroid":[0.60359,0.17984,-0.00329],"force_p95":0.67626,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.48885,"mean_force":0.19123,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58729,0.16852,0.13547]},{"body_a":"world","body_b":"grasp_target","contact_count":83.0,"contact_point_centroid":[0.52849,0.02865,-0.00145],"force_p95":0.51713,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58856,"mean_force":0.118,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51519,0.02912,0.03143]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":51.0,"contact_point_centroid":[0.59894,0.18692,0.12559],"force_p95":0.26681,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40742,"mean_force":0.04503,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59258,0.17024,0.13213]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":352.0,"contact_point_centroid":[0.59611,0.18472,0.13827],"force_p95":0.20936,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32794,"mean_force":0.12428,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59173,0.16673,0.14346]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5697.0,"contact_point_centroid":[0.52147,0.0478,0.08154],"force_p95":0.10941,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30794,"mean_force":0.07241,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51818,0.02899,0.07961]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":290.0,"contact_point_centroid":[0.59629,0.14882,0.13866],"force_p95":0.20373,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30169,"mean_force":0.13278,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59171,0.16666,0.14362]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5425.0,"contact_point_centroid":[0.52176,0.01015,0.08415],"force_p95":0.11097,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30078,"mean_force":0.07473,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51839,0.02898,0.08193]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03049,-0.00214],"force_p95":0.16478,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24354,"mean_force":0.13376,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.51744,0.02929,0.03134]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3.0,"contact_point_centroid":[0.6009,0.15384,0.12633],"force_p95":0.23207,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23565,"mean_force":0.19441,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59343,0.1702,0.13358]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4951.0,"contact_point_centroid":[0.56049,0.07547,0.14406],"force_p95":0.14023,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20658,"mean_force":0.09182,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55532,0.09382,0.14508]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4873.0,"contact_point_centroid":[0.56169,0.11536,0.14396],"force_p95":0.13339,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18883,"mean_force":0.09298,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55691,0.09701,0.14522]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4058.0,"contact_point_centroid":[0.5172,0.01001,0.03273],"force_p95":0.08137,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15003,"mean_force":0.05193,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.51623,0.02921,0.02999]},{"body_a":"world","body_b":"grasp_target","contact_count":1176.0,"contact_point_centroid":[0.5305,0.03079,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51053,0.01271,0.22486]},{"body_a":"world","body_b":"grasp_target","contact_count":668.0,"contact_point_centroid":[0.60392,0.17974,-0.00199],"force_p95":0.12289,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12321,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.5903,0.17179,0.17102]},{"body_a":"world","body_b":"grasp_target","contact_count":1004.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52278,0.02795,0.09377]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5016.0,"contact_point_centroid":[0.51712,0.04839,0.03178],"force_p95":0.07406,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08634,"mean_force":0.04467,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.51624,0.02921,0.03]}],"total_contact_groups":16},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60392,0.17974,0.01602],"final_tcp_position":[0.59522,0.17547,0.1895],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":9760.30694,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":295.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1176.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52296,0.02628,0.14787],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12217,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":251.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1004.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_to_grasp","tcp_end":[0.52485,0.02977,0.03986],"tcp_start":[0.52296,0.02628,0.14787],"tcp_to_object_dist_end":0.01498,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53041,0.02929,0.02552],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18483,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15607,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10874.0,"raw_peak_contact_force":0.24354,"tcp_end":[0.5162,0.02921,0.02996],"tcp_start":[0.52485,0.02977,0.03986],"tcp_to_object_dist_end":0.01488,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":389.0,"n_steps_budget":780.0,"object_pos_end":[0.54415,0.0292,0.13427],"object_pos_start":[0.53041,0.02929,0.02552],"object_to_goal_dist_end":0.16215,"object_to_goal_dist_start":0.18483,"object_z_max":0.13403,"peak_contact_force":0.11249,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11205.0,"raw_peak_contact_force":0.58856,"subtask_id":"lift_object","tcp_end":[0.52515,0.02902,0.14557],"tcp_start":[0.5162,0.02921,0.02996],"tcp_to_object_dist_end":0.02211,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":477.0,"n_steps_budget":1000.0,"object_pos_end":[0.59844,0.16437,0.12622],"object_pos_start":[0.54415,0.0292,0.13427],"object_to_goal_dist_end":0.02324,"object_to_goal_dist_start":0.16215,"object_z_max":0.13447,"peak_contact_force":0.12643,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9824.0,"raw_peak_contact_force":0.20658,"subtask_id":"approach_goal","tcp_end":[0.59102,0.16436,0.14907],"tcp_start":[0.52515,0.02902,0.14557],"tcp_to_object_dist_end":0.02403,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":48.0,"n_steps_budget":1000.0,"object_pos_end":[0.60193,0.17124,0.10769],"object_pos_start":[0.59844,0.16437,0.12622],"object_to_goal_dist_end":0.00736,"object_to_goal_dist_start":0.02324,"object_z_max":0.12622,"peak_contact_force":9760.30694,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":642.0,"raw_peak_contact_force":0.32794,"subtask_id":"place_object","tcp_end":[0.59343,0.1702,0.13358],"tcp_start":[0.59102,0.16436,0.14907],"tcp_to_object_dist_end":0.02727,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60392,0.17973,0.016],"object_pos_start":[0.60193,0.17124,0.10769],"object_to_goal_dist_end":0.09212,"object_to_goal_dist_start":0.00736,"object_z_max":0.10769,"peak_contact_force":0.12323,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":638.0,"raw_peak_contact_force":1.48885,"tcp_end":[0.58658,0.16828,0.15371],"tcp_start":[0.59343,0.1702,0.13358],"tcp_to_object_dist_end":0.13926,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":167.0,"n_steps_budget":600.0,"object_pos_end":[0.60392,0.17974,0.01602],"object_pos_start":[0.60392,0.17973,0.016],"object_to_goal_dist_end":0.09211,"object_to_goal_dist_start":0.09212,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":668.0,"raw_peak_contact_force":0.12321,"tcp_end":[0.59522,0.17547,0.1895],"tcp_start":[0.58658,0.16828,0.15371],"tcp_to_object_dist_end":0.17375,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.66667,"average_solve_count":183.0,"average_success_count":183.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.07858,"approach_object.approach_speed":0.13895,"descend_to_place.place_speed":0.05629,"descend_to_place.place_z_offset":0.03049,"grasp_action.grasp_duration":1.38675,"lift_object.lift_height":0.11769,"lift_object.lift_speed":0.14557,"release_object.release_duration":0.95353},"optimized_scores":{"best_composite_score":0.00421,"best_fitness_score":0.58421,"best_task_score":0.21281},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":171.0,"contact_point_centroid":[0.58678,0.18612,-0.00934],"force_p95":1.33745,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.04439,"mean_force":0.47329,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57778,0.17262,0.27115]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.50146,-0.01497,-0.00132],"force_p95":0.54765,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59119,"mean_force":0.12506,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48977,-0.01515,0.03232]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4634.0,"contact_point_centroid":[0.49454,0.00394,0.07503],"force_p95":0.10711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32455,"mean_force":0.06791,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49245,-0.01508,0.07253]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5098.0,"contact_point_centroid":[0.49453,-0.03396,0.07324],"force_p95":0.10295,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29253,"mean_force":0.06304,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49235,-0.01508,0.07153]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8557.0,"contact_point_centroid":[0.53461,0.04526,0.18691],"force_p95":0.1302,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25244,"mean_force":0.08333,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.52981,0.06378,0.18654]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8588.0,"contact_point_centroid":[0.53547,0.0841,0.1882],"force_p95":0.13012,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22135,"mean_force":0.08291,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5306,0.06559,0.18805]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01551,-0.00205],"force_p95":0.13719,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17738,"mean_force":0.12664,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.4919,-0.01518,0.03216]},{"body_a":"world","body_b":"grasp_target","contact_count":1112.0,"contact_point_centroid":[0.50382,-0.01567,-0.00188],"force_p95":0.13647,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49947,-0.00642,0.22591]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58624,0.18559,-0.00206],"force_p95":0.12647,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12765,"mean_force":0.11416,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57691,0.17631,0.27175]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4101.0,"contact_point_centroid":[0.49125,0.00404,0.03371],"force_p95":0.07716,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12291,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.49074,-0.01517,0.03094]},{"body_a":"world","body_b":"grasp_target","contact_count":644.0,"contact_point_centroid":[0.58625,0.18558,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.57912,0.18012,0.30946]},{"body_a":"world","body_b":"grasp_target","contact_count":1028.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49843,-0.01427,0.09434]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4904.0,"contact_point_centroid":[0.4913,-0.03425,0.03279],"force_p95":0.06923,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09205,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.49074,-0.01517,0.03095]},{"body_a":"left_finger","body_b":"right_finger","contact_count":13.0,"contact_point_centroid":[0.58063,0.17665,0.2733],"force_p95":0.01564,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01564,"mean_force":0.01496,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57959,0.17664,0.27067]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.57943,0.17712,0.27011],"force_p95":0.01391,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01489,"mean_force":0.01078,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57866,0.1771,0.26776]}],"total_contact_groups":15},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58625,0.18558,0.01602],"final_tcp_position":[0.58295,0.18439,0.32877],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":2.04439,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":279.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1112.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50004,-0.01334,0.14914],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1232,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":257.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_to_grasp","tcp_end":[0.49902,-0.01526,0.03984],"tcp_start":[0.50004,-0.01334,0.14914],"tcp_to_object_dist_end":0.01464,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5037,-0.01507,0.02583],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31201,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13405,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10805.0,"raw_peak_contact_force":0.17738,"tcp_end":[0.49071,-0.01517,0.03091],"tcp_start":[0.49902,-0.01526,0.03984],"tcp_to_object_dist_end":0.01395,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":300.0,"n_steps_budget":600.0,"object_pos_end":[0.51627,-0.01497,0.11503],"object_pos_start":[0.5037,-0.01507,0.02583],"object_to_goal_dist_end":0.25234,"object_to_goal_dist_start":0.31201,"object_z_max":0.11478,"peak_contact_force":0.10797,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9809.0,"raw_peak_contact_force":0.59119,"subtask_id":"lift_object","tcp_end":[0.49828,-0.01502,0.12449],"tcp_start":[0.49071,-0.01517,0.03091],"tcp_to_object_dist_end":0.02032,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":824.0,"n_steps_budget":1000.0,"object_pos_end":[0.58811,0.17757,0.07841],"object_pos_start":[0.51627,-0.01497,0.11503],"object_to_goal_dist_end":0.17,"object_to_goal_dist_start":0.25234,"object_z_max":0.23291,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17145.0,"raw_peak_contact_force":0.25244,"subtask_id":"approach_goal","tcp_end":[0.57539,0.1666,0.27312],"tcp_start":[0.57536,0.16644,0.27308],"tcp_to_object_dist_end":0.19544,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":58.0,"n_steps_budget":1000.0,"object_pos_end":[0.5869,0.18386,0.00956],"object_pos_start":[0.58823,0.17789,0.07492],"object_to_goal_dist_end":0.23858,"object_to_goal_dist_start":0.17347,"object_z_max":0.07492,"peak_contact_force":0.06849,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":184.0,"raw_peak_contact_force":2.04439,"subtask_id":"place_object","tcp_end":[0.57977,0.17704,0.27065],"tcp_start":[0.57539,0.1666,0.27312],"tcp_to_object_dist_end":0.26127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58625,0.18558,0.01602],"object_pos_start":[0.5869,0.18386,0.00956],"object_to_goal_dist_end":0.23211,"object_to_goal_dist_start":0.23858,"object_z_max":0.0168,"peak_contact_force":0.12264,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12765,"tcp_end":[0.57597,0.17589,0.29155],"tcp_start":[0.57977,0.17704,0.27065],"tcp_to_object_dist_end":0.27589,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":161.0,"n_steps_budget":600.0,"object_pos_end":[0.58625,0.18558,0.01602],"object_pos_start":[0.58625,0.18558,0.01602],"object_to_goal_dist_end":0.23211,"object_to_goal_dist_start":0.23211,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":644.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.58295,0.18439,0.32877],"tcp_start":[0.57597,0.17589,0.29155],"tcp_to_object_dist_end":0.31277,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74074,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.07395,"approach_object.approach_speed":0.15633,"descend_to_place.place_speed":0.03419,"descend_to_place.place_z_offset":0.02712,"grasp_action.grasp_duration":1.03795,"lift_object.lift_height":0.14182,"lift_object.lift_speed":0.15565,"release_object.release_duration":0.79659},"optimized_scores":{"best_composite_score":0.10873,"best_fitness_score":0.68873,"best_task_score":0.42301},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":785.0,"contact_point_centroid":[0.63092,0.17144,-0.00316],"force_p95":0.56641,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.54948,"mean_force":0.17748,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61268,0.16289,0.1783]},{"body_a":"world","body_b":"grasp_target","contact_count":2.0,"contact_point_centroid":[0.6299,0.18147,-0.00037],"force_p95":1.45401,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.4638,"mean_force":1.36589,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61704,0.16391,0.17885]},{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.51039,0.03734,-0.00149],"force_p95":0.52261,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64359,"mean_force":0.12494,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49804,0.03768,0.03205]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5134.0,"contact_point_centroid":[0.50412,0.01865,0.08554],"force_p95":0.11147,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3423,"mean_force":0.07334,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5011,0.03754,0.08319]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5567.0,"contact_point_centroid":[0.5037,0.0564,0.08237],"force_p95":0.10888,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33489,"mean_force":0.0694,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50086,0.03754,0.08046]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4996.0,"contact_point_centroid":[0.55531,0.06939,0.15859],"force_p95":0.14653,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2579,"mean_force":0.09461,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.5496,0.08774,0.15985]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51258,0.03936,-0.00217],"force_p95":0.1737,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25105,"mean_force":0.13594,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50028,0.03788,0.03191]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4725.0,"contact_point_centroid":[0.55859,0.11015,0.15951],"force_p95":0.13523,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20207,"mean_force":0.09856,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55315,0.09177,0.16108]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3766.0,"contact_point_centroid":[0.50032,0.0186,0.03366],"force_p95":0.08635,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15562,"mean_force":0.05555,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.4991,0.03779,0.03065]},{"body_a":"world","body_b":"grasp_target","contact_count":1124.0,"contact_point_centroid":[0.51251,0.03972,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50308,0.01634,0.22525]},{"body_a":"world","body_b":"grasp_target","contact_count":592.0,"contact_point_centroid":[0.63095,0.17153,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.61584,0.16588,0.21146]},{"body_a":"world","body_b":"grasp_target","contact_count":1016.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50638,0.03608,0.09391]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4958.0,"contact_point_centroid":[0.49986,0.05694,0.0325],"force_p95":0.07658,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08537,"mean_force":0.04535,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.49911,0.03779,0.03066]}],"total_contact_groups":13},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.63095,0.17153,0.01602],"final_tcp_position":[0.62121,0.16943,0.22645],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":50.17974,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":282.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":50.17974,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1124.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50752,0.0339,0.14812],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":254.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_to_grasp","tcp_end":[0.50748,0.03845,0.03989],"tcp_start":[0.50752,0.0339,0.14812],"tcp_to_object_dist_end":0.01481,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.03793,0.02543],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21371,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.16172,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10524.0,"raw_peak_contact_force":0.25105,"tcp_end":[0.49908,0.03778,0.03062],"tcp_start":[0.50748,0.03845,0.03989],"tcp_to_object_dist_end":0.01433,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":361.0,"n_steps_budget":600.0,"object_pos_end":[0.52647,0.03787,0.13565],"object_pos_start":[0.51243,0.03793,0.02543],"object_to_goal_dist_end":0.16864,"object_to_goal_dist_start":0.21371,"object_z_max":0.13541,"peak_contact_force":0.11043,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10780.0,"raw_peak_contact_force":0.64359,"subtask_id":"lift_object","tcp_end":[0.50749,0.03761,0.14795],"tcp_start":[0.49908,0.03778,0.03062],"tcp_to_object_dist_end":0.02262,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":550.0,"n_steps_budget":1000.0,"object_pos_end":[0.6244,0.17009,0.08899],"object_pos_start":[0.52647,0.03787,0.13565],"object_to_goal_dist_end":0.05618,"object_to_goal_dist_start":0.16864,"object_z_max":0.15447,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9721.0,"raw_peak_contact_force":0.2579,"subtask_id":"approach_goal","tcp_end":[0.61556,0.16184,0.1832],"tcp_start":[0.50749,0.03761,0.14795],"tcp_to_object_dist_end":0.09499,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":24.0,"n_steps_budget":1000.0,"object_pos_end":[0.62999,0.17812,0.02436],"object_pos_start":[0.6244,0.17009,0.08899],"object_to_goal_dist_end":0.12082,"object_to_goal_dist_start":0.05618,"object_z_max":0.08899,"peak_contact_force":1.4638,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":1.4638,"subtask_id":"place_object","tcp_end":[0.61717,0.16404,0.17856],"tcp_start":[0.61556,0.16184,0.1832],"tcp_to_object_dist_end":0.15537,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63095,0.17153,0.01602],"object_pos_start":[0.62999,0.17812,0.02436],"object_to_goal_dist_end":0.12905,"object_to_goal_dist_start":0.12082,"object_z_max":0.02436,"peak_contact_force":0.12264,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":785.0,"raw_peak_contact_force":1.54948,"tcp_end":[0.61123,0.1624,0.1978],"tcp_start":[0.61717,0.16404,0.17856],"tcp_to_object_dist_end":0.18307,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":148.0,"n_steps_budget":600.0,"object_pos_end":[0.63095,0.17153,0.01602],"object_pos_start":[0.63095,0.17153,0.01602],"object_to_goal_dist_end":0.12905,"object_to_goal_dist_start":0.12905,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":592.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.62121,0.16943,0.22645],"tcp_start":[0.61123,0.1624,0.1978],"tcp_to_object_dist_end":0.21066,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```