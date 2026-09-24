## Search State

- **Seed**: 4
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | impedance_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.0040 | 0.21 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.0589 | 0.27 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1032 | 0.20 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1431 | 0.34 | ✅ accepted |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1776 | 0.31 | ✅ accepted |

**Proposal policy**: task_score is 0.21 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

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
- Frozen realised-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`
- Frozen object start: [0.5443056105572368, 0.0011327552814361583, 0.03]
- Frozen task target: [0.6476243705707704, 0.15808360238956023, 0.19110337479925443]
- Goal object position: (0.6476243705707704, 0.15808360238956023, 0.19110337479925443)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6476243705707704, 0.15808360238956023, 0.19110337479925443)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5443056105572368, 0.0011327552814361583, 0.03)
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
  frozen_object_start: [0.5443, 0.0011, 0.03]
  frozen_task_target: [0.6476, 0.1581, 0.1911]
  frozen_object_starts: {'grasp_target': [0.5443056105572368, 0.0011327552814361583, 0.03]}
  frozen_targets: {'place_target': [0.6476243705707704, 0.15808360238956023, 0.19110337479925443]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8

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

## Current Skill (Q=-0.004) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
phases:
- id: approach_1
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.25
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
    - 0.02
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: descend_1
- id: grasp_1
  type: grasp
  control: impedance_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
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
- id: transport_arc
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    place_z_offset:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: release_1
- id: release_1
  type: release
  control: position_control
  termination: pose_tolerance
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.004
- **task_score** (E): 0.207
- **fitness_score**: 0.576  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1146 |
| descend_1 | 1.00 | 1.00 | 0.1434 |
| grasp_1 | 1.00 | 1.00 | 0.0134 |
| lift_1 | 1.00 | 1.00 | 0.1831 |
| lift_transport_clearance | 1.00 | 1.00 | 0.2006 |
| transport_arc | 0.00 | 1.00 | 0.0000 |
| descend_to_place | 1.00 | 1.00 | 0.2955 |
| release_1 | 1.00 | 1.00 | 0.0205 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.519, 0.004, 0.190) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.519, 0.004, 0.190)→(0.521, 0.005, 0.047) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 17.166 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.047)→(0.512, 0.005, 0.036) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 41.000 | 0.141 | 0.190 |
| lift_1 | lift | 1.00 / step_budget | (0.512, 0.005, 0.036)→(0.509, 0.005, 0.219) | (0.526, 0.005, 0.026)→(0.524, 0.005, 0.197) | 0.249→0.199 | 1.00 / 12.333 | 50723.782 | 0.536 |
| lift_transport_clearance | lift | 1.00 / step_budget | (0.509, 0.005, 0.219)→(0.508, 0.005, 0.420) | (0.524, 0.005, 0.197)→(0.516, 0.025, 0.016) | 0.199→0.245 | 1.00 / 8.000 | 94251.073 | 1.936 |
| transport_arc | approach | 0.00 / guard_failure | (0.508, 0.005, 0.420)→(0.508, 0.005, 0.420) | (0.516, 0.025, 0.016)→(0.516, 0.025, 0.016) | 0.245→0.245 | 1.00 / 8.333 | 94252.896 | 0.123 |
| descend_to_place | descend | 1.00 / step_budget | (0.508, 0.005, 0.420)→(0.601, 0.161, 0.196) | (0.516, 0.025, 0.016)→(0.516, 0.025, 0.016) | 0.245→0.245 | 1.00 / 8.000 | 3249.726 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.601, 0.161, 0.196)→(0.596, 0.160, 0.216) | (0.516, 0.025, 0.016)→(0.516, 0.025, 0.016) | 0.245→0.245 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 0.000
- terminal_score: 0.306
- phase_score: 0.319
- phase_breakdown.release_1_score: 0.514
- phase_breakdown.approach_1_score: 0.038
- phase_breakdown.descend_1_score: 0.890
- phase_breakdown.transport_arc_score: 0.001
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.624

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.624
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.306
- **Median Q (composite search score)**: -0.015
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.327


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `104d9d5641b6f93313b49acc931f841aa27a6ce63eca9eff4a16c33838e2c9c3`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `9de75aa839370ff688dada9a37e29517e2f368ed4f09f6a013379103594581cf`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89189,"average_solve_count":222.0,"average_success_count":222.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14513,"descend_1.grasp_z_offset":0.00178,"descend_to_place.place_speed":0.11426,"descend_to_place.place_z_offset":0.00685,"lift_1.lift_height":0.19756,"lift_transport_clearance.lift_transport_height":0.27291,"transport_arc.arc_height":0.27934,"transport_arc.transport_speed":0.26442},"optimized_scores":{"best_composite_score":-0.01527,"best_fitness_score":0.56473,"best_task_score":0.1854},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2927.0,"contact_point_centroid":[0.5382,0.01233,-0.0024],"force_p95":0.12539,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.0288,"mean_force":0.13906,"phase_index":4.0,"phase_name":"lift_transport_clearance","phase_type":"lift","tcp_position_centroid":[0.52444,0.00074,0.35493]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.54134,0.00051,-0.00134],"force_p95":0.50481,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53796,"mean_force":0.11254,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52814,0.00082,0.03712]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7399.0,"contact_point_centroid":[0.5297,-0.01795,0.11464],"force_p95":0.12973,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32581,"mean_force":0.0824,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52563,0.00079,0.11303]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7714.0,"contact_point_centroid":[0.52971,0.01949,0.11307],"force_p95":0.12546,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30535,"mean_force":0.08013,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52566,0.00079,0.11171]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":93.0,"contact_point_centroid":[0.53185,0.01673,0.21041],"force_p95":0.21134,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27078,"mean_force":0.08357,"phase_index":4.0,"phase_name":"lift_transport_clearance","phase_type":"lift","tcp_position_centroid":[0.52559,0.00079,0.21556]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":30.0,"contact_point_centroid":[0.5331,-0.01697,0.20765],"force_p95":0.21325,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23131,"mean_force":0.15894,"phase_index":4.0,"phase_name":"lift_transport_clearance","phase_type":"lift","tcp_position_centroid":[0.52606,0.00079,0.21434]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00101,-0.00203],"force_p95":0.13246,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15465,"mean_force":0.12545,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53069,0.00087,0.03726]},{"body_a":"world","body_b":"grasp_target","contact_count":900.0,"contact_point_centroid":[0.54431,0.00113,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12317,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51567,0.00043,0.24678]},{"body_a":"world","body_b":"grasp_target","contact_count":1080.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53507,0.00094,0.11944]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.53813,0.01229,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52585,0.00073,0.46694]},{"body_a":"world","body_b":"grasp_target","contact_count":2428.0,"contact_point_centroid":[0.53813,0.01229,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58016,0.07202,0.33764]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53813,0.01229,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6319,0.14528,0.20718]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53062,-0.01835,0.03854],"force_p95":0.07626,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12042,"mean_force":0.05178,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52947,0.00085,0.03587]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53054,0.01993,0.03767],"force_p95":0.06832,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09506,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52948,0.00085,0.03587]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2923.0,"contact_point_centroid":[0.52479,0.00074,0.36501],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01642,"mean_force":0.01052,"phase_index":4.0,"phase_name":"lift_transport_clearance","phase_type":"lift","tcp_position_centroid":[0.52451,0.00074,0.36268]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2584.0,"contact_point_centroid":[0.58041,0.07169,0.34054],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.01047,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57991,0.07168,0.33825]}],"total_contact_groups":18},"final_pose_error":0.01969,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.53813,0.01229,0.01602],"final_tcp_position":[0.63608,0.146,0.20837],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273003.24362,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":226.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":900.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53357,0.00089,0.19151],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16584,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":270.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":51.25189,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1080.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53842,0.00102,0.04662],"tcp_start":[0.53357,0.00089,0.19151],"tcp_to_object_dist_end":0.02143,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54419,0.00074,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25051,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13058,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15465,"subtask_id":"grasp_1","tcp_end":[0.52944,0.00085,0.03583],"tcp_start":[0.53842,0.00102,0.04662],"tcp_to_object_dist_end":0.0178,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":592.0,"n_steps_budget":1000.0,"object_pos_end":[0.54033,0.00067,0.19066],"object_pos_start":[0.54419,0.00074,0.02587],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.25051,"object_z_max":0.19059,"peak_contact_force":0.18273,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15190.0,"raw_peak_contact_force":0.53796,"tcp_end":[0.52616,0.00079,0.21392],"tcp_start":[0.52944,0.00085,0.03583],"tcp_to_object_dist_end":0.02723,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":834.0,"n_steps_budget":1000.0,"object_pos_end":[0.53813,0.01229,0.01602],"object_pos_start":[0.54033,0.00067,0.19066],"object_to_goal_dist_end":0.25278,"object_to_goal_dist_start":0.1905,"object_z_max":0.19066,"peak_contact_force":9749.28954,"phase_name":"lift_transport_clearance","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5973.0,"raw_peak_contact_force":2.0288,"tcp_end":[0.52584,0.00073,0.46686],"tcp_start":[0.52616,0.00079,0.21392],"tcp_to_object_dist_end":0.45115,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.53813,0.01229,0.01602],"object_pos_start":[0.53813,0.01229,0.01602],"object_to_goal_dist_end":0.25278,"object_to_goal_dist_start":0.25278,"object_z_max":0.01602,"peak_contact_force":9749.27016,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_arc","tcp_end":[0.52584,0.00073,0.46703],"tcp_start":[0.52585,0.00073,0.46701],"tcp_to_object_dist_end":0.45133,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":607.0,"n_steps_budget":1000.0,"object_pos_end":[0.53813,0.01229,0.01602],"object_pos_start":[0.53813,0.01229,0.01602],"object_to_goal_dist_end":0.25278,"object_to_goal_dist_start":0.25278,"object_z_max":0.01602,"peak_contact_force":9748.93229,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5012.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.63608,0.146,0.20837],"tcp_start":[0.52584,0.00073,0.46703],"tcp_to_object_dist_end":0.25391,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53813,0.01229,0.01602],"object_pos_start":[0.53813,0.01229,0.01602],"object_to_goal_dist_end":0.25278,"object_to_goal_dist_start":0.25278,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.63056,0.14483,0.22651],"tcp_start":[0.63608,0.146,0.20837],"tcp_to_object_dist_end":0.26536,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `349f925163f8e9284ad51ad55d38356f2e3c8deb4dc54e8ff12260e5f6d4b0f8`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.08466,"average_solve_count":189.0,"average_success_count":189.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14642,"descend_1.grasp_z_offset":0.00292,"descend_to_place.place_speed":0.17586,"descend_to_place.place_z_offset":-0.00741,"lift_1.lift_height":0.18849,"lift_transport_clearance.lift_transport_height":0.21146,"transport_arc.arc_height":0.3342,"transport_arc.transport_speed":0.22806},"optimized_scores":{"best_composite_score":0.04397,"best_fitness_score":0.62397,"best_task_score":0.30624},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1774.0,"contact_point_centroid":[0.52319,0.04856,-0.00268],"force_p95":0.27442,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.99753,"mean_force":0.15537,"phase_index":4.0,"phase_name":"lift_transport_clearance","phase_type":"lift","tcp_position_centroid":[0.511,0.02869,0.32992]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.5276,0.02847,-0.00147],"force_p95":0.48915,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5175,"mean_force":0.1107,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51504,0.02898,0.03911]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7527.0,"contact_point_centroid":[0.51641,0.01005,0.11591],"force_p95":0.11223,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31781,"mean_force":0.07624,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51263,0.02883,0.11398]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7699.0,"contact_point_centroid":[0.51625,0.04764,0.11149],"force_p95":0.11358,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31421,"mean_force":0.07542,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51265,0.02883,0.10971]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":657.0,"contact_point_centroid":[0.51723,0.04709,0.21335],"force_p95":0.19856,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29759,"mean_force":0.12388,"phase_index":4.0,"phase_name":"lift_transport_clearance","phase_type":"lift","tcp_position_centroid":[0.51145,0.02874,0.21705]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":635.0,"contact_point_centroid":[0.5175,0.01061,0.21326],"force_p95":0.2105,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28784,"mean_force":0.12629,"phase_index":4.0,"phase_name":"lift_transport_clearance","phase_type":"lift","tcp_position_centroid":[0.51151,0.02875,0.21642]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03056,-0.00215],"force_p95":0.16563,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23515,"mean_force":0.13393,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51758,0.02916,0.039]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4073.0,"contact_point_centroid":[0.51729,0.00987,0.04042],"force_p95":0.08154,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15564,"mean_force":0.0519,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51639,0.02908,0.03767]},{"body_a":"world","body_b":"grasp_target","contact_count":880.0,"contact_point_centroid":[0.5305,0.03079,-0.00185],"force_p95":0.1371,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12318,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51015,0.01192,0.24779]},{"body_a":"world","body_b":"grasp_target","contact_count":1088.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52273,0.02724,0.12096]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.52322,0.04858,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.51182,0.02873,0.39825]},{"body_a":"world","body_b":"grasp_target","contact_count":2376.0,"contact_point_centroid":[0.52322,0.04858,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55094,0.09694,0.25544]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52322,0.04858,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58613,0.16595,0.11329]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5021.0,"contact_point_centroid":[0.51723,0.04825,0.03947],"force_p95":0.07451,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07798,"mean_force":0.04447,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5164,0.02908,0.03767]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1724.0,"contact_point_centroid":[0.51145,0.02871,0.33838],"force_p95":0.01147,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01638,"mean_force":0.01056,"phase_index":4.0,"phase_name":"lift_transport_clearance","phase_type":"lift","tcp_position_centroid":[0.51107,0.02869,0.33607]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2525.0,"contact_point_centroid":[0.55123,0.09675,0.25813],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01291,"mean_force":0.01048,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55083,0.09674,0.25585]}],"total_contact_groups":18},"final_pose_error":0.0196,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.52322,0.04858,0.01602],"final_tcp_position":[0.59163,0.1672,0.11319],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273009.29394,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":221.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":880.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52215,0.02499,0.19316],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16745,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":272.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1088.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52515,0.02963,0.04796],"tcp_start":[0.52215,0.02499,0.19316],"tcp_to_object_dist_end":0.02261,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53044,0.02935,0.02549],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18479,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15771,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10894.0,"raw_peak_contact_force":0.23515,"subtask_id":"grasp_1","tcp_end":[0.51636,0.02908,0.03763],"tcp_start":[0.52515,0.02963,0.04796],"tcp_to_object_dist_end":0.0186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":551.0,"n_steps_budget":1000.0,"object_pos_end":[0.52957,0.02921,0.18579],"object_pos_start":[0.53044,0.02935,0.02549],"object_to_goal_dist_end":0.18311,"object_to_goal_dist_start":0.18479,"object_z_max":0.18555,"peak_contact_force":0.16962,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15306.0,"raw_peak_contact_force":0.5175,"tcp_end":[0.51305,0.02885,0.20643],"tcp_start":[0.51636,0.02908,0.03763],"tcp_to_object_dist_end":0.02644,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":628.0,"n_steps_budget":1000.0,"object_pos_end":[0.52322,0.04858,0.01602],"object_pos_start":[0.52957,0.02921,0.18579],"object_to_goal_dist_end":0.17751,"object_to_goal_dist_start":0.18311,"object_z_max":0.20519,"peak_contact_force":273003.80717,"phase_name":"lift_transport_clearance","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4790.0,"raw_peak_contact_force":1.99753,"tcp_end":[0.51181,0.02873,0.39816],"tcp_start":[0.51305,0.02885,0.20643],"tcp_to_object_dist_end":0.38283,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.52322,0.04858,0.01602],"object_pos_start":[0.52322,0.04858,0.01602],"object_to_goal_dist_end":0.17751,"object_to_goal_dist_start":0.17751,"object_z_max":0.01602,"peak_contact_force":273009.29394,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_arc","tcp_end":[0.51182,0.02873,0.39835],"tcp_start":[0.51182,0.02873,0.39833],"tcp_to_object_dist_end":0.38301,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":594.0,"n_steps_budget":1000.0,"object_pos_end":[0.52322,0.04858,0.01602],"object_pos_start":[0.52322,0.04858,0.01602],"object_to_goal_dist_end":0.17751,"object_to_goal_dist_start":0.17751,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4901.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.59163,0.1672,0.11319],"tcp_start":[0.51182,0.02873,0.39835],"tcp_to_object_dist_end":0.16791,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52322,0.04858,0.01602],"object_pos_start":[0.52322,0.04858,0.01602],"object_to_goal_dist_end":0.17751,"object_to_goal_dist_start":0.17751,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.58427,0.16532,0.13321],"tcp_start":[0.59163,0.1672,0.11319],"tcp_to_object_dist_end":0.17632,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a1798e4fdcacfe8740623adfe3f78d2bc74e0d14c8233e64f02c40cf2a534ecc`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8806,"average_solve_count":201.0,"average_success_count":201.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13556,"descend_1.grasp_z_offset":2e-05,"descend_to_place.place_speed":0.10094,"descend_to_place.place_z_offset":0.01579,"lift_1.lift_height":0.22191,"lift_transport_clearance.lift_transport_height":0.17696,"transport_arc.arc_height":0.29326,"transport_arc.transport_speed":0.18166},"optimized_scores":{"best_composite_score":-0.04072,"best_fitness_score":0.53928,"best_task_score":0.12987},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1516.0,"contact_point_centroid":[0.48754,0.01446,-0.0028],"force_p95":0.34818,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.78258,"mean_force":0.15871,"phase_index":4.0,"phase_name":"lift_transport_clearance","phase_type":"lift","tcp_position_centroid":[0.48598,-0.015,0.33514]},{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.50104,-0.01471,-0.00137],"force_p95":0.51763,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55201,"mean_force":0.12376,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48968,-0.01507,0.03711]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":132.0,"contact_point_centroid":[0.49358,0.00087,0.23589],"force_p95":0.28957,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3618,"mean_force":0.18755,"phase_index":4.0,"phase_name":"lift_transport_clearance","phase_type":"lift","tcp_position_centroid":[0.48717,-0.01501,0.24158]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8541.0,"contact_point_centroid":[0.49072,0.00382,0.12439],"force_p95":0.12441,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32034,"mean_force":0.07733,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48736,-0.01502,0.12262]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9052.0,"contact_point_centroid":[0.49069,-0.03379,0.1208],"force_p95":0.12308,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29669,"mean_force":0.07383,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48736,-0.01502,0.11943]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":46.0,"contact_point_centroid":[0.49445,-0.0327,0.23255],"force_p95":0.2086,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20924,"mean_force":0.14541,"phase_index":4.0,"phase_name":"lift_transport_clearance","phase_type":"lift","tcp_position_centroid":[0.48768,-0.01502,0.23895]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01552,-0.00205],"force_p95":0.13932,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18078,"mean_force":0.12713,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49207,-0.01509,0.03701]},{"body_a":"world","body_b":"grasp_target","contact_count":880.0,"contact_point_centroid":[0.50382,-0.01567,-0.00185],"force_p95":0.1371,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12318,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49969,-0.00604,0.24416]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4103.0,"contact_point_centroid":[0.49136,0.00413,0.03858],"force_p95":0.0775,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12795,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49093,-0.01508,0.03581]},{"body_a":"world","body_b":"grasp_target","contact_count":1060.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49897,-0.01392,0.11535]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.48741,0.0143,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48664,-0.01502,0.39543]},{"body_a":"world","body_b":"grasp_target","contact_count":2152.0,"contact_point_centroid":[0.48741,0.0143,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.53086,0.07684,0.32969]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.48741,0.0143,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57358,0.16999,0.26758]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4908.0,"contact_point_centroid":[0.49144,-0.03417,0.03766],"force_p95":0.06963,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0884,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49093,-0.01508,0.03582]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1464.0,"contact_point_centroid":[0.48639,-0.015,0.34206],"force_p95":0.01164,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01655,"mean_force":0.01077,"phase_index":4.0,"phase_name":"lift_transport_clearance","phase_type":"lift","tcp_position_centroid":[0.48601,-0.015,0.33974]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2293.0,"contact_point_centroid":[0.5313,0.07695,0.33188],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01273,"mean_force":0.01046,"phase_index":6.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.5309,0.07694,0.32962]}],"total_contact_groups":18},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.48741,0.0143,0.01602],"final_tcp_position":[0.57672,0.17055,0.26682],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":152170.99322,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":221.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":880.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50034,-0.01272,0.18493],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15898,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":265.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1060.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49943,-0.01517,0.04511],"tcp_start":[0.50034,-0.01272,0.18493],"tcp_to_object_dist_end":0.0196,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50371,-0.01503,0.0258],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.312,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.136,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10811.0,"raw_peak_contact_force":0.18078,"subtask_id":"grasp_1","tcp_end":[0.4909,-0.01508,0.03578],"tcp_start":[0.49943,-0.01517,0.04511],"tcp_to_object_dist_end":0.01624,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":638.0,"n_steps_budget":1000.0,"object_pos_end":[0.50255,-0.01528,0.21563],"object_pos_start":[0.50371,-0.01503,0.0258],"object_to_goal_dist_end":0.22197,"object_to_goal_dist_start":0.312,"object_z_max":0.21544,"peak_contact_force":152170.99322,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17667.0,"raw_peak_contact_force":0.55201,"tcp_end":[0.48795,-0.01502,0.23808],"tcp_start":[0.4909,-0.01508,0.03578],"tcp_to_object_dist_end":0.02678,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":500.0,"n_steps_budget":1000.0,"object_pos_end":[0.48741,0.0143,0.01602],"object_pos_start":[0.50255,-0.01528,0.21563],"object_to_goal_dist_end":0.30619,"object_to_goal_dist_start":0.22197,"object_z_max":0.21571,"peak_contact_force":0.12263,"phase_name":"lift_transport_clearance","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3158.0,"raw_peak_contact_force":1.78258,"tcp_end":[0.48663,-0.01502,0.39533],"tcp_start":[0.48795,-0.01502,0.23808],"tcp_to_object_dist_end":0.38044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.48741,0.0143,0.01602],"object_pos_start":[0.48741,0.0143,0.01602],"object_to_goal_dist_end":0.30619,"object_to_goal_dist_start":0.30619,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_arc","tcp_end":[0.48664,-0.01502,0.39553],"tcp_start":[0.48664,-0.01502,0.39551],"tcp_to_object_dist_end":0.38065,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":538.0,"n_steps_budget":1000.0,"object_pos_end":[0.48741,0.0143,0.01602],"object_pos_start":[0.48741,0.0143,0.01602],"object_to_goal_dist_end":0.30619,"object_to_goal_dist_start":0.30619,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4445.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57672,0.17055,0.26682],"tcp_start":[0.48664,-0.01502,0.39553],"tcp_to_object_dist_end":0.30869,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48741,0.0143,0.01602],"object_pos_start":[0.48741,0.0143,0.01602],"object_to_goal_dist_end":0.30619,"object_to_goal_dist_start":0.30619,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57263,0.16955,0.28749],"tcp_start":[0.57672,0.17055,0.26682],"tcp_to_object_dist_end":0.32413,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```