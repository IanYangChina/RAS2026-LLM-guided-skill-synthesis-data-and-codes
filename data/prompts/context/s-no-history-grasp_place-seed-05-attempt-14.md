## Search State

- **Seed**: 5
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
| approach_object | 1.00 | 1.00 | 0.1553 |
| descend_to_grasp | 1.00 | 1.00 | 0.1087 |
| grasp_action | 1.00 | 1.00 | 0.0126 |
| lift_object | 1.00 | 1.00 | 0.1311 |
| approach_goal | 1.00 | 0.33 | 0.1850 |
| descend_to_place | 1.00 | 1.00 | 0.0346 |
| release_object | 1.00 | 1.00 | 0.0210 |
| retract_after_place | 1.00 | 1.00 | 0.1058 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.148) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 16.808 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, 0.016, 0.148)→(0.510, 0.018, 0.040) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_action | grasp | 1.00 / step_budget | (0.510, 0.018, 0.040)→(0.502, 0.017, 0.030) | (0.516, 0.018, 0.026)→(0.516, 0.017, 0.026) | 0.236→0.237 | 1.00 / 41.000 | 0.151 | 0.224 |
| lift_object | lift | 1.00 / step_budget | (0.502, 0.017, 0.030)→(0.511, 0.017, 0.161) | (0.516, 0.017, 0.026)→(0.529, 0.017, 0.150) | 0.237→0.189 | 1.00 / 22.333 | 0.113 | 0.589 |
| approach_goal | approach | 1.00 / step_budget | (0.511, 0.017, 0.161)→(0.595, 0.167, 0.206) | (0.529, 0.017, 0.150)→(0.603, 0.169, 0.148) | 0.189→0.038 | 0.33 / 7.667 | 55983.910 | 0.211 |
| descend_to_place | descend | 1.00 / step_budget | (0.595, 0.167, 0.206)→(0.599, 0.174, 0.172) | (0.603, 0.169, 0.148)→(0.605, 0.177, 0.088) | 0.038→0.079 | 1.00 / 10.667 | 0.130 | 1.225 |
| release_object | release | 1.00 / step_budget | (0.599, 0.174, 0.172)→(0.593, 0.173, 0.192) | (0.605, 0.177, 0.088)→(0.602, 0.179, 0.011) | 0.079→0.156 | 1.00 / 4.000 | 0.180 | 0.781 |
| retract_after_place | retract | 1.00 / step_budget | (0.593, 0.173, 0.192)→(0.602, 0.178, 0.298) | (0.602, 0.179, 0.011)→(0.603, 0.181, 0.016) | 0.156→0.151 | 1.00 / 4.000 | 0.123 | 0.174 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.541
- phase_score: 0.551
- phase_breakdown.approach_object_score: 0.671
- phase_breakdown.place_object_score: 0.000
- phase_breakdown.lift_object_score: 0.559
- phase_breakdown.approach_goal_score: 0.672
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
- **Final σ (mean)**: 0.324


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21591,"average_solve_count":264.0,"average_success_count":264.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.03128,"approach_object.approach_speed":0.10365,"descend_to_place.place_speed":0.0206,"grasp_action.grasp_duration":1.33954,"lift_object.lift_height":0.14516,"lift_object.lift_speed":0.10628,"release_object.release_duration":0.14372,"retract_after_place.retract_speed":0.15231},"optimized_scores":{"best_composite_score":0.16705,"best_fitness_score":0.74705,"best_task_score":0.54115},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":303.0,"contact_point_centroid":[0.60273,0.17415,-0.00485],"force_p95":1.10414,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.56509,"mean_force":0.28452,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59249,0.17021,0.12253]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.52821,0.02839,-0.00146],"force_p95":0.5019,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59146,"mean_force":0.11445,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51517,0.02913,0.03117]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5894.0,"contact_point_centroid":[0.52153,0.04779,0.08372],"force_p95":0.11088,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30809,"mean_force":0.07338,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51815,0.02899,0.08182]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5636.0,"contact_point_centroid":[0.52188,0.01017,0.08661],"force_p95":0.11101,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30028,"mean_force":0.07549,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51839,0.02899,0.08443]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03049,-0.00214],"force_p95":0.16468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24369,"mean_force":0.13373,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.51743,0.0293,0.03111]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4280.0,"contact_point_centroid":[0.5583,0.10844,0.14652],"force_p95":0.16587,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21681,"mean_force":0.10053,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55349,0.09005,0.14829]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4837.0,"contact_point_centroid":[0.55837,0.07134,0.14654],"force_p95":0.13645,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21249,"mean_force":0.0916,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55325,0.08955,0.14831]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4058.0,"contact_point_centroid":[0.51719,0.01002,0.03251],"force_p95":0.08135,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14982,"mean_force":0.05193,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.51622,0.02922,0.02977]},{"body_a":"world","body_b":"grasp_target","contact_count":1204.0,"contact_point_centroid":[0.5305,0.03079,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12303,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51054,0.01268,0.22509]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.6026,0.17611,-0.00197],"force_p95":0.1294,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13433,"mean_force":0.12293,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58924,0.17174,0.11306]},{"body_a":"world","body_b":"grasp_target","contact_count":1008.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52283,0.02795,0.09366]},{"body_a":"world","body_b":"grasp_target","contact_count":1596.0,"contact_point_centroid":[0.6026,0.17611,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.59114,0.1737,0.1858]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5016.0,"contact_point_centroid":[0.51711,0.04839,0.03156],"force_p95":0.07403,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08638,"mean_force":0.04467,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.51623,0.02922,0.02977]},{"body_a":"left_finger","body_b":"right_finger","contact_count":69.0,"contact_point_centroid":[0.59438,0.17256,0.1169],"force_p95":0.01532,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01565,"mean_force":0.01321,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59389,0.17253,0.11448]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.59281,0.17281,0.11123],"force_p95":0.01189,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01222,"mean_force":0.01032,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59238,0.17278,0.10902]}],"total_contact_groups":15},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.6026,0.17611,0.01602],"final_tcp_position":[0.59746,0.17694,0.23879],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.56509,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":302.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1204.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52304,0.02628,0.14793],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12222,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1008.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_to_grasp","tcp_end":[0.52483,0.02977,0.03962],"tcp_start":[0.52304,0.02628,0.14793],"tcp_to_object_dist_end":0.01477,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53041,0.0293,0.02552],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18483,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15597,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10874.0,"raw_peak_contact_force":0.24369,"tcp_end":[0.51619,0.02921,0.02973],"tcp_start":[0.52483,0.02977,0.03962],"tcp_to_object_dist_end":0.01482,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":409.0,"n_steps_budget":840.0,"object_pos_end":[0.54446,0.02932,0.13987],"object_pos_start":[0.53041,0.0293,0.02552],"object_to_goal_dist_end":0.16293,"object_to_goal_dist_start":0.18483,"object_z_max":0.13962,"peak_contact_force":0.11726,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11612.0,"raw_peak_contact_force":0.59146,"subtask_id":"lift_object","tcp_end":[0.52524,0.02903,0.15142],"tcp_start":[0.51619,0.02921,0.02973],"tcp_to_object_dist_end":0.02243,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":478.0,"n_steps_budget":1000.0,"object_pos_end":[0.59832,0.15889,0.11303],"object_pos_start":[0.54446,0.02932,0.13987],"object_to_goal_dist_end":0.02056,"object_to_goal_dist_start":0.16293,"object_z_max":0.14007,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9117.0,"raw_peak_contact_force":0.21681,"subtask_id":"approach_goal","tcp_end":[0.5909,0.16408,0.1496],"tcp_start":[0.52524,0.02903,0.15142],"tcp_to_object_dist_end":0.03767,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":139.0,"n_steps_budget":1000.0,"object_pos_end":[0.60258,0.17628,0.01666],"object_pos_start":[0.59832,0.15889,0.11303],"object_to_goal_dist_end":0.09146,"object_to_goal_dist_start":0.02056,"object_z_max":0.11303,"peak_contact_force":0.13408,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":372.0,"raw_peak_contact_force":1.56509,"subtask_id":"place_object","tcp_end":[0.59432,0.17319,0.11237],"tcp_start":[0.5909,0.16408,0.1496],"tcp_to_object_dist_end":0.09611,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6026,0.17611,0.01602],"object_pos_start":[0.60258,0.17628,0.01666],"object_to_goal_dist_end":0.09211,"object_to_goal_dist_start":0.09146,"object_z_max":0.01666,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.13433,"tcp_end":[0.58734,0.17111,0.13284],"tcp_start":[0.59432,0.17319,0.11237],"tcp_to_object_dist_end":0.11792,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":399.0,"n_steps_budget":600.0,"object_pos_end":[0.6026,0.17611,0.01602],"object_pos_start":[0.6026,0.17611,0.01602],"object_to_goal_dist_end":0.09211,"object_to_goal_dist_start":0.09211,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1596.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59746,0.17694,0.23879],"tcp_start":[0.58734,0.17111,0.13284],"tcp_to_object_dist_end":0.22283,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17647,"average_solve_count":272.0,"average_success_count":272.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.0453,"approach_object.approach_speed":0.13755,"descend_to_place.place_speed":0.02068,"grasp_action.grasp_duration":1.86501,"lift_object.lift_height":0.15556,"lift_object.lift_speed":0.06725,"release_object.release_duration":0.13377,"retract_after_place.retract_speed":0.23144},"optimized_scores":{"best_composite_score":0.00415,"best_fitness_score":0.58415,"best_task_score":0.2127},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":118.0,"contact_point_centroid":[0.58103,0.19308,-0.00985],"force_p95":1.60982,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.07998,"mean_force":0.655,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57777,0.18082,0.27073]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.50118,-0.01523,-0.00137],"force_p95":0.49875,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5828,"mean_force":0.13791,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48979,-0.01515,0.03221]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":636.0,"contact_point_centroid":[0.584,0.19995,0.24622],"force_p95":0.13155,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31894,"mean_force":0.08298,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58029,0.18187,0.25067]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7420.0,"contact_point_centroid":[0.49447,0.00393,0.09395],"force_p95":0.10173,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31688,"mean_force":0.06372,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49263,-0.01507,0.09187]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":429.0,"contact_point_centroid":[0.58425,0.16364,0.2469],"force_p95":0.16277,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3029,"mean_force":0.11025,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58034,0.18189,0.25081]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7980.0,"contact_point_centroid":[0.4941,-0.03401,0.09123],"force_p95":0.10141,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2907,"mean_force":0.06021,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49243,-0.01507,0.08953]},{"body_a":"world","body_b":"grasp_target","contact_count":1488.0,"contact_point_centroid":[0.58283,0.1922,-0.00219],"force_p95":0.12878,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27642,"mean_force":0.11914,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.58066,0.18334,0.32642]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":910.0,"contact_point_centroid":[0.58541,0.16071,0.26819],"force_p95":0.1376,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23293,"mean_force":0.09635,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5805,0.17877,0.27113]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":890.0,"contact_point_centroid":[0.58525,0.19703,0.26773],"force_p95":0.13903,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22312,"mean_force":0.1006,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58051,0.1788,0.27094]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01551,-0.00205],"force_p95":0.13719,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17738,"mean_force":0.12664,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.4919,-0.01518,0.03216]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10934.0,"contact_point_centroid":[0.54235,0.1004,0.22141],"force_p95":0.10784,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1656,"mean_force":0.07461,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53831,0.08179,0.22122]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11249.0,"contact_point_centroid":[0.54143,0.06102,0.22007],"force_p95":0.10684,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15983,"mean_force":0.0732,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.53735,0.07959,0.21978]},{"body_a":"world","body_b":"grasp_target","contact_count":1112.0,"contact_point_centroid":[0.50382,-0.01567,-0.00188],"force_p95":0.13647,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49947,-0.00642,0.22591]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4101.0,"contact_point_centroid":[0.49125,0.00404,0.03371],"force_p95":0.07716,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12291,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.49074,-0.01517,0.03094]},{"body_a":"world","body_b":"grasp_target","contact_count":1028.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49843,-0.01427,0.09434]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4904.0,"contact_point_centroid":[0.4913,-0.03425,0.03279],"force_p95":0.06923,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09205,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.49074,-0.01517,0.03095]}],"total_contact_groups":16},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.58282,0.19215,0.01602],"final_tcp_position":[0.58506,0.18627,0.37825],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":279.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1112.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50004,-0.01334,0.14914],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1232,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":257.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_to_grasp","tcp_end":[0.49902,-0.01526,0.03984],"tcp_start":[0.50004,-0.01334,0.14914],"tcp_to_object_dist_end":0.01464,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5037,-0.01507,0.02583],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31201,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13405,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10805.0,"raw_peak_contact_force":0.17738,"tcp_end":[0.49071,-0.01517,0.03091],"tcp_start":[0.49902,-0.01526,0.03984],"tcp_to_object_dist_end":0.01395,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":450.0,"n_steps_budget":1000.0,"object_pos_end":[0.51529,-0.01501,0.15126],"object_pos_start":[0.5037,-0.01507,0.02583],"object_to_goal_dist_end":0.23558,"object_to_goal_dist_start":0.31201,"object_z_max":0.15101,"peak_contact_force":0.10695,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15480.0,"raw_peak_contact_force":0.5828,"subtask_id":"lift_object","tcp_end":[0.49882,-0.01502,0.16207],"tcp_start":[0.49071,-0.01517,0.03091],"tcp_to_object_dist_end":0.0197,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":834.0,"n_steps_budget":1000.0,"object_pos_end":[0.58897,0.17615,0.26195],"object_pos_start":[0.51529,-0.01501,0.15126],"object_to_goal_dist_end":0.01798,"object_to_goal_dist_start":0.23558,"object_z_max":0.26184,"peak_contact_force":167951.73011,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22183.0,"raw_peak_contact_force":0.1656,"subtask_id":"approach_goal","tcp_end":[0.58009,0.17623,0.28323],"tcp_start":[0.49882,-0.01502,0.16207],"tcp_to_object_dist_end":0.02306,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":97.0,"n_steps_budget":1000.0,"object_pos_end":[0.58973,0.18219,0.23221],"object_pos_start":[0.58897,0.17615,0.26195],"object_to_goal_dist_end":0.01699,"object_to_goal_dist_start":0.01798,"object_z_max":0.26196,"peak_contact_force":0.12837,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1800.0,"raw_peak_contact_force":0.23293,"subtask_id":"place_object","tcp_end":[0.58194,0.18229,0.25505],"tcp_start":[0.58009,0.17623,0.28323],"tcp_to_object_dist_end":0.02413,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58156,0.18737,0.00134],"object_pos_start":[0.58973,0.18219,0.23221],"object_to_goal_dist_end":0.24684,"object_to_goal_dist_start":0.01699,"object_z_max":0.23221,"peak_contact_force":0.2948,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1183.0,"raw_peak_contact_force":2.07998,"tcp_end":[0.57775,0.18081,0.27545],"tcp_start":[0.58194,0.18229,0.25505],"tcp_to_object_dist_end":0.27421,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":372.0,"n_steps_budget":600.0,"object_pos_end":[0.58282,0.19215,0.01602],"object_pos_start":[0.58156,0.18737,0.00134],"object_to_goal_dist_end":0.23218,"object_to_goal_dist_start":0.24684,"object_z_max":0.01689,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1488.0,"raw_peak_contact_force":0.27642,"tcp_end":[0.58506,0.18627,0.37825],"tcp_start":[0.57775,0.18081,0.27545],"tcp_to_object_dist_end":0.36229,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37264,"average_solve_count":212.0,"average_success_count":212.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.05014,"approach_object.approach_speed":0.15418,"descend_to_place.place_speed":0.0232,"grasp_action.grasp_duration":1.26145,"lift_object.lift_height":0.16404,"lift_object.lift_speed":0.11691,"release_object.release_duration":0.13953,"retract_after_place.retract_speed":0.17958},"optimized_scores":{"best_composite_score":0.10868,"best_fitness_score":0.68868,"best_task_score":0.42292},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":425.0,"contact_point_centroid":[0.62341,0.17398,-0.00429],"force_p95":0.89137,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.8771,"mean_force":0.22967,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61694,0.16471,0.16442]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.51022,0.03714,-0.00147],"force_p95":0.56393,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59361,"mean_force":0.12459,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49803,0.03768,0.03214]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6797.0,"contact_point_centroid":[0.50375,0.05639,0.09185],"force_p95":0.1095,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31466,"mean_force":0.0702,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50081,0.03753,0.08996]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6416.0,"contact_point_centroid":[0.50416,0.01867,0.09551],"force_p95":0.11041,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30725,"mean_force":0.07292,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.50106,0.03753,0.09329]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4918.0,"contact_point_centroid":[0.55536,0.06993,0.17195],"force_p95":0.14369,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25111,"mean_force":0.09209,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55031,0.08825,0.17381]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51258,0.03936,-0.00217],"force_p95":0.1737,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25105,"mean_force":0.13594,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50028,0.03788,0.03191]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4826.0,"contact_point_centroid":[0.55896,0.11106,0.17214],"force_p95":0.13622,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19297,"mean_force":0.09391,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55428,0.09277,0.17443]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3766.0,"contact_point_centroid":[0.50032,0.0186,0.03366],"force_p95":0.08635,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15562,"mean_force":0.05555,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.4991,0.03779,0.03065]},{"body_a":"world","body_b":"grasp_target","contact_count":1124.0,"contact_point_centroid":[0.51251,0.03972,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50308,0.01634,0.22525]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.62333,0.17413,-0.00199],"force_p95":0.12381,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12725,"mean_force":0.12286,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61529,0.16662,0.14917]},{"body_a":"world","body_b":"grasp_target","contact_count":1016.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50638,0.03608,0.09391]},{"body_a":"world","body_b":"grasp_target","contact_count":1676.0,"contact_point_centroid":[0.62333,0.17413,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.61771,0.16832,0.22203]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4958.0,"contact_point_centroid":[0.49986,0.05694,0.0325],"force_p95":0.07658,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08537,"mean_force":0.04535,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.49911,0.03779,0.03066]},{"body_a":"left_finger","body_b":"right_finger","contact_count":195.0,"contact_point_centroid":[0.61901,0.16644,0.15794],"force_p95":0.01508,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01621,"mean_force":0.01201,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61845,0.16641,0.15568]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.61866,0.16759,0.14786],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01105,"mean_force":0.0102,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61818,0.16756,0.14561]}],"total_contact_groups":15},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62333,0.17413,0.01602],"final_tcp_position":[0.62409,0.17115,0.27555],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":50.17974,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":282.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":50.17974,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1124.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50752,0.0339,0.14812],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":254.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_to_grasp","tcp_end":[0.50748,0.03845,0.03989],"tcp_start":[0.50752,0.0339,0.14812],"tcp_to_object_dist_end":0.01481,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.03793,0.02543],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21371,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.16172,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10524.0,"raw_peak_contact_force":0.25105,"tcp_end":[0.49908,0.03778,0.03062],"tcp_start":[0.50748,0.03845,0.03989],"tcp_to_object_dist_end":0.01433,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":450.0,"n_steps_budget":870.0,"object_pos_end":[0.52653,0.03789,0.15755],"object_pos_start":[0.51243,0.03793,0.02543],"object_to_goal_dist_end":0.16879,"object_to_goal_dist_start":0.21371,"object_z_max":0.1573,"peak_contact_force":0.11386,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13295.0,"raw_peak_contact_force":0.59361,"subtask_id":"lift_object","tcp_end":[0.50774,0.03762,0.17016],"tcp_start":[0.49908,0.03778,0.03062],"tcp_to_object_dist_end":0.02263,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":544.0,"n_steps_budget":1000.0,"object_pos_end":[0.62286,0.17311,0.06872],"object_pos_start":[0.52653,0.03789,0.15755],"object_to_goal_dist_end":0.07645,"object_to_goal_dist_start":0.16879,"object_z_max":0.15813,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9744.0,"raw_peak_contact_force":0.25111,"subtask_id":"approach_goal","tcp_end":[0.615,0.16119,0.18472],"tcp_start":[0.50774,0.03762,0.17016],"tcp_to_object_dist_end":0.11687,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":125.0,"n_steps_budget":1000.0,"object_pos_end":[0.62329,0.17397,0.01618],"object_pos_start":[0.62286,0.17311,0.06872],"object_to_goal_dist_end":0.12893,"object_to_goal_dist_start":0.07645,"object_z_max":0.06872,"peak_contact_force":0.12745,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":620.0,"raw_peak_contact_force":1.8771,"subtask_id":"place_object","tcp_end":[0.61998,0.16795,0.14928],"tcp_start":[0.615,0.16119,0.18472],"tcp_to_object_dist_end":0.13328,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62333,0.17413,0.01602],"object_pos_start":[0.62329,0.17397,0.01618],"object_to_goal_dist_end":0.12909,"object_to_goal_dist_start":0.12893,"object_z_max":0.01618,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12725,"tcp_end":[0.61358,0.16607,0.16862],"tcp_start":[0.61998,0.16795,0.14928],"tcp_to_object_dist_end":0.15312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":419.0,"n_steps_budget":600.0,"object_pos_end":[0.62333,0.17413,0.01602],"object_pos_start":[0.62333,0.17413,0.01602],"object_to_goal_dist_end":0.12909,"object_to_goal_dist_start":0.12909,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1676.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62409,0.17115,0.27555],"tcp_start":[0.61358,0.16607,0.16862],"tcp_to_object_dist_end":0.25954,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```