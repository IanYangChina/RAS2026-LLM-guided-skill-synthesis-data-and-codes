## Search State

- **Seed**: 4
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1776 | 0.31 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.0835 | 0.22 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1679 | 0.30 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2603 | 0.32 | ✅ accepted |
| 2 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ❌ rejected |

**Proposal policy**: task_score is 0.31 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.178) — your mutation base

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
      - 0.05
      - 0.2
      default: 0.1
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
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.178
- **task_score** (E): 0.313
- **fitness_score**: 0.628  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0993 |
| descend_1 | 1.00 | 1.00 | 0.1585 |
| grasp_1 | 1.00 | 1.00 | 0.0134 |
| lift_1 | 1.00 | 1.00 | 0.1189 |
| transport_arc | 0.00 | 1.00 | 0.1423 |
| descend_to_place | 0.00 | 1.00 | 0.0913 |
| release_1 | 1.00 | 1.00 | 0.0231 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.517, 0.005, 0.206) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 14.787 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.517, 0.005, 0.206)→(0.521, 0.005, 0.048) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.048)→(0.512, 0.005, 0.038) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 41.667 | 0.143 | 0.194 |
| lift_1 | lift | 1.00 / step_budget | (0.512, 0.005, 0.038)→(0.508, 0.005, 0.157) | (0.526, 0.005, 0.026)→(0.525, 0.005, 0.139) | 0.249→0.213 | 1.00 / 21.667 | 0.135 | 0.514 |
| transport_arc | approach | 0.00 / step_budget | (0.508, 0.005, 0.157)→(0.539, 0.017, 0.130) | (0.525, 0.005, 0.139)→(0.583, 0.065, 0.012) | 0.213→0.207 | 1.00 / 11.333 | 988.864 | 1368.203 |
| descend_to_place | descend | 0.00 / step_budget | (0.539, 0.017, 0.130)→(0.573, 0.082, 0.178) | (0.583, 0.065, 0.012)→(0.583, 0.079, 0.019) | 0.207→0.194 | 1.00 / 9.000 | 55983.993 | 368.963 |
| release_1 | release | 1.00 / step_budget | (0.573, 0.082, 0.178)→(0.570, 0.081, 0.201) | (0.583, 0.079, 0.019)→(0.582, 0.079, 0.019) | 0.194→0.193 | 1.00 / 4.000 | 0.123 | 43.720 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.504
- phase_score: 0.258
- phase_breakdown.transport_arc_score: 0.023
- phase_breakdown.descend_1_score: 0.863
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.125
- phase_breakdown.release_1_score: 0.016
- grasp_place_fitness: 0.724

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.724
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.504
- **Median Q (composite search score)**: 0.165
- **K-run variance**: 0.0056
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at lower bound**: transport_arc.transport_speed
- **Final σ (mean)**: 0.386


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":39.0,"average_failure_rate":0.22941,"average_mean_iterations":50.82941,"average_solve_count":170.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.22803,"descend_1.grasp_z_offset":0.00641,"descend_to_place.place_z_offset":0.03593,"lift_1.lift_height":0.12096,"transport_arc.arc_height":0.10908,"transport_arc.transport_speed":0.40612},"optimized_scores":{"best_composite_score":0.16511,"best_fitness_score":0.61511,"best_task_score":0.29452},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":648.0,"contact_point_centroid":[0.69162,-0.01036,-0.00063],"force_p95":250.44693,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1723.17909,"mean_force":241.60081,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.59383,-0.00961,0.01838]},{"body_a":"world","body_b":"hand","contact_count":10.0,"contact_point_centroid":[0.69686,-0.0215,-4e-05],"force_p95":143.61346,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":150.81851,"mean_force":69.25612,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59738,-0.02779,0.04113]},{"body_a":"world","body_b":"left_finger","contact_count":1569.0,"contact_point_centroid":[0.60758,0.01127,-0.00876],"force_p95":9.69119,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":51.95169,"mean_force":5.03442,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.59487,0.02059,-0.00615]},{"body_a":"world","body_b":"right_finger","contact_count":1236.0,"contact_point_centroid":[0.58324,0.03671,-0.00707],"force_p95":9.97358,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":35.83805,"mean_force":5.35487,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.59573,0.02394,-0.00954]},{"body_a":"grasp_target","body_b":"hand","contact_count":485.0,"contact_point_centroid":[0.64791,0.04986,0.04107],"force_p95":1.15222,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.21414,"mean_force":0.45138,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5934,-0.004,0.01396]},{"body_a":"world","body_b":"grasp_target","contact_count":2264.0,"contact_point_centroid":[0.63451,0.07392,-0.0044],"force_p95":0.68195,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.52979,"mean_force":0.27972,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5944,-0.00831,0.01874]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":494.0,"contact_point_centroid":[0.56653,0.01047,0.13319],"force_p95":0.43883,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.36385,"mean_force":0.23492,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5572,0.02757,0.13379]},{"body_a":"grasp_target","body_b":"link7","contact_count":128.0,"contact_point_centroid":[0.66133,0.07686,0.05085],"force_p95":0.8823,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.4154,"mean_force":0.36737,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.59709,-0.02555,0.03637]},{"body_a":"grasp_target","body_b":"link7","contact_count":131.0,"contact_point_centroid":[0.65971,0.08979,0.04626],"force_p95":0.53951,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.89097,"mean_force":0.2693,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59915,-0.01387,0.05056]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":514.0,"contact_point_centroid":[0.56647,0.05286,0.12953],"force_p95":0.46844,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.74453,"mean_force":0.18687,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.56585,0.03327,0.1281]},{"body_a":"world","body_b":"grasp_target","contact_count":1212.0,"contact_point_centroid":[0.63336,0.08277,-0.00319],"force_p95":0.47057,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5455,"mean_force":0.18533,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60572,0.00967,0.07382]},{"body_a":"grasp_target","body_b":"hand","contact_count":134.0,"contact_point_centroid":[0.63635,0.07514,0.05398],"force_p95":0.45721,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.53784,"mean_force":0.28358,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59922,-0.01353,0.05084]},{"body_a":"world","body_b":"grasp_target","contact_count":79.0,"contact_point_centroid":[0.54147,0.00054,-0.00133],"force_p95":0.42974,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47787,"mean_force":0.10435,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52807,0.00082,0.04152]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4781.0,"contact_point_centroid":[0.52875,-0.01807,0.08726],"force_p95":0.11276,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31679,"mean_force":0.07566,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52551,0.00078,0.08504]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5008.0,"contact_point_centroid":[0.52881,0.01957,0.08541],"force_p95":0.11103,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29536,"mean_force":0.07312,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52556,0.00078,0.08345]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00103,-0.00203],"force_p95":0.13255,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15396,"mean_force":0.12549,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53055,0.00087,0.04161]}],"total_contact_groups":24},"final_pose_error":0.17927,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.63356,0.07953,0.02602],"final_tcp_position":[0.61176,0.03579,0.10095],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1723.17909,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":100.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02601],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25013,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12223,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":396.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52709,0.00071,0.26767],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.24227,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":402.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02601],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25013,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1608.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.53823,0.00101,0.05097],"tcp_start":[0.52709,0.00071,0.26767],"tcp_to_object_dist_end":0.02568,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5442,0.00075,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2505,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13077,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15396,"subtask_id":"grasp_1","tcp_end":[0.52932,0.00085,0.04017],"tcp_start":[0.53823,0.00101,0.05097],"tcp_to_object_dist_end":0.02065,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":341.0,"n_steps_budget":780.0,"object_pos_end":[0.54166,0.0008,0.12238],"object_pos_start":[0.5442,0.00075,0.02587],"object_to_goal_dist_end":0.20172,"object_to_goal_dist_start":0.2505,"object_z_max":0.12212,"peak_contact_force":0.10175,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9868.0,"raw_peak_contact_force":0.47787,"tcp_end":[0.52535,0.00078,0.14171],"tcp_start":[0.52932,0.00085,0.04017],"tcp_to_object_dist_end":0.02529,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":721.0,"n_steps_budget":1000.0,"object_pos_end":[0.63633,0.08134,0.01774],"object_pos_start":[0.54166,0.0008,0.12238],"object_to_goal_dist_end":0.18993,"object_to_goal_dist_start":0.20172,"object_z_max":0.12278,"peak_contact_force":225.19341,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8854.0,"raw_peak_contact_force":1723.17909,"subtask_id":"transport_arc","tcp_end":[0.59734,-0.02779,0.04077],"tcp_start":[0.52535,0.00078,0.14171],"tcp_to_object_dist_end":0.11815,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":356.0,"n_steps_budget":1000.0,"object_pos_end":[0.63358,0.07968,0.02602],"object_pos_start":[0.63633,0.08134,0.01774],"object_to_goal_dist_end":0.1833,"object_to_goal_dist_start":0.18993,"object_z_max":0.02618,"peak_contact_force":0.12618,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3027.0,"raw_peak_contact_force":150.81851,"subtask_id":"release_1","tcp_end":[0.61176,0.03579,0.10095],"tcp_start":[0.59734,-0.02779,0.04077],"tcp_to_object_dist_end":0.08954,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63356,0.07953,0.02602],"object_pos_start":[0.63358,0.07968,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.1833,"object_z_max":0.02602,"peak_contact_force":0.12264,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1033.0,"raw_peak_contact_force":0.12618,"subtask_id":"release_1","tcp_end":[0.60647,0.0356,0.12032],"tcp_start":[0.61176,0.03579,0.10095],"tcp_to_object_dist_end":0.1075,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.44681,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.0859,"descend_1.grasp_z_offset":0.00057,"descend_to_place.place_z_offset":0.02389,"lift_1.lift_height":0.18251,"transport_arc.arc_height":0.12729,"transport_arc.transport_speed":0.3512},"optimized_scores":{"best_composite_score":0.27449,"best_fitness_score":0.72449,"best_task_score":0.50405},"replay_outcomes":[{"contacts":{"omitted_contact_groups":12,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":87.0,"contact_point_centroid":[0.54532,0.10734,-0.00209],"force_p95":669.35096,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":976.1841,"mean_force":126.64865,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48356,0.06793,0.02211]},{"body_a":"world","body_b":"link6","contact_count":642.0,"contact_point_centroid":[0.65537,0.08196,-0.00019],"force_p95":422.41762,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":754.91874,"mean_force":286.43204,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.51705,0.10816,0.16936]},{"body_a":"world","body_b":"link6","contact_count":998.0,"contact_point_centroid":[0.65347,0.13686,-0.0003],"force_p95":474.61226,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":713.01523,"mean_force":344.56885,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61461,0.15342,0.29061]},{"body_a":"world","body_b":"link7","contact_count":155.0,"contact_point_centroid":[0.60202,0.05339,-0.00035],"force_p95":337.05332,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":402.6134,"mean_force":217.56633,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.47632,0.05555,0.01512]},{"body_a":"world","body_b":"link6","contact_count":86.0,"contact_point_centroid":[0.67689,0.14389,-0.00011],"force_p95":75.30481,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":130.91089,"mean_force":53.4515,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61902,0.16072,0.28803]},{"body_a":"world","body_b":"right_finger","contact_count":1160.0,"contact_point_centroid":[0.49689,0.06009,-0.00577],"force_p95":8.88213,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":38.75268,"mean_force":3.50878,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49409,0.04803,-0.00442]},{"body_a":"world","body_b":"left_finger","contact_count":1088.0,"contact_point_centroid":[0.49628,0.03549,-0.00605],"force_p95":8.89302,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":38.41553,"mean_force":3.51588,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49451,0.04787,-0.00516]},{"body_a":"grasp_target","body_b":"link7","contact_count":540.0,"contact_point_centroid":[0.60518,0.06822,0.01791],"force_p95":1.92246,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.91231,"mean_force":0.88726,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46174,0.07514,0.04734]},{"body_a":"grasp_target","body_b":"hand","contact_count":436.0,"contact_point_centroid":[0.56942,0.05424,0.02679],"force_p95":0.86426,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.65577,"mean_force":0.42232,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46275,0.06756,0.03979]},{"body_a":"world","body_b":"grasp_target","contact_count":3141.0,"contact_point_centroid":[0.58677,0.08131,-0.00607],"force_p95":1.0302,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24035,"mean_force":0.42723,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50451,0.09596,0.12701]},{"body_a":"grasp_target","body_b":"link6","contact_count":737.0,"contact_point_centroid":[0.60692,0.08491,0.01665],"force_p95":1.36872,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.1633,"mean_force":0.62842,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5156,0.10574,0.16434]},{"body_a":"grasp_target","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.61042,0.12561,0.0181],"force_p95":0.54085,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.90284,"mean_force":0.34689,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6146,0.1534,0.29062]},{"body_a":"world","body_b":"grasp_target","contact_count":3013.0,"contact_point_centroid":[0.58114,0.13815,-0.00444],"force_p95":0.55261,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.94106,"mean_force":0.2763,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61459,0.15336,0.29063]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":432.0,"contact_point_centroid":[0.55313,0.05592,0.18192],"force_p95":0.4951,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.67246,"mean_force":0.23488,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54754,0.03828,0.18609]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":366.0,"contact_point_centroid":[0.54507,0.01724,0.19013],"force_p95":0.49296,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.60198,"mean_force":0.25503,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54026,0.03621,0.1946]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.5276,0.02839,-0.00147],"force_p95":0.51612,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5467,"mean_force":0.1176,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51462,0.02891,0.03674]}],"total_contact_groups":28},"final_pose_error":0.15769,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5724,0.14337,0.01605],"final_tcp_position":[0.61905,0.16108,0.28771],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":328.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1308.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52326,0.02662,0.13378],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10809,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":167.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":668.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52475,0.02956,0.04558],"tcp_start":[0.52326,0.02662,0.13378],"tcp_to_object_dist_end":0.02043,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53044,0.02924,0.02547],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18488,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15939,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10904.0,"raw_peak_contact_force":0.24092,"subtask_id":"grasp_1","tcp_end":[0.51594,0.029,0.03527],"tcp_start":[0.52475,0.02956,0.04558],"tcp_to_object_dist_end":0.01751,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":534.0,"n_steps_budget":1000.0,"object_pos_end":[0.52983,0.02885,0.17943],"object_pos_start":[0.53044,0.02924,0.02547],"object_to_goal_dist_end":0.18069,"object_to_goal_dist_start":0.18488,"object_z_max":0.1792,"peak_contact_force":0.19495,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14584.0,"raw_peak_contact_force":0.5467,"tcp_end":[0.51255,0.02877,0.1982],"tcp_start":[0.51594,0.029,0.03527],"tcp_to_object_dist_end":0.02552,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57473,0.13765,0.01059],"object_pos_start":[0.52983,0.02885,0.17943],"object_to_goal_dist_end":0.10908,"object_to_goal_dist_start":0.18069,"object_z_max":0.18004,"peak_contact_force":1366.84211,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11768.0,"raw_peak_contact_force":976.1841,"subtask_id":"transport_arc","tcp_end":[0.61177,0.14421,0.29363],"tcp_start":[0.51255,0.02877,0.1982],"tcp_to_object_dist_end":0.28552,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5753,0.14097,0.01384],"object_pos_start":[0.57473,0.13765,0.01059],"object_to_goal_dist_end":0.10481,"object_to_goal_dist_start":0.10908,"object_z_max":0.01424,"peak_contact_force":167951.73011,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9276.0,"raw_peak_contact_force":713.01523,"subtask_id":"release_1","tcp_end":[0.61905,0.16108,0.28771],"tcp_start":[0.61177,0.14421,0.29363],"tcp_to_object_dist_end":0.27807,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5724,0.14337,0.01605],"object_pos_start":[0.5753,0.14097,0.01384],"object_to_goal_dist_end":0.10276,"object_to_goal_dist_start":0.10481,"object_z_max":0.01605,"peak_contact_force":0.12432,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1225.0,"raw_peak_contact_force":130.91089,"subtask_id":"release_1","tcp_end":[0.61917,0.16091,0.31347],"tcp_start":[0.61905,0.16108,0.28771],"tcp_to_object_dist_end":0.30159,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":38.0,"average_failure_rate":0.20879,"average_mean_iterations":45.35165,"average_solve_count":182.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16842,"descend_1.grasp_z_offset":0.00187,"descend_to_place.place_z_offset":0.01823,"lift_1.lift_height":0.11152,"transport_arc.arc_height":0.10375,"transport_arc.transport_speed":0.10001},"optimized_scores":{"best_composite_score":0.09316,"best_fitness_score":0.54316,"best_task_score":0.1416},"replay_outcomes":[{"contacts":{"omitted_contact_groups":13,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":515.0,"contact_point_centroid":[0.5846,-0.11914,-0.0007],"force_p95":342.61489,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1405.24722,"mean_force":193.96614,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52396,-0.04439,-0.00353]},{"body_a":"world","body_b":"link7","contact_count":321.0,"contact_point_centroid":[0.55856,-0.07952,-8e-05],"force_p95":289.38619,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":403.80872,"mean_force":128.19713,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.4243,-0.06606,0.04236]},{"body_a":"world","body_b":"link6","contact_count":248.0,"contact_point_centroid":[0.62546,-0.00685,-0.00015],"force_p95":203.32313,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":282.29036,"mean_force":150.32632,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.41349,-0.06521,0.05076]},{"body_a":"world","body_b":"link6","contact_count":8.0,"contact_point_centroid":[0.61658,-0.00364,-0.00013],"force_p95":240.6263,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":243.05438,"mean_force":213.81431,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.40746,-0.06621,0.0573]},{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54894,-0.104,-5e-05],"force_p95":39.28092,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":43.64547,"mean_force":14.54849,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.40743,-0.06647,0.05695]},{"body_a":"world","body_b":"right_finger","contact_count":5145.0,"contact_point_centroid":[0.52489,-0.02151,-0.00594],"force_p95":7.13459,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":34.55301,"mean_force":3.89644,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52733,-0.04284,-0.0043]},{"body_a":"world","body_b":"left_finger","contact_count":6086.0,"contact_point_centroid":[0.53076,-0.06394,-0.00583],"force_p95":7.44935,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":31.43317,"mean_force":3.85331,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52412,-0.04446,-0.00324]},{"body_a":"world","body_b":"grasp_target","contact_count":3505.0,"contact_point_centroid":[0.56786,-0.02333,-0.00731],"force_p95":0.9478,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.79414,"mean_force":0.48842,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48385,-0.05279,0.01619]},{"body_a":"grasp_target","body_b":"hand","contact_count":934.0,"contact_point_centroid":[0.56244,-0.03447,0.0245],"force_p95":1.37457,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.98388,"mean_force":0.92263,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.483,-0.05324,0.01539]},{"body_a":"grasp_target","body_b":"link7","contact_count":494.0,"contact_point_centroid":[0.56896,-0.02241,0.0214],"force_p95":1.01795,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.89314,"mean_force":0.73314,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.43963,-0.06444,0.0342]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":823.0,"contact_point_centroid":[0.54881,-0.03902,0.07666],"force_p95":0.56361,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.44183,"mean_force":0.21385,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54044,-0.02081,0.07539]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":889.0,"contact_point_centroid":[0.54463,-0.00083,0.06764],"force_p95":0.51785,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.99177,"mean_force":0.18948,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5391,-0.02118,0.06631]},{"body_a":"grasp_target","body_b":"link6","contact_count":247.0,"contact_point_centroid":[0.56994,-0.02491,0.00994],"force_p95":0.31614,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.55291,"mean_force":0.22928,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.41339,-0.06524,0.05086]},{"body_a":"grasp_target","body_b":"link7","contact_count":243.0,"contact_point_centroid":[0.54138,-0.02367,0.03066],"force_p95":1.06047,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.38085,"mean_force":0.59542,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.42514,-0.03786,0.07688]},{"body_a":"grasp_target","body_b":"hand","contact_count":213.0,"contact_point_centroid":[0.52457,-0.03116,0.03782],"force_p95":0.60087,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.8626,"mean_force":0.38033,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.42278,-0.04129,0.07424]},{"body_a":"world","body_b":"grasp_target","contact_count":1584.0,"contact_point_centroid":[0.54237,-2e-05,-0.00387],"force_p95":0.69885,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.79952,"mean_force":0.27231,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.44774,-0.00662,0.10178]}],"total_contact_groups":29},"final_pose_error":0.20913,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.53873,0.01488,0.01602],"final_tcp_position":[0.48856,0.04814,0.14528],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1405.24722,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":160.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":44.11699,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":636.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50046,-0.01186,0.21751],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19156,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":321.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1284.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.49954,-0.01512,0.0473],"tcp_start":[0.50046,-0.01186,0.21751],"tcp_to_object_dist_end":0.02172,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50373,-0.01498,0.02578],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31198,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13833,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11320.0,"raw_peak_contact_force":0.18826,"subtask_id":"grasp_1","tcp_end":[0.49103,-0.01503,0.03794],"tcp_start":[0.49954,-0.01512,0.0473],"tcp_to_object_dist_end":0.01758,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":291.0,"n_steps_budget":720.0,"object_pos_end":[0.50359,-0.01491,0.11475],"object_pos_start":[0.50373,-0.01498,0.02578],"object_to_goal_dist_end":0.25628,"object_to_goal_dist_start":0.31198,"object_z_max":0.11449,"peak_contact_force":0.10776,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10211.0,"raw_peak_contact_force":0.51851,"tcp_end":[0.48721,-0.01497,0.13003],"tcp_start":[0.49103,-0.01503,0.03794],"tcp_to_object_dist_end":0.0224,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":13.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53895,-0.02419,0.00869],"object_pos_start":[0.50359,-0.01491,0.11475],"object_to_goal_dist_end":0.32313,"object_to_goal_dist_start":0.25628,"object_z_max":0.11522,"peak_contact_force":1374.55679,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20235.0,"raw_peak_contact_force":1405.24722,"subtask_id":"transport_arc","tcp_end":[0.40747,-0.06654,0.05687],"tcp_start":[0.48721,-0.01497,0.13003],"tcp_to_object_dist_end":0.14629,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":507.0,"n_steps_budget":1000.0,"object_pos_end":[0.53873,0.01488,0.01602],"object_pos_start":[0.53895,-0.02419,0.00869],"object_to_goal_dist_end":0.29321,"object_to_goal_dist_start":0.32313,"object_z_max":0.02036,"peak_contact_force":0.12272,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4313.0,"raw_peak_contact_force":243.05438,"subtask_id":"release_1","tcp_end":[0.48856,0.04814,0.14528],"tcp_start":[0.40747,-0.06654,0.05687],"tcp_to_object_dist_end":0.14258,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53873,0.01488,0.01602],"object_pos_start":[0.53873,0.01488,0.01602],"object_to_goal_dist_end":0.29321,"object_to_goal_dist_start":0.29321,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12272,"subtask_id":"release_1","tcp_end":[0.48429,0.04776,0.16837],"tcp_start":[0.48856,0.04814,0.14528],"tcp_to_object_dist_end":0.16509,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```