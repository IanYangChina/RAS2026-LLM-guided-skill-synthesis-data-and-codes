## Search State

- **Seed**: 5
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
| descend_to_grasp | 1.00 | 1.00 | 0.1085 |
| grasp_action | 1.00 | 1.00 | 0.0126 |
| lift_object | 1.00 | 1.00 | 0.1101 |
| approach_goal | 0.33 | 1.00 | 0.1131 |
| descend_to_place | 1.00 | 1.00 | 0.0611 |
| release_object | 1.00 | 1.00 | 0.0213 |
| retract_after_place | 1.00 | 1.00 | 0.0418 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.148) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, 0.016, 0.148)→(0.510, 0.018, 0.040) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_action | grasp | 1.00 / step_budget | (0.510, 0.018, 0.040)→(0.502, 0.017, 0.031) | (0.516, 0.018, 0.026)→(0.516, 0.017, 0.026) | 0.236→0.237 | 1.00 / 41.000 | 0.151 | 0.224 |
| lift_object | lift | 1.00 / step_budget | (0.502, 0.017, 0.031)→(0.498, 0.017, 0.141) | (0.516, 0.017, 0.026)→(0.516, 0.017, 0.130) | 0.237→0.200 | 1.00 / 22.667 | 0.109 | 0.622 |
| approach_goal | approach | 0.33 / guard_failure | (0.505, 0.033, 0.152)→(0.571, 0.122, 0.166) | (0.516, 0.017, 0.130)→(0.545, 0.079, 0.137) | 0.200→0.131 | 1.00 / 22.333 | 3253.472 | 0.203 |
| descend_to_place | descend | 1.00 / step_budget | (0.571, 0.122, 0.166)→(0.597, 0.171, 0.188) | (0.582, 0.122, 0.146)→(0.604, 0.172, 0.163) | 0.077→0.023 | 1.00 / 14.333 | 50723.764 | 0.282 |
| release_object | release | 1.00 / step_budget | (0.597, 0.171, 0.188)→(0.591, 0.170, 0.209) | (0.604, 0.172, 0.163)→(0.608, 0.179, 0.016) | 0.023→0.152 | 1.00 / 4.000 | 0.117 | 1.728 |
| retract_after_place | retract | 1.00 / step_budget | (0.591, 0.170, 0.209)→(0.600, 0.177, 0.248) | (0.608, 0.179, 0.016)→(0.608, 0.179, 0.016) | 0.152→0.151 | 1.00 / 4.000 | 0.123 | 0.126 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.541
- phase_score: 0.609
- phase_breakdown.approach_object_score: 0.675
- phase_breakdown.place_object_score: 0.319
- phase_breakdown.lift_object_score: 0.490
- phase_breakdown.approach_goal_score: 0.671
- phase_breakdown.descend_to_grasp_score: 0.797
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
- **Final σ (mean)**: 0.307


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55747,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.07355,"approach_object.approach_speed":0.13675,"descend_to_place.place_speed":0.06573,"descend_to_place.place_z_offset":0.03801,"grasp_action.grasp_duration":1.30389,"lift_object.lift_height":0.13895,"lift_object.lift_speed":0.09071,"release_object.release_duration":0.89203},"optimized_scores":{"best_composite_score":0.16692,"best_fitness_score":0.74692,"best_task_score":0.54102},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":514.0,"contact_point_centroid":[0.60318,0.17572,-0.00362],"force_p95":0.90878,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.49945,"mean_force":0.20884,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5854,0.16608,0.14954]},{"body_a":"world","body_b":"grasp_target","contact_count":83.0,"contact_point_centroid":[0.52781,0.02865,-0.00145],"force_p95":0.54999,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62434,"mean_force":0.1311,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51493,0.02912,0.03136]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":211.0,"contact_point_centroid":[0.59275,0.18351,0.14253],"force_p95":0.17814,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33352,"mean_force":0.10708,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59026,0.16594,0.14799]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5583.0,"contact_point_centroid":[0.51555,0.0101,0.08548],"force_p95":0.11109,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32283,"mean_force":0.0744,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51235,0.02895,0.08323]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5911.0,"contact_point_centroid":[0.51553,0.04778,0.08292],"force_p95":0.10927,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32216,"mean_force":0.07161,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.51239,0.02895,0.081]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":124.0,"contact_point_centroid":[0.59573,0.14802,0.14271],"force_p95":0.26542,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32039,"mean_force":0.16846,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59024,0.16589,0.14806]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":99.0,"contact_point_centroid":[0.5951,0.18335,0.13917],"force_p95":0.19419,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24851,"mean_force":0.07708,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5907,0.16786,0.14478]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3.0,"contact_point_centroid":[0.59879,0.1529,0.1387],"force_p95":0.24248,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24725,"mean_force":0.17822,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.59131,0.16768,0.14592]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03049,-0.00214],"force_p95":0.16467,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24339,"mean_force":0.13373,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.51744,0.0293,0.03129]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4637.0,"contact_point_centroid":[0.55187,0.07298,0.14635],"force_p95":0.15842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21233,"mean_force":0.09513,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54682,0.09133,0.14739]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4792.0,"contact_point_centroid":[0.55379,0.11358,0.14603],"force_p95":0.14366,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1965,"mean_force":0.0939,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.54908,0.09527,0.14741]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4058.0,"contact_point_centroid":[0.5172,0.01002,0.03269],"force_p95":0.08135,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14979,"mean_force":0.05193,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.51623,0.02922,0.02995]},{"body_a":"world","body_b":"grasp_target","contact_count":1176.0,"contact_point_centroid":[0.5305,0.03079,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51056,0.01273,0.22476]},{"body_a":"world","body_b":"grasp_target","contact_count":496.0,"contact_point_centroid":[0.60326,0.17528,-0.00199],"force_p95":0.12336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12372,"mean_force":0.12266,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.5892,0.17008,0.17765]},{"body_a":"world","body_b":"grasp_target","contact_count":1004.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52279,0.02797,0.09362]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5016.0,"contact_point_centroid":[0.51712,0.04839,0.03174],"force_p95":0.07404,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08624,"mean_force":0.04466,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.51624,0.02922,0.02995]}],"total_contact_groups":16},"final_pose_error":0.01981,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.60326,0.17528,0.01602],"final_tcp_position":[0.59425,0.1744,0.19015],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":152170.99322,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":295.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1176.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.52297,0.02632,0.14762],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":251.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1004.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_to_grasp","tcp_end":[0.52485,0.02977,0.03981],"tcp_start":[0.52297,0.02632,0.14762],"tcp_to_object_dist_end":0.01494,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53041,0.0293,0.02552],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18483,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15597,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10874.0,"raw_peak_contact_force":0.24339,"tcp_end":[0.51621,0.02922,0.02991],"tcp_start":[0.52485,0.02977,0.03981],"tcp_to_object_dist_end":0.01486,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":396.0,"n_steps_budget":960.0,"object_pos_end":[0.53135,0.0291,0.13847],"object_pos_start":[0.53041,0.0293,0.02552],"object_to_goal_dist_end":0.16791,"object_to_goal_dist_start":0.18483,"object_z_max":0.13821,"peak_contact_force":0.11143,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11577.0,"raw_peak_contact_force":0.62434,"subtask_id":"lift_object","tcp_end":[0.51234,0.02896,0.1494],"tcp_start":[0.51621,0.02922,0.02991],"tcp_to_object_dist_end":0.02193,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":467.0,"n_steps_budget":1000.0,"object_pos_end":[0.59729,0.16458,0.12618],"object_pos_start":[0.53135,0.0291,0.13847],"object_to_goal_dist_end":0.02327,"object_to_goal_dist_start":0.16791,"object_z_max":0.13871,"peak_contact_force":9760.30694,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9429.0,"raw_peak_contact_force":0.21233,"subtask_id":"approach_goal","tcp_end":[0.59015,0.16468,0.14948],"tcp_start":[0.51234,0.02896,0.1494],"tcp_to_object_dist_end":0.02437,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":25.0,"n_steps_budget":1000.0,"object_pos_end":[0.59922,0.16877,0.12032],"object_pos_start":[0.59729,0.16458,0.12618],"object_to_goal_dist_end":0.01584,"object_to_goal_dist_start":0.02327,"object_z_max":0.12618,"peak_contact_force":152170.99322,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":335.0,"raw_peak_contact_force":0.33352,"subtask_id":"place_object","tcp_end":[0.59133,0.16765,0.14599],"tcp_start":[0.59015,0.16468,0.14948],"tcp_to_object_dist_end":0.02688,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60326,0.17522,0.016],"object_pos_start":[0.59922,0.16877,0.12032],"object_to_goal_dist_end":0.09216,"object_to_goal_dist_start":0.01584,"object_z_max":0.12032,"peak_contact_force":0.12374,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":616.0,"raw_peak_contact_force":1.49945,"tcp_end":[0.58498,0.16594,0.16659],"tcp_start":[0.59133,0.16765,0.14599],"tcp_to_object_dist_end":0.15198,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":124.0,"n_steps_budget":600.0,"object_pos_end":[0.60326,0.17528,0.01602],"object_pos_start":[0.60326,0.17522,0.016],"object_to_goal_dist_end":0.09215,"object_to_goal_dist_start":0.09216,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":496.0,"raw_peak_contact_force":0.12372,"tcp_end":[0.59425,0.1744,0.19015],"tcp_start":[0.58498,0.16594,0.16659],"tcp_to_object_dist_end":0.17436,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80556,"average_solve_count":180.0,"average_success_count":180.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.03316,"approach_object.approach_speed":0.19827,"descend_to_place.place_speed":0.07688,"descend_to_place.place_z_offset":6e-05,"grasp_action.grasp_duration":1.7469,"lift_object.lift_height":0.1159,"lift_object.lift_speed":0.10353,"release_object.release_duration":0.90646},"optimized_scores":{"best_composite_score":0.00405,"best_fitness_score":0.58405,"best_task_score":0.21265},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":397.0,"contact_point_centroid":[0.59243,0.19227,-0.00512],"force_p95":1.03066,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.01991,"mean_force":0.2465,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.57639,0.17885,0.24372]},{"body_a":"world","body_b":"grasp_target","contact_count":73.0,"contact_point_centroid":[0.50064,-0.01495,-0.00136],"force_p95":0.54412,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61048,"mean_force":0.14384,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48951,-0.01515,0.03239]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4858.0,"contact_point_centroid":[0.48889,0.00395,0.07705],"force_p95":0.10598,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33689,"mean_force":0.06608,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4871,-0.01511,0.07454]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5405.0,"contact_point_centroid":[0.48898,-0.03402,0.07538],"force_p95":0.10106,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30513,"mean_force":0.06076,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48711,-0.01511,0.07367]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":39.0,"contact_point_centroid":[0.58751,0.16272,0.23007],"force_p95":0.20165,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21948,"mean_force":0.13783,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58057,0.18041,0.23652]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":122.0,"contact_point_centroid":[0.58529,0.19638,0.23021],"force_p95":0.16133,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20818,"mean_force":0.06953,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.58026,0.18039,0.2358]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9257.0,"contact_point_centroid":[0.54516,0.08672,0.19585],"force_p95":0.1463,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20807,"mean_force":0.08595,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54111,0.10522,0.19683]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01551,-0.00205],"force_p95":0.13726,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17756,"mean_force":0.12665,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.4919,-0.01518,0.03231]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9923.0,"contact_point_centroid":[0.54658,0.1252,0.19652],"force_p95":0.12553,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17365,"mean_force":0.08084,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.54198,0.10685,0.19771]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3133.0,"contact_point_centroid":[0.50188,-0.0062,0.14714],"force_p95":0.10612,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16077,"mean_force":0.07629,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49757,0.01232,0.14643]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2868.0,"contact_point_centroid":[0.50199,0.0313,0.14805],"force_p95":0.11022,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15461,"mean_force":0.08079,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.49772,0.01263,0.14669]},{"body_a":"world","body_b":"grasp_target","contact_count":1056.0,"contact_point_centroid":[0.50382,-0.01567,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49949,-0.00642,0.22587]},{"body_a":"world","body_b":"grasp_target","contact_count":1088.0,"contact_point_centroid":[0.59263,0.19203,-0.00199],"force_p95":0.12416,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12656,"mean_force":0.12288,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.57938,0.18208,0.29261]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4101.0,"contact_point_centroid":[0.49125,0.00404,0.03386],"force_p95":0.07717,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12312,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.49074,-0.01516,0.03109]},{"body_a":"world","body_b":"grasp_target","contact_count":1028.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49842,-0.01426,0.09453]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4904.0,"contact_point_centroid":[0.4913,-0.03425,0.03294],"force_p95":0.06925,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09208,"mean_force":0.04474,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.49074,-0.01516,0.0311]}],"total_contact_groups":16},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.59263,0.19204,0.01602],"final_tcp_position":[0.58381,0.18561,0.32848],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":2.01991,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":265.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1056.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50003,-0.01332,0.1492],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12326,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":257.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_to_grasp","tcp_end":[0.49902,-0.01525,0.04],"tcp_start":[0.50003,-0.01332,0.1492],"tcp_to_object_dist_end":0.01479,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5037,-0.01507,0.02582],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31201,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13411,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10805.0,"raw_peak_contact_force":0.17756,"tcp_end":[0.49071,-0.01516,0.03106],"tcp_start":[0.49902,-0.01525,0.04],"tcp_to_object_dist_end":0.014,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":304.0,"n_steps_budget":720.0,"object_pos_end":[0.50456,-0.01495,0.11865],"object_pos_start":[0.5037,-0.01507,0.02582],"object_to_goal_dist_end":0.25399,"object_to_goal_dist_start":0.31201,"object_z_max":0.11839,"peak_contact_force":0.10858,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10336.0,"raw_peak_contact_force":0.61048,"subtask_id":"lift_object","tcp_end":[0.48688,-0.01509,0.12758],"tcp_start":[0.49071,-0.01516,0.03106],"tcp_to_object_dist_end":0.0198,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":236.0,"n_steps_budget":1000.0,"object_pos_end":[0.52204,0.0334,0.14956],"object_pos_start":[0.50456,-0.01495,0.11865],"object_to_goal_dist_end":0.19403,"object_to_goal_dist_start":0.25399,"object_z_max":0.15183,"peak_contact_force":0.0,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6001.0,"raw_peak_contact_force":0.16077,"subtask_id":"approach_goal","tcp_end":[0.50909,0.03837,0.16585],"tcp_start":[0.50738,0.03338,0.16295],"tcp_to_object_dist_end":0.02139,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":864.0,"n_steps_budget":1000.0,"object_pos_end":[0.58573,0.18011,0.21132],"object_pos_start":[0.52414,0.03849,0.15204],"object_to_goal_dist_end":0.03754,"object_to_goal_dist_start":0.18804,"object_z_max":0.21138,"peak_contact_force":0.1886,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":19180.0,"raw_peak_contact_force":0.20807,"subtask_id":"place_object","tcp_end":[0.58064,0.1802,0.23676],"tcp_start":[0.50909,0.03837,0.16585],"tcp_to_object_dist_end":0.02595,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59263,0.19212,0.01636],"object_pos_start":[0.58573,0.18011,0.21132],"object_to_goal_dist_end":0.23188,"object_to_goal_dist_start":0.03754,"object_z_max":0.21132,"peak_contact_force":0.12643,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":558.0,"raw_peak_contact_force":2.01991,"tcp_end":[0.5763,0.17881,0.25784],"tcp_start":[0.58064,0.1802,0.23676],"tcp_to_object_dist_end":0.2424,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":272.0,"n_steps_budget":600.0,"object_pos_end":[0.59263,0.19204,0.01602],"object_pos_start":[0.59263,0.19212,0.01636],"object_to_goal_dist_end":0.23221,"object_to_goal_dist_start":0.23188,"object_z_max":0.01636,"peak_contact_force":0.12263,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1088.0,"raw_peak_contact_force":0.12656,"tcp_end":[0.58381,0.18561,0.32848],"tcp_start":[0.5763,0.17881,0.25784],"tcp_to_object_dist_end":0.31265,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69853,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_goal.transport_speed":0.09934,"approach_object.approach_speed":0.18781,"descend_to_place.place_speed":0.05129,"descend_to_place.place_z_offset":0.04536,"grasp_action.grasp_duration":1.47565,"lift_object.lift_height":0.1334,"lift_object.lift_speed":0.10796,"release_object.release_duration":1.40985},"optimized_scores":{"best_composite_score":0.10871,"best_fitness_score":0.68871,"best_task_score":0.42301},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":200.0,"contact_point_centroid":[0.62551,0.16997,-0.00639],"force_p95":1.30983,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.66519,"mean_force":0.39187,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61224,0.16408,0.19324]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.50956,0.0371,-0.00148],"force_p95":0.54379,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63228,"mean_force":0.13423,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49781,0.03767,0.03213]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5353.0,"contact_point_centroid":[0.49796,0.01853,0.08394],"force_p95":0.1101,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33118,"mean_force":0.07074,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49539,0.03747,0.08157]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5822.0,"contact_point_centroid":[0.49789,0.05635,0.08104],"force_p95":0.10713,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32984,"mean_force":0.06679,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49543,0.03747,0.07916]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":370.0,"contact_point_centroid":[0.62181,0.14499,0.18402],"force_p95":0.11758,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30348,"mean_force":0.09301,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61591,0.1637,0.18208]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":648.0,"contact_point_centroid":[0.62201,0.14665,0.17813],"force_p95":0.11621,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29644,"mean_force":0.07551,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61606,0.16536,0.1776]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":855.0,"contact_point_centroid":[0.62151,0.18405,0.17783],"force_p95":0.1012,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29168,"mean_force":0.06328,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61603,0.16535,0.17755]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":495.0,"contact_point_centroid":[0.62103,0.1822,0.18263],"force_p95":0.10404,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28639,"mean_force":0.07576,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61589,0.16367,0.1821]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51258,0.03936,-0.00217],"force_p95":0.17377,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25115,"mean_force":0.13596,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.50027,0.03788,0.03192]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5416.0,"contact_point_centroid":[0.56042,0.0829,0.16404],"force_p95":0.13313,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23488,"mean_force":0.08828,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.55606,0.10166,0.16298]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6588.0,"contact_point_centroid":[0.56205,0.12114,0.16435],"force_p95":0.11248,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21051,"mean_force":0.07575,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.557,0.10267,0.16325]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3764.0,"contact_point_centroid":[0.50032,0.01859,0.03367],"force_p95":0.08637,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15569,"mean_force":0.05558,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.4991,0.03779,0.03066]},{"body_a":"world","body_b":"grasp_target","contact_count":1096.0,"contact_point_centroid":[0.51251,0.03972,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12307,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50307,0.01636,0.22519]},{"body_a":"world","body_b":"grasp_target","contact_count":528.0,"contact_point_centroid":[0.62921,0.16949,-0.00195],"force_p95":0.12703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1277,"mean_force":0.11784,"phase_index":7.0,"phase_name":"retract_after_place","phase_type":"retract","tcp_position_centroid":[0.61636,0.16679,0.21308]},{"body_a":"world","body_b":"grasp_target","contact_count":1016.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50636,0.03607,0.09396]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4956.0,"contact_point_centroid":[0.49986,0.05694,0.03251],"force_p95":0.07662,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08546,"mean_force":0.04537,"phase_index":2.0,"phase_name":"grasp_action","phase_type":"grasp","tcp_position_centroid":[0.49911,0.03779,0.03067]}],"total_contact_groups":16},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62921,0.16948,0.01602],"final_tcp_position":[0.62118,0.16963,0.2264],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.66519,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":275.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1096.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.50748,0.03388,0.14817],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12239,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":254.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_to_grasp","tcp_end":[0.50747,0.03845,0.0399],"tcp_start":[0.50748,0.03388,0.14817],"tcp_to_object_dist_end":0.01482,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.03793,0.02543],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21372,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.16176,"phase_name":"grasp_action","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10520.0,"raw_peak_contact_force":0.25115,"tcp_end":[0.49907,0.03778,0.03063],"tcp_start":[0.50747,0.03845,0.0399],"tcp_to_object_dist_end":0.01434,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":361.0,"n_steps_budget":780.0,"object_pos_end":[0.51359,0.03775,0.13423],"object_pos_start":[0.51243,0.03793,0.02543],"object_to_goal_dist_end":0.17684,"object_to_goal_dist_start":0.21372,"object_z_max":0.13397,"peak_contact_force":0.10758,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11255.0,"raw_peak_contact_force":0.63228,"subtask_id":"lift_object","tcp_end":[0.49535,0.03747,0.14465],"tcp_start":[0.49907,0.03778,0.03063],"tcp_to_object_dist_end":0.02101,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":487.0,"n_steps_budget":1000.0,"object_pos_end":[0.51427,0.03787,0.1345],"object_pos_start":[0.51359,0.03775,0.13423],"object_to_goal_dist_end":0.17629,"object_to_goal_dist_start":0.17684,"object_z_max":0.15981,"peak_contact_force":0.10952,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12004.0,"raw_peak_contact_force":0.23488,"subtask_id":"approach_goal","tcp_end":[0.61511,0.16225,0.18324],"tcp_start":[0.49568,0.03763,0.14495],"tcp_to_object_dist_end":0.16738,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":37.0,"n_steps_budget":1000.0,"object_pos_end":[0.62595,0.16578,0.15801],"object_pos_start":[0.62318,0.16239,0.15986],"object_to_goal_dist_end":0.01472,"object_to_goal_dist_start":0.01849,"object_z_max":0.15986,"peak_contact_force":0.11115,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":865.0,"raw_peak_contact_force":0.30348,"subtask_id":"place_object","tcp_end":[0.61785,0.16567,0.18141],"tcp_start":[0.61511,0.16225,0.18324],"tcp_to_object_dist_end":0.02476,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62879,0.1683,0.01463],"object_pos_start":[0.62595,0.16578,0.15801],"object_to_goal_dist_end":0.13047,"object_to_goal_dist_start":0.01472,"object_z_max":0.15801,"peak_contact_force":0.09959,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1703.0,"raw_peak_contact_force":1.66519,"tcp_end":[0.6122,0.16407,0.20113],"tcp_start":[0.61785,0.16567,0.18141],"tcp_to_object_dist_end":0.18728,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":132.0,"n_steps_budget":600.0,"object_pos_end":[0.62921,0.16948,0.01602],"object_pos_start":[0.62879,0.1683,0.01463],"object_to_goal_dist_end":0.12905,"object_to_goal_dist_start":0.13047,"object_z_max":0.01654,"peak_contact_force":0.12267,"phase_name":"retract_after_place","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":528.0,"raw_peak_contact_force":0.1277,"tcp_end":[0.62118,0.16963,0.2264],"tcp_start":[0.6122,0.16407,0.20113],"tcp_to_object_dist_end":0.21054,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```