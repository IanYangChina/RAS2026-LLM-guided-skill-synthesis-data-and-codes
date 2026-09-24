## Search State

- **Seed**: 5
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
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1552 |
| descend_to_grasp | 1.00 | 1.00 | 0.1087 |
| grasp_action | 1.00 | 1.00 | 0.0126 |
| lift_object | 1.00 | 1.00 | 0.1188 |
| approach_goal | 1.00 | 0.67 | 0.1870 |
| descend_to_place | 1.00 | 0.67 | 0.0213 |
| release_object | 1.00 | 1.00 | 0.0210 |
| retract_after_place | 1.00 | 1.00 | 0.0441 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.148) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, 0.016, 0.148)→(0.510, 0.018, 0.040) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_action | grasp | 1.00 / step_budget | (0.510, 0.018, 0.040)→(0.502, 0.017, 0.030) | (0.516, 0.018, 0.026)→(0.516, 0.017, 0.026) | 0.236→0.237 | 1.00 / 41.000 | 0.151 | 0.224 |
| lift_object | lift | 1.00 / step_budget | (0.502, 0.017, 0.030)→(0.510, 0.017, 0.149) | (0.516, 0.017, 0.026)→(0.527, 0.017, 0.138) | 0.237→0.189 | 1.00 / 27.667 | 0.100 | 0.619 |
| approach_goal | approach | 1.00 / step_budget | (0.510, 0.017, 0.149)→(0.596, 0.168, 0.205) | (0.527, 0.017, 0.138)→(0.603, 0.171, 0.160) | 0.189→0.034 | 0.67 / 17.667 | 0.070 | 0.184 |
| descend_to_place | descend | 1.00 / step_budget | (0.596, 0.168, 0.205)→(0.598, 0.174, 0.185) | (0.603, 0.171, 0.160)→(0.607, 0.177, 0.099) | 0.034→0.069 | 0.67 / 11.333 | 0.064 | 0.771 |
| release_object | release | 1.00 / step_budget | (0.598, 0.174, 0.185)→(0.593, 0.172, 0.205) | (0.607, 0.177, 0.099)→(0.606, 0.178, 0.011) | 0.069→0.156 | 1.00 / 4.000 | 0.171 | 1.164 |
| retract_after_place | retract | 1.00 / step_budget | (0.593, 0.172, 0.205)→(0.600, 0.177, 0.248) | (0.606, 0.178, 0.011)→(0.607, 0.179, 0.016) | 0.156→0.151 | 1.00 / 4.000 | 0.123 | 0.164 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.541
- phase_score: 0.541
- phase_breakdown.approach_object_score: 0.671
- phase_breakdown.place_object_score: 0.000
- phase_breakdown.lift_object_score: 0.451
- phase_breakdown.approach_goal_score: 0.673
- phase_breakdown.descend_to_grasp_score: 0.799
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
- **Final σ (mean)**: 0.312


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.59302,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.06875,"approach_object.approach_speed":0.11015,"descend_to_place.place_speed":0.0542,"descend_to_place.place_z_offset":0.0132,"grasp_action.grasp_duration":0.98383,"lift_object.lift_height":0.13432,"lift_object.lift_speed":0.13122,"release_object.release_duration":0.23045},"optimized_scores":{"best_composite_score":0.16711,"best_fitness_score":0.74711,"best_task_score":0.54128},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":764.0,"contact_point_centroid":[0.60106,0.1779,-0.0031],"force_p95":0.57107,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.18822,"mean_force":0.16798,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58906,0.17117,0.12491]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.52776,0.02855,-0.00145],"force_p95":0.57967,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65261,"mean_force":0.13016,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51516,0.02913,0.0312]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4978.0,"contact_point_centroid":[0.52188,0.01015,0.08199],"force_p95":0.1115,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33777,"mean_force":0.07575,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51846,0.02899,0.07975]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5258.0,"contact_point_centroid":[0.52152,0.04781,0.0792],"force_p95":0.11045,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33512,"mean_force":0.0731,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51822,0.02899,0.07729]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":368.0,"contact_point_centroid":[0.59592,0.18458,0.13704],"force_p95":0.20076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32649,"mean_force":0.11973,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59136,0.16667,0.14249]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":319.0,"contact_point_centroid":[0.5963,0.14895,0.13784],"force_p95":0.21241,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29619,"mean_force":0.12355,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59133,0.1666,0.14275]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03049,-0.00214],"force_p95":0.16471,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24374,"mean_force":0.13374,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.51743,0.0293,0.03112]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4470.0,"contact_point_centroid":[0.55955,0.07278,0.14165],"force_p95":0.15503,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21215,"mean_force":0.09843,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55397,0.09112,0.14207]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4697.0,"contact_point_centroid":[0.5616,0.11463,0.14153],"force_p95":0.14198,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19705,"mean_force":0.09482,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55653,0.09632,0.14245]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4058.0,"contact_point_centroid":[0.51719,0.01001,0.03252],"force_p95":0.08135,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14988,"mean_force":0.05193,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.51622,0.02922,0.02977]},{"body_a":"world","body_b":"grasp_target","contact_count":1196.0,"contact_point_centroid":[0.5305,0.03079,-0.00189],"force_p95":0.13615,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51052,0.01267,0.22511]},{"body_a":"world","body_b":"grasp_target","contact_count":1008.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52282,0.02795,0.09368]},{"body_a":"world","body_b":"grasp_target","contact_count":784.0,"contact_point_centroid":[0.60109,0.17797,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.59081,0.17322,0.16646]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5016.0,"contact_point_centroid":[0.51711,0.04839,0.03157],"force_p95":0.07403,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08641,"mean_force":0.04467,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.51623,0.02922,0.02978]}],"total_contact_groups":14},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60109,0.17797,0.01602],"final_tcp_position":[0.59564,0.17608,0.18918],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.18822,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":300.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1196.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52302,0.02627,0.14797],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1008.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_to_grasp","tcp_end":[0.52483,0.02977,0.03963],"tcp_start":[0.52302,0.02627,0.14797],"tcp_to_object_dist_end":0.01478,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53041,0.02929,0.02552],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18483,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15599,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10874.0,"raw_peak_contact_force":0.24374,"tcp_end":[0.51619,0.02921,0.02974],"tcp_start":[0.52483,0.02977,0.03963],"tcp_to_object_dist_end":0.01483,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":361.0,"n_steps_budget":630.0,"object_pos_end":[0.5442,0.02924,0.12905],"object_pos_start":[0.53041,0.02929,0.02552],"object_to_goal_dist_end":0.16133,"object_to_goal_dist_start":0.18483,"object_z_max":0.12881,"peak_contact_force":0.1119,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10313.0,"raw_peak_contact_force":0.65261,"subtask_id":"lift_object","tcp_end":[0.52512,0.02902,0.14058],"tcp_start":[0.51619,0.02921,0.02974],"tcp_to_object_dist_end":0.02229,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":469.0,"n_steps_budget":1000.0,"object_pos_end":[0.59838,0.16479,0.12562],"object_pos_start":[0.5442,0.02924,0.12905],"object_to_goal_dist_end":0.02252,"object_to_goal_dist_start":0.16133,"object_z_max":0.12925,"peak_contact_force":0.13009,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9167.0,"raw_peak_contact_force":0.21215,"subtask_id":"approach_goal","tcp_end":[0.59113,0.16457,0.14865],"tcp_start":[0.52512,0.02902,0.14058],"tcp_to_object_dist_end":0.02415,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":94.0,"n_steps_budget":1000.0,"object_pos_end":[0.60105,0.17416,0.04178],"object_pos_start":[0.59838,0.16479,0.12562],"object_to_goal_dist_end":0.06646,"object_to_goal_dist_start":0.02252,"object_z_max":0.12562,"peak_contact_force":0.0,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":687.0,"raw_peak_contact_force":0.32649,"subtask_id":"place_object","tcp_end":[0.5942,0.17262,0.12412],"tcp_start":[0.59113,0.16457,0.14865],"tcp_to_object_dist_end":0.08264,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60109,0.17797,0.01602],"object_pos_start":[0.60105,0.17416,0.04178],"object_to_goal_dist_end":0.09207,"object_to_goal_dist_start":0.06646,"object_z_max":0.04178,"peak_contact_force":0.1226,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":764.0,"raw_peak_contact_force":1.18822,"tcp_end":[0.58744,0.17063,0.14461],"tcp_start":[0.5942,0.17262,0.12412],"tcp_to_object_dist_end":0.12952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":196.0,"n_steps_budget":600.0,"object_pos_end":[0.60109,0.17797,0.01602],"object_pos_start":[0.60109,0.17797,0.01602],"object_to_goal_dist_end":0.09207,"object_to_goal_dist_start":0.09207,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":784.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59564,0.17608,0.18918],"tcp_start":[0.58744,0.17063,0.14461],"tcp_to_object_dist_end":0.17326,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21176,"average_solve_count":255.0,"average_success_count":255.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.05292,"approach_object.approach_speed":0.11811,"descend_to_place.place_speed":0.07965,"descend_to_place.place_z_offset":0.00864,"grasp_action.grasp_duration":1.90607,"lift_object.lift_height":0.15538,"lift_object.lift_speed":0.05366,"release_object.release_duration":0.28752},"optimized_scores":{"best_composite_score":0.0042,"best_fitness_score":0.5842,"best_task_score":0.21276},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":117.0,"contact_point_centroid":[0.58773,0.18668,-0.01066],"force_p95":1.79504,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.1763,"mean_force":0.72027,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57787,0.18034,0.27858]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.50131,-0.01476,-0.00139],"force_p95":0.47753,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56404,"mean_force":0.14794,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48975,-0.01515,0.03211]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8537.0,"contact_point_centroid":[0.4936,0.00405,0.09808],"force_p95":0.08023,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30198,"mean_force":0.05643,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49305,-0.01507,0.0956]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8974.0,"contact_point_centroid":[0.4934,-0.03413,0.09566],"force_p95":0.07813,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28437,"mean_force":0.0543,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49287,-0.01507,0.09349]},{"body_a":"world","body_b":"grasp_target","contact_count":748.0,"contact_point_centroid":[0.59094,0.18546,-0.00237],"force_p95":0.12928,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24781,"mean_force":0.11381,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.58023,0.18281,0.30549]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":964.0,"contact_point_centroid":[0.58259,0.16244,0.26072],"force_p95":0.08987,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21494,"mean_force":0.05348,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58044,0.18145,0.25905]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1078.0,"contact_point_centroid":[0.5825,0.2004,0.25931],"force_p95":0.08454,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20345,"mean_force":0.05196,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58042,0.18144,0.259]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01551,-0.00205],"force_p95":0.13719,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17737,"mean_force":0.12664,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.49191,-0.01518,0.03216]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1052.0,"contact_point_centroid":[0.58273,0.15978,0.27581],"force_p95":0.08809,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15304,"mean_force":0.06354,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58069,0.17875,0.27434]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1187.0,"contact_point_centroid":[0.58268,0.19778,0.2745],"force_p95":0.08162,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14777,"mean_force":0.0588,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5807,0.17879,0.27418]},{"body_a":"world","body_b":"grasp_target","contact_count":1132.0,"contact_point_centroid":[0.50382,-0.01567,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49948,-0.00641,0.22605]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4101.0,"contact_point_centroid":[0.49125,0.00404,0.03371],"force_p95":0.07715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12291,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.49075,-0.01517,0.03095]},{"body_a":"world","body_b":"grasp_target","contact_count":1028.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49846,-0.01427,0.09435]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16459.0,"contact_point_centroid":[0.53989,0.06452,0.22384],"force_p95":0.07381,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09909,"mean_force":0.05018,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53917,0.08358,0.2224]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4904.0,"contact_point_centroid":[0.49131,-0.03425,0.0328],"force_p95":0.06923,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09205,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.49075,-0.01517,0.03095]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15376.0,"contact_point_centroid":[0.54141,0.10607,0.22631],"force_p95":0.07808,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08853,"mean_force":0.05292,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54063,0.08693,0.22459]}],"total_contact_groups":16},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.5909,0.18539,0.01602],"final_tcp_position":[0.5835,0.18544,0.32872],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":2.1763,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":284.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1132.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.5001,-0.01334,0.14916],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12322,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":257.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_to_grasp","tcp_end":[0.49903,-0.01526,0.03984],"tcp_start":[0.5001,-0.01334,0.14916],"tcp_to_object_dist_end":0.01464,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5037,-0.01507,0.02583],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31201,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13405,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10805.0,"raw_peak_contact_force":0.17737,"tcp_end":[0.49072,-0.01517,0.03092],"tcp_start":[0.49903,-0.01526,0.03984],"tcp_to_object_dist_end":0.01394,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":463.0,"n_steps_budget":1000.0,"object_pos_end":[0.51049,-0.01506,0.15251],"object_pos_start":[0.5037,-0.01507,0.02583],"object_to_goal_dist_end":0.23662,"object_to_goal_dist_start":0.31201,"object_z_max":0.15225,"peak_contact_force":0.08108,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17597.0,"raw_peak_contact_force":0.56404,"subtask_id":"lift_object","tcp_end":[0.49891,-0.01502,0.16205],"tcp_start":[0.49072,-0.01517,0.03092],"tcp_to_object_dist_end":0.015,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":830.0,"n_steps_budget":1000.0,"object_pos_end":[0.58768,0.17621,0.26724],"object_pos_start":[0.51049,-0.01506,0.15251],"object_to_goal_dist_end":0.0222,"object_to_goal_dist_start":0.23662,"object_z_max":0.26712,"peak_contact_force":0.08101,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31835.0,"raw_peak_contact_force":0.09909,"subtask_id":"approach_goal","tcp_end":[0.58011,0.17626,0.28325],"tcp_start":[0.49891,-0.01502,0.16205],"tcp_to_object_dist_end":0.01771,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":70.0,"n_steps_budget":1000.0,"object_pos_end":[0.59027,0.18158,0.2465],"object_pos_start":[0.58768,0.17621,0.26724],"object_to_goal_dist_end":0.00696,"object_to_goal_dist_start":0.0222,"object_z_max":0.26726,"peak_contact_force":0.08739,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2239.0,"raw_peak_contact_force":0.15304,"subtask_id":"place_object","tcp_end":[0.58189,0.18176,0.26304],"tcp_start":[0.58011,0.17626,0.28325],"tcp_to_object_dist_end":0.01854,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58889,0.18194,0.00203],"object_pos_start":[0.59027,0.18158,0.2465],"object_to_goal_dist_end":0.24615,"object_to_goal_dist_start":0.00696,"object_z_max":0.2465,"peak_contact_force":0.26776,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2159.0,"raw_peak_contact_force":2.1763,"tcp_end":[0.57785,0.18034,0.28342],"tcp_start":[0.58189,0.18176,0.26304],"tcp_to_object_dist_end":0.2816,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":187.0,"n_steps_budget":600.0,"object_pos_end":[0.5909,0.18539,0.01602],"object_pos_start":[0.58889,0.18194,0.00203],"object_to_goal_dist_end":0.23214,"object_to_goal_dist_start":0.24615,"object_z_max":0.01685,"peak_contact_force":0.12264,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":748.0,"raw_peak_contact_force":0.24781,"tcp_end":[0.5835,0.18544,0.32872],"tcp_start":[0.57785,0.18034,0.28342],"tcp_to_object_dist_end":0.31279,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50279,"average_solve_count":179.0,"average_success_count":179.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.06166,"approach_object.approach_speed":0.12125,"descend_to_place.place_speed":0.05462,"descend_to_place.place_z_offset":0.02042,"grasp_action.grasp_duration":1.22442,"lift_object.lift_height":0.13787,"lift_object.lift_speed":0.14904,"release_object.release_duration":0.35996},"optimized_scores":{"best_composite_score":0.10878,"best_fitness_score":0.68878,"best_task_score":0.42312},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":159.0,"contact_point_centroid":[0.62832,0.17366,-0.00742],"force_p95":1.30604,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.83418,"mean_force":0.43441,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61789,0.16536,0.17215]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.51012,0.03707,-0.00149],"force_p95":0.51922,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64104,"mean_force":0.12203,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49805,0.03768,0.03208]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5028.0,"contact_point_centroid":[0.50412,0.01865,0.08393],"force_p95":0.11131,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33949,"mean_force":0.07332,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.5011,0.03754,0.08159]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5423.0,"contact_point_centroid":[0.50371,0.0564,0.08076],"force_p95":0.10878,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33475,"mean_force":0.06967,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50085,0.03754,0.07885]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51258,0.03936,-0.00217],"force_p95":0.17368,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25101,"mean_force":0.13594,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50028,0.03788,0.03193]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5175.0,"contact_point_centroid":[0.5549,0.06914,0.15637],"force_p95":0.15534,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24168,"mean_force":0.09519,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54929,0.08752,0.15735]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5173.0,"contact_point_centroid":[0.55927,0.11129,0.1578],"force_p95":0.13492,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20667,"mean_force":0.09535,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55407,0.09293,0.15916]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3770.0,"contact_point_centroid":[0.50032,0.0186,0.03367],"force_p95":0.08632,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15561,"mean_force":0.0555,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.49911,0.03779,0.03066]},{"body_a":"world","body_b":"grasp_target","contact_count":1180.0,"contact_point_centroid":[0.51251,0.03972,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50305,0.01635,0.22524]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.62819,0.17382,-0.00207],"force_p95":0.12694,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12835,"mean_force":0.1159,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61502,0.16582,0.16723]},{"body_a":"world","body_b":"grasp_target","contact_count":740.0,"contact_point_centroid":[0.62819,0.17383,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.61715,0.16767,0.20572]},{"body_a":"world","body_b":"grasp_target","contact_count":1016.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.5064,0.03608,0.09395]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4959.0,"contact_point_centroid":[0.49987,0.05694,0.03251],"force_p95":0.07657,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08533,"mean_force":0.04534,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.49912,0.03779,0.03067]},{"body_a":"left_finger","body_b":"right_finger","contact_count":133.0,"contact_point_centroid":[0.61793,0.16658,0.1651],"force_p95":0.01441,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01635,"mean_force":0.01147,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.6172,0.16655,0.1625]}],"total_contact_groups":14},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62819,0.17383,0.01602],"final_tcp_position":[0.62203,0.17026,0.226],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.83418,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":296.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1180.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50755,0.0339,0.14819],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12241,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":254.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_to_grasp","tcp_end":[0.50749,0.03845,0.0399],"tcp_start":[0.50755,0.0339,0.14819],"tcp_to_object_dist_end":0.01482,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.03793,0.02543],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21371,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.16175,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10529.0,"raw_peak_contact_force":0.25101,"tcp_end":[0.49908,0.03778,0.03063],"tcp_start":[0.50749,0.03845,0.0399],"tcp_to_object_dist_end":0.01433,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":353.0,"n_steps_budget":600.0,"object_pos_end":[0.52639,0.0379,0.13193],"object_pos_start":[0.51243,0.03793,0.02543],"object_to_goal_dist_end":0.16891,"object_to_goal_dist_start":0.21371,"object_z_max":0.13169,"peak_contact_force":0.10627,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10529.0,"raw_peak_contact_force":0.64104,"subtask_id":"lift_object","tcp_end":[0.50741,0.03761,0.14412],"tcp_start":[0.49908,0.03778,0.03063],"tcp_to_object_dist_end":0.02256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":579.0,"n_steps_budget":1000.0,"object_pos_end":[0.62431,0.17148,0.08701],"object_pos_start":[0.52639,0.0379,0.13193],"object_to_goal_dist_end":0.05812,"object_to_goal_dist_start":0.16891,"object_z_max":0.15388,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10348.0,"raw_peak_contact_force":0.24168,"subtask_id":"approach_goal","tcp_end":[0.61568,0.16202,0.18298],"tcp_start":[0.50741,0.03761,0.14412],"tcp_to_object_dist_end":0.09682,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":66.0,"n_steps_budget":1000.0,"object_pos_end":[0.62889,0.17634,0.01009],"object_pos_start":[0.62431,0.17148,0.08701],"object_to_goal_dist_end":0.135,"object_to_goal_dist_start":0.05812,"object_z_max":0.08701,"peak_contact_force":0.10499,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":159.0,"raw_peak_contact_force":1.83418,"subtask_id":"place_object","tcp_end":[0.61941,0.16703,0.16725],"tcp_start":[0.61568,0.16202,0.18298],"tcp_to_object_dist_end":0.15773,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62819,0.17383,0.01602],"object_pos_start":[0.62889,0.17634,0.01009],"object_to_goal_dist_end":0.12901,"object_to_goal_dist_start":0.135,"object_z_max":0.01663,"peak_contact_force":0.12264,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":933.0,"raw_peak_contact_force":0.12835,"tcp_end":[0.61341,0.16529,0.18667],"tcp_start":[0.61941,0.16703,0.16725],"tcp_to_object_dist_end":0.1715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":185.0,"n_steps_budget":600.0,"object_pos_end":[0.62819,0.17383,0.01602],"object_pos_start":[0.62819,0.17383,0.01602],"object_to_goal_dist_end":0.12901,"object_to_goal_dist_start":0.12901,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":740.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.62203,0.17026,0.226],"tcp_start":[0.61341,0.16529,0.18667],"tcp_to_object_dist_end":0.2101,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```