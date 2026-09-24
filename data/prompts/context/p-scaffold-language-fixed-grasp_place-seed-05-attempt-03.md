## Search State

- **Seed**: 5
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4745 | 0.95 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1790 | 0.41 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1731 | 0.41 | ✅ accepted |
| 0 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.2807 | 0.21 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.95). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach_1 | object | (0.00, 0.00, 0.00) | distance | approach_height |
| descend_1 | object | (0.00, 0.00, 0.02) | distance | grasp_z_offset |
| grasp_1 | object | (0.00, 0.00, 0.02) | contact | — |
| transport_arc | goal | (0.00, 0.00, 0.00) | distance | — |
| release_1 | goal | (0.00, 0.00, 0.00) | distance | — |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.474) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_1
  anchor: object
- id: descend_1
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.02
- id: grasp_1
  anchor: object
  metric: contact
  offset:
  - 0.0
  - 0.0
  - 0.02
- id: transport_arc
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    orientation:
      mode: none
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_1
- id: descend_1
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
    - 0.05
    orientation:
      mode: none
  parameters:
    depth:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: descend_1
- id: grasp_1
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
      mode: none
  subtask_id: grasp_1
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.2
    orientation:
      mode: none
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.35
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.3
      default: 0.12
      binds_to:
      - path: generator.speed
        mode: replace
- id: transport_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
    orientation:
      mode: none
  parameters:
    speed:
      type: scalar
      range:
      - 0.02
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
    transport_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: transport_arc
- id: descend_goal
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
    - 0.03
    orientation:
      mode: none
  parameters:
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: placement_force
    when: during_phase
    predicate: force_below
    threshold: 15.0
    on_failure: abort

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15]
  - orientation: mode=none
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.05]
  - orientation: mode=none
  - parameter_bindings:
    - depth: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.2]
  - orientation: mode=none
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15]
  - orientation: mode=none
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
    - transport_height: status=consumed; consumers=target.offset.z (replace)
- **descend_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03]
  - orientation: mode=none
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=placement_force, when=during_phase, predicate=force_below, on_failure=abort, threshold=15.0

## Design Metrics

- **Composite score**: 0.474
- **task_score** (E): 0.945
- **fitness_score**: 0.944  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.470

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1013 |
| descend_1 | 1.00 | 1.00 | 0.1707 |
| grasp_1 | 1.00 | 1.00 | 0.0129 |
| lift_1 | 0.67 | 1.00 | 0.1323 |
| transport_1 | 0.33 | 1.00 | 0.1599 |
| descend_goal | 1.00 | 1.00 | 0.1151 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.020, 0.217) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.511, 0.020, 0.217)→(0.510, 0.018, 0.047) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.510, 0.018, 0.047)→(0.502, 0.018, 0.037) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 42.333 | 0.140 | 0.169 |
| lift_1 | lift | 0.67 / step_budget | (0.502, 0.018, 0.037)→(0.498, 0.018, 0.169) | (0.516, 0.018, 0.026)→(0.509, 0.018, 0.150) | 0.236→0.192 | 1.00 / 39.667 | 0.088 | 0.561 |
| transport_1 | approach | 0.33 / step_budget | (0.498, 0.018, 0.169)→(0.563, 0.114, 0.272) | (0.509, 0.018, 0.150)→(0.568, 0.116, 0.246) | 0.192→0.122 | 1.00 / 32.333 | 0.103 | 0.224 |
| descend_goal | descend | 1.00 / step_budget | (0.563, 0.114, 0.272)→(0.599, 0.175, 0.195) | (0.568, 0.116, 0.246)→(0.596, 0.175, 0.164) | 0.122→0.020 | 1.00 / 28.333 | 0.106 | 0.241 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.371
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.265
- phase_breakdown.transport_arc_score: 0.045
- phase_breakdown.descend_1_score: 0.854
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.000
- phase_breakdown.approach_1_score: 0.107
- grasp_place_fitness: 0.973

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.973
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.501
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.379


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8806,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1042,"descend_1.depth":0.01062,"descend_goal.place_z_offset":0.03121,"lift_1.lift_height":0.10372,"lift_1.speed":0.11367,"transport_1.speed":0.07801,"transport_1.transport_height":0.18371},"optimized_scores":{"best_composite_score":0.50349,"best_fitness_score":0.97349,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":157.0,"contact_point_centroid":[0.5259,0.02968,-0.00125],"force_p95":0.35311,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62082,"mean_force":0.1042,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51437,0.02998,0.03602]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9081.0,"contact_point_centroid":[0.51256,0.04903,0.08056],"force_p95":0.08656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35011,"mean_force":0.06113,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51184,0.02982,0.07791]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11065.0,"contact_point_centroid":[0.5135,0.0109,0.07817],"force_p95":0.08018,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33106,"mean_force":0.05067,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51185,0.02982,0.07648]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17386.0,"contact_point_centroid":[0.56957,0.10898,0.15794],"force_p95":0.08641,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24302,"mean_force":0.05308,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.56592,0.12747,0.1583]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14330.0,"contact_point_centroid":[0.56501,0.14893,0.15809],"force_p95":0.10152,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2209,"mean_force":0.06444,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.56758,0.13012,0.15686]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53051,0.03082,-0.00205],"force_p95":0.13976,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16701,"mean_force":0.12686,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51733,0.03019,0.036]},{"body_a":"world","body_b":"grasp_target","contact_count":2144.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13219,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51033,0.02488,0.22289]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13827.0,"contact_point_centroid":[0.52111,0.06746,0.16012],"force_p95":0.11089,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13684,"mean_force":0.07058,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51952,0.04824,0.15885]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5299.0,"contact_point_centroid":[0.51724,0.01107,0.03657],"force_p95":0.07083,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12285,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51607,0.0301,0.03458]},{"body_a":"world","body_b":"grasp_target","contact_count":1196.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52309,0.03155,0.09267]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18067.0,"contact_point_centroid":[0.52323,0.03042,0.16029],"force_p95":0.08755,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11537,"mean_force":0.05357,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51974,0.04868,0.15972]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4170.0,"contact_point_centroid":[0.51672,0.0494,0.03737],"force_p95":0.08221,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09045,"mean_force":0.05189,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51608,0.0301,0.03458]}],"total_contact_groups":12},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59049,0.17437,0.1038],"final_tcp_position":[0.59517,0.17421,0.13296],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.62082,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":537.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2144.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52405,0.03255,0.14152],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11569,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":299.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1196.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52478,0.0307,0.04457],"tcp_start":[0.52405,0.03255,0.14152],"tcp_to_object_dist_end":0.01941,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5304,0.03056,0.0258],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18369,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.13951,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11269.0,"raw_peak_contact_force":0.16701,"subtask_id":"grasp_1","tcp_end":[0.51604,0.0301,0.03454],"tcp_start":[0.52478,0.0307,0.04457],"tcp_to_object_dist_end":0.01682,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":530.0,"n_steps_budget":600.0,"object_pos_end":[0.52487,0.03058,0.11013],"object_pos_start":[0.5304,0.03056,0.0258],"object_to_goal_dist_end":0.16669,"object_to_goal_dist_start":0.18369,"object_z_max":0.11001,"peak_contact_force":0.10498,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20303.0,"raw_peak_contact_force":0.62082,"tcp_end":[0.51191,0.02983,0.12523],"tcp_start":[0.51604,0.0301,0.03454],"tcp_to_object_dist_end":0.01991,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54061,0.07146,0.17225],"object_pos_start":[0.52487,0.03058,0.11013],"object_to_goal_dist_end":0.13894,"object_to_goal_dist_start":0.16669,"object_z_max":0.17218,"peak_contact_force":0.11716,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31894.0,"raw_peak_contact_force":0.13684,"subtask_id":"transport_arc","tcp_end":[0.53276,0.07004,0.19507],"tcp_start":[0.51191,0.02983,0.12523],"tcp_to_object_dist_end":0.02416,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":906.0,"n_steps_budget":1000.0,"object_pos_end":[0.59049,0.17437,0.1038],"object_pos_start":[0.54061,0.07146,0.17225],"object_to_goal_dist_end":0.01257,"object_to_goal_dist_start":0.13894,"object_z_max":0.17227,"peak_contact_force":0.08735,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":31716.0,"raw_peak_contact_force":0.24302,"tcp_end":[0.59517,0.17421,0.13296],"tcp_start":[0.53276,0.07004,0.19507],"tcp_to_object_dist_end":0.02953,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88816,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.2986,"descend_1.depth":0.01392,"descend_goal.place_z_offset":0.0136,"lift_1.lift_height":0.33697,"lift_1.speed":0.11243,"transport_1.speed":0.20973,"transport_1.transport_height":0.06211},"optimized_scores":{"best_composite_score":0.41858,"best_fitness_score":0.88858,"best_task_score":0.83614},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.50027,-0.01554,-0.00125],"force_p95":0.26535,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50283,"mean_force":0.0877,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48887,-0.0154,0.04071]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20704.0,"contact_point_centroid":[0.48816,0.00362,0.12821],"force_p95":0.0743,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30728,"mean_force":0.05028,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48656,-0.01537,0.12649]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18103.0,"contact_point_centroid":[0.48741,-0.03456,0.1287],"force_p95":0.08131,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30039,"mean_force":0.05698,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48655,-0.01537,0.1261]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16398.0,"contact_point_centroid":[0.52075,0.03198,0.26411],"force_p95":0.08711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24976,"mean_force":0.06059,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51718,0.05076,0.26364]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6254.0,"contact_point_centroid":[0.56105,0.17017,0.27366],"force_p95":0.0935,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23106,"mean_force":0.06018,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.56639,0.15218,0.27458]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5555.0,"contact_point_centroid":[0.56988,0.13353,0.27199],"force_p95":0.11434,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22533,"mean_force":0.07317,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.56637,0.15212,0.27464]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18319.0,"contact_point_centroid":[0.51786,0.07076,0.26498],"force_p95":0.07927,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21396,"mean_force":0.05437,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51771,0.05186,0.26433]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01576,-0.00203],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14845,"mean_force":0.12515,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49169,-0.01543,0.04059]},{"body_a":"world","body_b":"grasp_target","contact_count":1060.0,"contact_point_centroid":[0.50382,-0.01567,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4992,-0.00556,0.31019]},{"body_a":"world","body_b":"grasp_target","contact_count":3292.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49886,-0.01397,0.18295]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5091.0,"contact_point_centroid":[0.49148,0.00364,0.04098],"force_p95":0.06811,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09499,"mean_force":0.04296,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49048,-0.01541,0.03929]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4146.0,"contact_point_centroid":[0.48977,-0.03466,0.04177],"force_p95":0.07887,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09268,"mean_force":0.05178,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49048,-0.01541,0.03929]}],"total_contact_groups":12},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.57582,0.18159,0.22438],"final_tcp_position":[0.58103,0.18085,0.25718],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":0.50283,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":266.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1060.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50065,-0.01251,0.31972],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.29374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":823.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3292.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49893,-0.01548,0.04845],"tcp_start":[0.50065,-0.01251,0.31972],"tcp_to_object_dist_end":0.02296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5037,-0.0158,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31245,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13212,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11037.0,"raw_peak_contact_force":0.14845,"subtask_id":"grasp_1","tcp_end":[0.49045,-0.01541,0.03925],"tcp_start":[0.49893,-0.01548,0.04845],"tcp_to_object_dist_end":0.01883,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49637,-0.01576,0.19838],"object_pos_start":[0.5037,-0.0158,0.02588],"object_to_goal_dist_end":0.22796,"object_to_goal_dist_start":0.31245,"object_z_max":0.1982,"peak_contact_force":0.07907,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38954.0,"raw_peak_contact_force":0.50283,"tcp_end":[0.48717,-0.01537,0.22104],"tcp_start":[0.49045,-0.01541,0.03925],"tcp_to_object_dist_end":0.02446,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55655,0.12548,0.26827],"object_pos_start":[0.49637,-0.01576,0.19838],"object_to_goal_dist_end":0.07189,"object_to_goal_dist_start":0.22796,"object_z_max":0.26825,"peak_contact_force":0.09382,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34717.0,"raw_peak_contact_force":0.24976,"subtask_id":"transport_arc","tcp_end":[0.55357,0.1242,0.29654],"tcp_start":[0.48717,-0.01537,0.22104],"tcp_to_object_dist_end":0.02846,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":375.0,"n_steps_budget":1000.0,"object_pos_end":[0.57582,0.18159,0.22438],"object_pos_start":[0.55655,0.12548,0.26827],"object_to_goal_dist_end":0.02684,"object_to_goal_dist_start":0.07189,"object_z_max":0.26827,"peak_contact_force":0.12583,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11809.0,"raw_peak_contact_force":0.23106,"tcp_end":[0.58103,0.18085,0.25718],"tcp_start":[0.55357,0.1242,0.29654],"tcp_to_object_dist_end":0.03322,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01471,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15258,"descend_1.depth":0.01274,"descend_goal.place_z_offset":0.04212,"lift_1.lift_height":0.13623,"lift_1.speed":0.09741,"transport_1.speed":0.29839,"transport_1.transport_height":0.20432},"optimized_scores":{"best_composite_score":0.50138,"best_fitness_score":0.97138,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.50942,0.03806,-0.00119],"force_p95":0.29748,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55911,"mean_force":0.08329,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49717,0.03844,0.03951]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13311.0,"contact_point_centroid":[0.49508,0.05745,0.10131],"force_p95":0.08429,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3371,"mean_force":0.05913,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49462,0.03824,0.09859]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16172.0,"contact_point_centroid":[0.49664,0.01932,0.09896],"force_p95":0.08013,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31338,"mean_force":0.05032,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49461,0.03824,0.0974]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19541.0,"contact_point_centroid":[0.544,0.06788,0.25028],"force_p95":0.08457,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28662,"mean_force":0.05164,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54003,0.08621,0.24956]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15019.0,"contact_point_centroid":[0.53879,0.10428,0.24905],"force_p95":0.10757,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25315,"mean_force":0.0689,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53895,0.08512,0.24762]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5509.0,"contact_point_centroid":[0.60605,0.17601,0.26319],"force_p95":0.11195,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24757,"mean_force":0.0709,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.60992,0.15736,0.26365]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7192.0,"contact_point_centroid":[0.61382,0.13946,0.25976],"force_p95":0.09626,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22446,"mean_force":0.05714,"phase_index":5.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.61029,0.15775,0.26125]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51255,0.03974,-0.00209],"force_p95":0.14968,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19168,"mean_force":0.12967,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5,0.03868,0.03902]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5047.0,"contact_point_centroid":[0.5004,0.01957,0.03915],"force_p95":0.07278,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15554,"mean_force":0.04309,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49877,0.03858,0.03767]},{"body_a":"world","body_b":"grasp_target","contact_count":1508.0,"contact_point_centroid":[0.51251,0.03972,-0.00191],"force_p95":0.13496,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5024,0.02446,0.24835]},{"body_a":"world","body_b":"grasp_target","contact_count":1768.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50613,0.03911,0.11848]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4188.0,"contact_point_centroid":[0.499,0.05787,0.04039],"force_p95":0.08512,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08744,"mean_force":0.05184,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49877,0.03858,0.03768]}],"total_contact_groups":12},"final_pose_error":0.00976,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62119,0.16998,0.16347],"final_tcp_position":[0.62132,0.16894,0.19372],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.55911,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":378.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1508.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50757,0.03914,0.1911],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16515,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":442.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1768.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50729,0.03928,0.04713],"tcp_start":[0.50757,0.03914,0.1911],"tcp_to_object_dist_end":0.02175,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51248,0.03922,0.02567],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21275,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14851,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11035.0,"raw_peak_contact_force":0.19168,"subtask_id":"grasp_1","tcp_end":[0.49874,0.03858,0.03764],"tcp_start":[0.50729,0.03928,0.04713],"tcp_to_object_dist_end":0.01823,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.50464,0.03909,0.14278],"object_pos_start":[0.51248,0.03922,0.02567],"object_to_goal_dist_end":0.18144,"object_to_goal_dist_start":0.21275,"object_z_max":0.14267,"peak_contact_force":0.08003,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29627.0,"raw_peak_contact_force":0.55911,"tcp_end":[0.49493,0.03827,0.1618],"tcp_start":[0.49874,0.03858,0.03764],"tcp_to_object_dist_end":0.02136,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.6073,0.15003,0.29848],"object_pos_start":[0.50464,0.03909,0.14278],"object_to_goal_dist_end":0.15641,"object_to_goal_dist_start":0.18144,"object_z_max":0.29842,"peak_contact_force":0.09733,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34560.0,"raw_peak_contact_force":0.28662,"subtask_id":"transport_arc","tcp_end":[0.60208,0.14834,0.32545],"tcp_start":[0.49493,0.03827,0.1618],"tcp_to_object_dist_end":0.02752,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":380.0,"n_steps_budget":1000.0,"object_pos_end":[0.62119,0.16998,0.16347],"object_pos_start":[0.6073,0.15003,0.29848],"object_to_goal_dist_end":0.01968,"object_to_goal_dist_start":0.15641,"object_z_max":0.29848,"peak_contact_force":0.10501,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12701.0,"raw_peak_contact_force":0.24757,"tcp_end":[0.62132,0.16894,0.19372],"tcp_start":[0.60208,0.14834,0.32545],"tcp_to_object_dist_end":0.03027,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```