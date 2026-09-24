## Search State

- **Seed**: 4
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1679 | 0.30 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2603 | 0.32 | ✅ accepted |
| 2 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ❌ rejected |
| 1 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ❌ rejected |
| 0 | push → align → release → insert → lift | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | admittance_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0580 | 0.20 | ✅ accepted |

**Proposal policy**: task_score is 0.30 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.168) — your mutation base

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

- **Composite score**: 0.168
- **task_score** (E): 0.299
- **fitness_score**: 0.618  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1208 |
| descend_1 | 1.00 | 1.00 | 0.1328 |
| grasp_1 | 1.00 | 1.00 | 0.0134 |
| lift_1 | 1.00 | 1.00 | 0.1134 |
| transport_to_goal | 1.00 | 1.00 | 0.2756 |
| descend_to_place | 1.00 | 1.00 | 0.1123 |
| release_1 | 1.00 | 1.00 | 0.0195 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.519, 0.006, 0.183) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 12.543 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.519, 0.006, 0.183)→(0.521, 0.005, 0.050) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 18.026 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.050)→(0.512, 0.005, 0.040) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 43.000 | 0.143 | 0.191 |
| lift_1 | lift | 1.00 / step_budget | (0.512, 0.005, 0.040)→(0.508, 0.005, 0.154) | (0.526, 0.005, 0.026)→(0.524, 0.005, 0.134) | 0.249→0.209 | 1.00 / 23.333 | 0.107 | 0.484 |
| transport_to_goal | approach | 1.00 / step_budget | (0.508, 0.005, 0.154)→(0.606, 0.167, 0.347) | (0.524, 0.005, 0.134)→(0.562, 0.088, 0.016) | 0.209→0.195 | 1.00 / 8.000 | 0.123 | 1.997 |
| descend_to_place | descend | 1.00 / step_budget | (0.606, 0.167, 0.347)→(0.609, 0.172, 0.235) | (0.562, 0.088, 0.016)→(0.562, 0.088, 0.016) | 0.195→0.195 | 1.00 / 8.333 | 94251.204 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.609, 0.172, 0.235)→(0.604, 0.170, 0.254) | (0.562, 0.088, 0.016)→(0.562, 0.088, 0.016) | 0.195→0.195 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.475
- phase_score: 0.411
- phase_breakdown.transport_arc_score: 0.255
- phase_breakdown.descend_1_score: 0.881
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.144
- phase_breakdown.release_1_score: 0.171
- grasp_place_fitness: 0.704

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.704
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.475
- **Median Q (composite search score)**: 0.143
- **K-run variance**: 0.0039
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.473


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0604,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12966,"descend_1.grasp_z_offset":0.00863,"descend_to_place.place_z_offset":0.01923,"lift_1.lift_height":0.11832,"transport_to_goal.transport_height":0.22238,"transport_to_goal.transport_speed":0.28779},"optimized_scores":{"best_composite_score":0.14259,"best_fitness_score":0.59259,"best_task_score":0.2539},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2248.0,"contact_point_centroid":[0.57411,0.07934,-0.00242],"force_p95":0.17518,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.94324,"mean_force":0.14697,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.60624,0.10639,0.3166]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.54172,0.00029,-0.00134],"force_p95":0.42738,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45362,"mean_force":0.09354,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52818,0.00083,0.04376]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2497.0,"contact_point_centroid":[0.54467,0.03877,0.17111],"force_p95":0.15382,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34663,"mean_force":0.09241,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53857,0.02045,0.17097]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4677.0,"contact_point_centroid":[0.5288,-0.01808,0.08826],"force_p95":0.11239,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31383,"mean_force":0.07497,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52567,0.00079,0.086]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2115.0,"contact_point_centroid":[0.5442,0.00159,0.17142],"force_p95":0.16668,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30138,"mean_force":0.09985,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53833,0.02013,0.17045]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4925.0,"contact_point_centroid":[0.52884,0.01959,0.08618],"force_p95":0.11088,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29155,"mean_force":0.07219,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52572,0.00079,0.08425]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00103,-0.00203],"force_p95":0.13252,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15402,"mean_force":0.12551,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5307,0.00088,0.04387]},{"body_a":"world","body_b":"grasp_target","contact_count":1008.0,"contact_point_centroid":[0.54431,0.00113,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51591,0.00043,0.23936]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53064,-0.01835,0.04515],"force_p95":0.07632,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12396,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5295,0.00086,0.04247]},{"body_a":"world","body_b":"grasp_target","contact_count":920.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53535,0.00095,0.11535]},{"body_a":"world","body_b":"grasp_target","contact_count":1088.0,"contact_point_centroid":[0.57396,0.07934,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64421,0.1544,0.31462]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57396,0.07934,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64098,0.15536,0.22811]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53056,0.01993,0.04427],"force_p95":0.06838,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0941,"mean_force":0.04469,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5295,0.00086,0.04247]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2226.0,"contact_point_centroid":[0.60895,0.10932,0.32386],"force_p95":0.01137,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01615,"mean_force":0.01061,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.60859,0.10931,0.3216]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.64359,0.15606,0.22717],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01007,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64308,0.15603,0.22478]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1162.0,"contact_point_centroid":[0.64461,0.1544,0.31737],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01266,"mean_force":0.01044,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64421,0.15439,0.31501]}],"total_contact_groups":16},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.57396,0.07934,0.01602],"final_tcp_position":[0.64469,0.15645,0.22991],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":273004.67128,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":253.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1008.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53414,0.0009,0.17651],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15084,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":230.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":53.83374,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":920.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53835,0.00102,0.05325],"tcp_start":[0.53414,0.0009,0.17651],"tcp_to_object_dist_end":0.02787,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.00076,0.02586],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2505,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13082,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15402,"subtask_id":"grasp_1","tcp_end":[0.52947,0.00085,0.04244],"tcp_start":[0.53835,0.00102,0.05325],"tcp_to_object_dist_end":0.02218,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":330.0,"n_steps_budget":750.0,"object_pos_end":[0.54132,0.00085,0.12001],"object_pos_start":[0.54421,0.00076,0.02586],"object_to_goal_dist_end":0.20267,"object_to_goal_dist_start":0.2505,"object_z_max":0.11976,"peak_contact_force":0.10666,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9680.0,"raw_peak_contact_force":0.45362,"tcp_end":[0.52551,0.00079,0.14124],"tcp_start":[0.52947,0.00085,0.04244],"tcp_to_object_dist_end":0.02647,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":889.0,"n_steps_budget":1000.0,"object_pos_end":[0.57396,0.07934,0.01602],"object_pos_start":[0.54132,0.00085,0.12001],"object_to_goal_dist_end":0.20562,"object_to_goal_dist_start":0.20267,"object_z_max":0.17656,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9086.0,"raw_peak_contact_force":1.94324,"subtask_id":"transport_arc","tcp_end":[0.64326,0.15246,0.3948],"tcp_start":[0.52551,0.00079,0.14124],"tcp_to_object_dist_end":0.39195,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":272.0,"n_steps_budget":1000.0,"object_pos_end":[0.57396,0.07934,0.01602],"object_pos_start":[0.57396,0.07934,0.01602],"object_to_goal_dist_end":0.20562,"object_to_goal_dist_start":0.20562,"object_z_max":0.01602,"peak_contact_force":273004.67128,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2250.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_arc","tcp_end":[0.64469,0.15645,0.22991],"tcp_start":[0.64326,0.15246,0.3948],"tcp_to_object_dist_end":0.23812,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57396,0.07934,0.01602],"object_pos_start":[0.57396,0.07934,0.01602],"object_to_goal_dist_end":0.20562,"object_to_goal_dist_start":0.20562,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.63979,0.15495,0.2473],"tcp_start":[0.64469,0.15645,0.22991],"tcp_to_object_dist_end":0.25207,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02941,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07833,"descend_1.grasp_z_offset":0.00714,"descend_to_place.place_z_offset":0.04921,"lift_1.lift_height":0.15917,"transport_to_goal.transport_height":0.16584,"transport_to_goal.transport_speed":0.27139},"optimized_scores":{"best_composite_score":0.25362,"best_fitness_score":0.70362,"best_task_score":0.47511},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":877.0,"contact_point_centroid":[0.57239,0.12257,-0.00323],"force_p95":0.60109,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06642,"mean_force":0.17551,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57523,0.13789,0.24204]},{"body_a":"world","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.52794,0.02825,-0.00146],"force_p95":0.43633,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46213,"mean_force":0.0983,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51467,0.02883,0.04339]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6251.0,"contact_point_centroid":[0.51584,0.00987,0.10679],"force_p95":0.11397,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30864,"mean_force":0.07642,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51226,0.02867,0.10464]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2028.0,"contact_point_centroid":[0.53284,0.07349,0.19388],"force_p95":0.14856,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3079,"mean_force":0.08823,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52661,0.0554,0.19405]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6499.0,"contact_point_centroid":[0.51573,0.04748,0.1032],"force_p95":0.11292,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30647,"mean_force":0.07484,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51229,0.02868,0.10131]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1598.0,"contact_point_centroid":[0.53038,0.03231,0.19194],"force_p95":0.17703,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29715,"mean_force":0.10275,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52417,0.05086,0.1918]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53057,0.03057,-0.00216],"force_p95":0.16647,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22898,"mean_force":0.13416,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5172,0.029,0.04324]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4076.0,"contact_point_centroid":[0.51705,0.00971,0.04465],"force_p95":0.08175,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15545,"mean_force":0.05188,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51602,0.02893,0.04191]},{"body_a":"world","body_b":"grasp_target","contact_count":1364.0,"contact_point_centroid":[0.5305,0.03079,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51068,0.01295,0.21424]},{"body_a":"world","body_b":"grasp_target","contact_count":600.0,"contact_point_centroid":[0.57231,0.12263,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59438,0.17101,0.2198]},{"body_a":"world","body_b":"grasp_target","contact_count":564.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52331,0.02806,0.08985]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57231,0.12263,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59176,0.17333,0.17563]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5037.0,"contact_point_centroid":[0.51697,0.0481,0.0437],"force_p95":0.07475,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07732,"mean_force":0.04434,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51603,0.02893,0.04192]},{"body_a":"left_finger","body_b":"right_finger","contact_count":740.0,"contact_point_centroid":[0.57936,0.14395,0.248],"force_p95":0.01342,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01535,"mean_force":0.01079,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57888,0.14393,0.24567]},{"body_a":"left_finger","body_b":"right_finger","contact_count":629.0,"contact_point_centroid":[0.59468,0.17104,0.22174],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01273,"mean_force":0.0106,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59438,0.17103,0.21962]},{"body_a":"left_finger","body_b":"right_finger","contact_count":218.0,"contact_point_centroid":[0.59471,0.17424,0.17359],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01103,"mean_force":0.01022,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59428,0.17421,0.17137]}],"total_contact_groups":16},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57231,0.12263,0.01602],"final_tcp_position":[0.59635,0.17473,0.17613],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":2.06642,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":342.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1364.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52333,0.02674,0.12637],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10069,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":141.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":564.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52471,0.02947,0.0522],"tcp_start":[0.52333,0.02674,0.12637],"tcp_to_object_dist_end":0.02685,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53047,0.02932,0.02547],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18481,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15879,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10913.0,"raw_peak_contact_force":0.22898,"subtask_id":"grasp_1","tcp_end":[0.516,0.02893,0.04188],"tcp_start":[0.52471,0.02947,0.0522],"tcp_to_object_dist_end":0.02188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":455.0,"n_steps_budget":990.0,"object_pos_end":[0.52806,0.0291,0.15851],"object_pos_start":[0.53047,0.02932,0.02547],"object_to_goal_dist_end":0.17403,"object_to_goal_dist_start":0.18481,"object_z_max":0.15825,"peak_contact_force":0.10555,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12831.0,"raw_peak_contact_force":0.46213,"tcp_end":[0.51246,0.02869,0.1814],"tcp_start":[0.516,0.02893,0.04188],"tcp_to_object_dist_end":0.0277,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":488.0,"n_steps_budget":1000.0,"object_pos_end":[0.57231,0.12263,0.01602],"object_pos_start":[0.52806,0.0291,0.15851],"object_to_goal_dist_end":0.11163,"object_to_goal_dist_start":0.17403,"object_z_max":0.17758,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5243.0,"raw_peak_contact_force":2.06642,"subtask_id":"transport_arc","tcp_end":[0.59306,0.16761,0.25979],"tcp_start":[0.51246,0.02869,0.1814],"tcp_to_object_dist_end":0.24875,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":1000.0,"object_pos_end":[0.57231,0.12263,0.01602],"object_pos_start":[0.57231,0.12263,0.01602],"object_to_goal_dist_end":0.11163,"object_to_goal_dist_start":0.11163,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1229.0,"raw_peak_contact_force":0.12264,"subtask_id":"transport_arc","tcp_end":[0.59635,0.17473,0.17613],"tcp_start":[0.59306,0.16761,0.25979],"tcp_to_object_dist_end":0.17008,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57231,0.12263,0.01602],"object_pos_start":[0.57231,0.12263,0.01602],"object_to_goal_dist_end":0.11163,"object_to_goal_dist_start":0.11163,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.59026,0.17279,0.19544],"tcp_start":[0.59635,0.17473,0.17613],"tcp_to_object_dist_end":0.18716,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.07042,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19772,"descend_1.grasp_z_offset":0.00034,"descend_to_place.place_z_offset":0.03168,"lift_1.lift_height":0.12117,"transport_to_goal.transport_height":0.15641,"transport_to_goal.transport_speed":0.27292},"optimized_scores":{"best_composite_score":0.10751,"best_fitness_score":0.55751,"best_task_score":0.16705},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2306.0,"contact_point_centroid":[0.54004,0.06106,-0.00243],"force_p95":0.15546,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.98157,"mean_force":0.14402,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55101,0.11774,0.30643]},{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.50107,-0.01481,-0.0014],"force_p95":0.513,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53705,"mean_force":0.1252,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48984,-0.01494,0.03761]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5151.0,"contact_point_centroid":[0.48921,0.00416,0.08402],"force_p95":0.10677,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30231,"mean_force":0.06614,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48746,-0.0149,0.08149]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2336.0,"contact_point_centroid":[0.5028,0.02751,0.16633],"force_p95":0.13974,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30014,"mean_force":0.08984,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49676,0.00915,0.16577]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5708.0,"contact_point_centroid":[0.48928,-0.03384,0.08267],"force_p95":0.10141,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29549,"mean_force":0.0611,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48745,-0.0149,0.08094]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2029.0,"contact_point_centroid":[0.50163,-0.0117,0.16408],"force_p95":0.16248,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25602,"mean_force":0.09917,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49572,0.00685,0.16297]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01556,-0.00206],"force_p95":0.14115,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19117,"mean_force":0.12774,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49222,-0.01497,0.03753]},{"body_a":"world","body_b":"grasp_target","contact_count":432.0,"contact_point_centroid":[0.50382,-0.01567,-0.00171],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12378,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49997,-0.00478,0.27509]},{"body_a":"world","body_b":"grasp_target","contact_count":1512.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4991,-0.01273,0.14616]},{"body_a":"world","body_b":"grasp_target","contact_count":620.0,"contact_point_centroid":[0.53994,0.06105,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58353,0.18217,0.34507]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53994,0.06105,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.582,0.1839,0.2991]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5068.0,"contact_point_centroid":[0.49096,0.00429,0.03948],"force_p95":0.06726,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09918,"mean_force":0.04293,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49108,-0.01496,0.03633]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5413.0,"contact_point_centroid":[0.49082,-0.03421,0.03897],"force_p95":0.06564,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07501,"mean_force":0.04113,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49108,-0.01496,0.03633]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2242.0,"contact_point_centroid":[0.55423,0.1235,0.3162],"force_p95":0.01141,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01532,"mean_force":0.01058,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55393,0.1235,0.31393]},{"body_a":"left_finger","body_b":"right_finger","contact_count":672.0,"contact_point_centroid":[0.58383,0.18217,0.34777],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.0103,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.58352,0.18216,0.34539]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.58406,0.18456,0.29727],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.01014,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58341,0.18454,0.29489]}],"total_contact_groups":16},"final_pose_error":0.0197,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.53994,0.06105,0.01602],"final_tcp_position":[0.58458,0.18489,0.29919],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9748.81729,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":109.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":37.38323,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":432.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50032,-0.01047,0.24657],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22064,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":378.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1512.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.49957,-0.01504,0.04565],"tcp_start":[0.50032,-0.01047,0.24657],"tcp_to_object_dist_end":0.02009,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50372,-0.01508,0.02576],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31206,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13877,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12281.0,"raw_peak_contact_force":0.19117,"subtask_id":"grasp_1","tcp_end":[0.49105,-0.01496,0.0363],"tcp_start":[0.49957,-0.01504,0.04565],"tcp_to_object_dist_end":0.01648,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":321.0,"n_steps_budget":780.0,"object_pos_end":[0.50405,-0.01479,0.12376],"object_pos_start":[0.50372,-0.01508,0.02576],"object_to_goal_dist_end":0.25146,"object_to_goal_dist_start":0.31206,"object_z_max":0.12349,"peak_contact_force":0.10829,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10933.0,"raw_peak_contact_force":0.53705,"tcp_end":[0.48727,-0.01489,0.13796],"tcp_start":[0.49105,-0.01496,0.0363],"tcp_to_object_dist_end":0.02198,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":875.0,"n_steps_budget":1000.0,"object_pos_end":[0.53994,0.06105,0.01602],"object_pos_start":[0.50405,-0.01479,0.12376],"object_to_goal_dist_end":0.26842,"object_to_goal_dist_start":0.25146,"object_z_max":0.17347,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8913.0,"raw_peak_contact_force":1.98157,"subtask_id":"transport_arc","tcp_end":[0.58249,0.17964,0.38688],"tcp_start":[0.48727,-0.01489,0.13796],"tcp_to_object_dist_end":0.39168,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":155.0,"n_steps_budget":1000.0,"object_pos_end":[0.53994,0.06105,0.01602],"object_pos_start":[0.53994,0.06105,0.01602],"object_to_goal_dist_end":0.26842,"object_to_goal_dist_start":0.26842,"object_z_max":0.01602,"peak_contact_force":9748.81729,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1292.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_arc","tcp_end":[0.58458,0.18489,0.29919],"tcp_start":[0.58249,0.17964,0.38688],"tcp_to_object_dist_end":0.31227,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53994,0.06105,0.01602],"object_pos_start":[0.53994,0.06105,0.01602],"object_to_goal_dist_end":0.26842,"object_to_goal_dist_start":0.26842,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.58127,0.18353,0.3189],"tcp_start":[0.58458,0.18489,0.29919],"tcp_to_object_dist_end":0.32931,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```