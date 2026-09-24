## Search State

- **Seed**: 4
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → descend → release | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1941 | 0.38 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | time_limit | 9 | -0.1763 | 0.20 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 7 | -0.2957 | 0.18 | ❌ rejected |
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | force_threshold_switch | position_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 4 | 0.3576 | 0.37 | ✅ accepted |

**Proposal policy**: task_score is 0.38 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.194) — your mutation base

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
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
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
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.005
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: descend_1
- id: grasp_1
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
    grasp_timeout:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: grasp_1
- id: lift_1
  type: lift
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
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
    speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: transport_arc
- id: place_1
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
    tolerance: 0.005
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: release_1
- id: release_1
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
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.01
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.005
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_timeout: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.02
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.5
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **place_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.194
- **task_score** (E): 0.377
- **fitness_score**: 0.664  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.470

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1664 |
| descend_1 | 1.00 | 1.00 | 0.0950 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 0.00 | 1.00 | 0.1194 |
| place_1 | 1.00 | 1.00 | 0.1427 |
| release_1 | 1.00 | 1.00 | 0.0212 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.005, 0.137) | (0.526, 0.005, 0.030)→(0.526, 0.005, 0.026) | 0.246→0.249 | 1.00 / 4.000 | 6.621 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.520, 0.005, 0.137)→(0.521, 0.005, 0.042) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.521, 0.005, 0.042)→(0.512, 0.005, 0.033) | (0.526, 0.005, 0.026)→(0.526, 0.005, 0.026) | 0.249→0.249 | 1.00 / 42.667 | 0.136 | 0.163 |
| lift_1 | lift | 0.00 / step_budget | (0.541, 0.065, 0.305)→(0.601, 0.159, 0.336) | (0.526, 0.005, 0.026)→(0.554, 0.066, 0.289) | 0.249→0.169 | 1.00 / 35.333 | 55983.979 | 0.756 |
| place_1 | descend | 1.00 / step_budget | (0.601, 0.159, 0.336)→(0.607, 0.172, 0.194) | (0.608, 0.161, 0.315)→(0.609, 0.174, 0.168) | 0.134→0.020 | 1.00 / 32.667 | 0.117 | 0.396 |
| release_1 | release | 1.00 / step_budget | (0.607, 0.172, 0.194)→(0.602, 0.170, 0.214) | (0.609, 0.174, 0.168)→(0.608, 0.167, 0.024) | 0.020→0.159 | 1.00 / 2.667 | 0.160 | 1.505 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.587
- phase_score: 0.317
- phase_breakdown.release_1_score: 0.344
- phase_breakdown.descend_1_score: 0.831
- phase_breakdown.transport_arc_score: 0.047
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.117
- grasp_place_fitness: 0.769

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.769
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.587
- **Median Q (composite search score)**: 0.171
- **K-run variance**: 0.0061
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.338


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32082,"average_solve_count":293.0,"average_success_count":293.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.02938,"descend_1.speed":0.08867,"grasp_1.grasp_timeout":1.51133,"lift_1.arc_height":0.1686,"lift_1.speed":0.01022,"place_1.speed":0.0595,"release_1.release_duration":1.14758},"optimized_scores":{"best_composite_score":0.17149,"best_fitness_score":0.64149,"best_task_score":0.33126},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":139.0,"contact_point_centroid":[0.6323,0.15417,-0.00906],"force_p95":1.34732,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.52447,"mean_force":0.53235,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63766,0.15477,0.20169]},{"body_a":"world","body_b":"grasp_target","contact_count":100.0,"contact_point_centroid":[0.53536,-0.00186,-0.00135],"force_p95":0.79941,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86591,"mean_force":0.43442,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52701,-0.00135,0.03342]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":28562.0,"contact_point_centroid":[0.52406,0.01379,0.23055],"force_p95":0.08591,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.49289,"mean_force":0.05683,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52269,-0.00514,0.22887]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":27204.0,"contact_point_centroid":[0.52179,-0.02635,0.23077],"force_p95":0.08751,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32967,"mean_force":0.05845,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52107,-0.0073,0.22878]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14802.0,"contact_point_centroid":[0.63444,0.16822,0.27287],"force_p95":0.06454,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30146,"mean_force":0.04274,"phase_index":4.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.63855,0.14967,0.26909]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13908.0,"contact_point_centroid":[0.64175,0.13083,0.26686],"force_p95":0.06735,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23055,"mean_force":0.04579,"phase_index":4.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.63878,0.15001,0.26511]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1277.0,"contact_point_centroid":[0.63811,0.17461,0.19245],"force_p95":0.06703,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20149,"mean_force":0.04098,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64144,0.15582,0.18823]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1458.0,"contact_point_centroid":[0.64513,0.13682,0.18951],"force_p95":0.06294,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18846,"mean_force":0.03704,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64144,0.15582,0.18823]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00115,-0.00203],"force_p95":0.1312,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15262,"mean_force":0.1253,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53155,0.00088,0.03352]},{"body_a":"world","body_b":"grasp_target","contact_count":2452.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13067,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51696,0.00047,0.21785]},{"body_a":"world","body_b":"grasp_target","contact_count":3908.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5365,0.00098,0.07912]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4149.0,"contact_point_centroid":[0.53131,0.02015,0.03442],"force_p95":0.07656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09651,"mean_force":0.05218,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53026,0.00085,0.03202]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5327.0,"contact_point_centroid":[0.53065,-0.01819,0.0345],"force_p95":0.06263,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08696,"mean_force":0.04072,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53026,0.00085,0.03202]}],"total_contact_groups":13},"final_pose_error":0.00495,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.63363,0.15311,0.02604],"final_tcp_position":[0.64318,0.15624,0.19224],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":19.61857,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":614.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":19.61857,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2452.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53687,0.00098,0.13658],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11081,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":977.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3908.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53885,0.00102,0.0421],"tcp_start":[0.53687,0.00098,0.13658],"tcp_to_object_dist_end":0.01698,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54418,0.00111,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25029,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13092,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11276.0,"raw_peak_contact_force":0.15262,"subtask_id":"grasp_1","tcp_end":[0.53023,0.00085,0.03198],"tcp_start":[0.53885,0.00102,0.0421],"tcp_to_object_dist_end":0.01523,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":1518.0,"n_steps_budget":1000.0,"object_pos_end":[0.53779,-0.00509,0.29932],"object_pos_start":[0.54418,0.00111,0.02587],"object_to_goal_dist_end":0.2245,"object_to_goal_dist_start":0.25029,"object_z_max":0.36549,"peak_contact_force":0.06807,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":55866.0,"raw_peak_contact_force":0.86591,"subtask_id":"transport_arc","tcp_end":[0.63577,0.1438,0.34849],"tcp_start":[0.52363,-0.00511,0.31198],"tcp_to_object_dist_end":0.1849,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":638.0,"n_steps_budget":1000.0,"object_pos_end":[0.64236,0.15756,0.17049],"object_pos_start":[0.63931,0.1451,0.32943],"object_to_goal_dist_end":0.02128,"object_to_goal_dist_start":0.13918,"object_z_max":0.32943,"peak_contact_force":0.06775,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":28710.0,"raw_peak_contact_force":0.30146,"subtask_id":"release_1","tcp_end":[0.64318,0.15624,0.19224],"tcp_start":[0.63577,0.1438,0.34849],"tcp_to_object_dist_end":0.02181,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63363,0.15311,0.02604],"object_pos_start":[0.64236,0.15756,0.17049],"object_to_goal_dist_end":0.16573,"object_to_goal_dist_start":0.02128,"object_z_max":0.17049,"peak_contact_force":0.15302,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2874.0,"raw_peak_contact_force":1.52447,"tcp_end":[0.63761,0.15476,0.21148],"tcp_start":[0.64318,0.15624,0.19224],"tcp_to_object_dist_end":0.18549,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50204,"average_solve_count":245.0,"average_success_count":245.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0806,"descend_1.speed":0.09606,"grasp_1.grasp_timeout":0.82741,"lift_1.arc_height":0.11251,"lift_1.speed":0.02433,"place_1.speed":0.04086,"release_1.release_duration":1.70189},"optimized_scores":{"best_composite_score":0.2989,"best_fitness_score":0.7689,"best_task_score":0.58693},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":158.0,"contact_point_centroid":[0.58763,0.17282,-0.00763],"force_p95":1.05146,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.19184,"mean_force":0.4394,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58822,0.17154,0.14756]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.52465,0.02823,-0.00144],"force_p95":0.62408,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68211,"mean_force":0.31919,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51458,0.02849,0.03408]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19124.0,"contact_point_centroid":[0.52105,0.06169,0.17778],"force_p95":0.10567,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41509,"mean_force":0.06492,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52062,0.04251,0.17547]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16005.0,"contact_point_centroid":[0.58904,0.18843,0.1795],"force_p95":0.09228,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33803,"mean_force":0.06085,"phase_index":4.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.5921,0.16961,0.17609]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":23474.0,"contact_point_centroid":[0.52345,0.02476,0.17654],"force_p95":0.08449,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30425,"mean_force":0.05257,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52114,0.04341,0.17511]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21297.0,"contact_point_centroid":[0.59678,0.15137,0.17571],"force_p95":0.07458,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22685,"mean_force":0.04636,"phase_index":4.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.59211,0.16963,0.17587]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53053,0.0308,-0.00209],"force_p95":0.14776,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19343,"mean_force":0.12921,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51794,0.0299,0.03426]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1400.0,"contact_point_centroid":[0.59812,0.15452,0.13495],"force_p95":0.06402,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15075,"mean_force":0.03769,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59259,0.17286,0.13481]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5287.0,"contact_point_centroid":[0.51769,0.01078,0.03467],"force_p95":0.06897,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13868,"mean_force":0.0411,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51667,0.02982,0.03281]},{"body_a":"world","body_b":"grasp_target","contact_count":2188.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51074,0.01381,0.21822]},{"body_a":"world","body_b":"grasp_target","contact_count":3576.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52325,0.0294,0.07916]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1053.0,"contact_point_centroid":[0.59118,0.19209,0.13884],"force_p95":0.07918,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09113,"mean_force":0.0476,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59256,0.17285,0.13476]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4191.0,"contact_point_centroid":[0.51708,0.04912,0.03559],"force_p95":0.08289,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08557,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51667,0.02982,0.03282]}],"total_contact_groups":13},"final_pose_error":0.03123,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.59244,0.17147,0.029],"final_tcp_position":[0.59436,0.17335,0.13803],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":548.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2188.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52409,0.02818,0.1371],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1113,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":894.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3576.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52514,0.03038,0.04249],"tcp_start":[0.52409,0.02818,0.1371],"tcp_to_object_dist_end":0.01732,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53043,0.03032,0.02569],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18392,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14672,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11278.0,"raw_peak_contact_force":0.19343,"subtask_id":"grasp_1","tcp_end":[0.51664,0.02982,0.03278],"tcp_start":[0.52514,0.03038,0.04249],"tcp_to_object_dist_end":0.01552,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1176.0,"n_steps_budget":1000.0,"object_pos_end":[0.57397,0.11218,0.24781],"object_pos_start":[0.53043,0.03032,0.02569],"object_to_goal_dist_end":0.15713,"object_to_goal_dist_start":0.18392,"object_z_max":0.25075,"peak_contact_force":167951.73011,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":42690.0,"raw_peak_contact_force":0.68211,"subtask_id":"transport_arc","tcp_end":[0.59007,0.16261,0.25921],"tcp_start":[0.55963,0.10921,0.26174],"tcp_to_object_dist_end":0.05416,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59675,0.17527,0.11547],"object_pos_start":[0.59834,0.16558,0.24243],"object_to_goal_dist_end":0.0094,"object_to_goal_dist_start":0.135,"object_z_max":0.24243,"peak_contact_force":0.07921,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":37302.0,"raw_peak_contact_force":0.33803,"subtask_id":"release_1","tcp_end":[0.59436,0.17335,0.13803],"tcp_start":[0.59007,0.16261,0.25921],"tcp_to_object_dist_end":0.02276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59244,0.17147,0.029],"object_pos_start":[0.59675,0.17527,0.11547],"object_to_goal_dist_end":0.07993,"object_to_goal_dist_start":0.0094,"object_z_max":0.11547,"peak_contact_force":0.2096,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2611.0,"raw_peak_contact_force":1.19184,"tcp_end":[0.58811,0.17151,0.15918],"tcp_start":[0.59436,0.17335,0.13803],"tcp_to_object_dist_end":0.13025,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.06395,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.13255,"descend_1.speed":0.07056,"grasp_1.grasp_timeout":1.60593,"lift_1.arc_height":0.08751,"lift_1.speed":0.14744,"place_1.speed":0.06307,"release_1.release_duration":0.84135},"optimized_scores":{"best_composite_score":0.1119,"best_fitness_score":0.5819,"best_task_score":0.21307},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":334.0,"contact_point_centroid":[0.59796,0.17751,-0.00573],"force_p95":1.0385,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79867,"mean_force":0.27093,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57907,0.18383,0.25967]},{"body_a":"world","body_b":"grasp_target","contact_count":71.0,"contact_point_centroid":[0.49995,-0.01599,-0.00131],"force_p95":0.64041,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71877,"mean_force":0.16513,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48892,-0.01585,0.03535]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5351.0,"contact_point_centroid":[0.58936,0.1609,0.32489],"force_p95":0.146,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.54846,"mean_force":0.10447,"phase_index":4.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.57964,0.17685,0.32815]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5607.0,"contact_point_centroid":[0.57971,0.19542,0.3281],"force_p95":0.13198,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.49596,"mean_force":0.09875,"phase_index":4.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.57956,0.17667,0.32977]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":97.0,"contact_point_centroid":[0.58499,0.20463,0.24612],"force_p95":0.23231,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43183,"mean_force":0.18408,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58269,0.18512,0.24926]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18238.0,"contact_point_centroid":[0.51136,0.04731,0.22275],"force_p95":0.11209,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3998,"mean_force":0.07564,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50838,0.02845,0.22125]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17522.0,"contact_point_centroid":[0.515,0.01358,0.23093],"force_p95":0.11543,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36731,"mean_force":0.07792,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5101,0.03194,0.22926]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":213.0,"contact_point_centroid":[0.59348,0.17077,0.24399],"force_p95":0.15699,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29431,"mean_force":0.08981,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58249,0.18506,0.24873]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5038,-0.01578,-0.00202],"force_p95":0.13088,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14436,"mean_force":0.12484,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49162,-0.01554,0.03528]},{"body_a":"world","body_b":"grasp_target","contact_count":1908.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13338,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49879,-0.00698,0.21967]},{"body_a":"world","body_b":"grasp_target","contact_count":3432.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49764,-0.0151,0.07783]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4141.0,"contact_point_centroid":[0.48972,-0.03477,0.03647],"force_p95":0.07917,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09657,"mean_force":0.05174,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49038,-0.01553,0.03396]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5098.0,"contact_point_centroid":[0.49142,0.00353,0.03566],"force_p95":0.06839,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08883,"mean_force":0.04297,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49038,-0.01553,0.03396]}],"total_contact_groups":13},"final_pose_error":0.00499,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.59803,0.17758,0.01668],"final_tcp_position":[0.58334,0.1853,0.25086],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1.79867,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":478.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1908.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49952,-0.01432,0.13873],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1128,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":858.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3432.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49863,-0.0156,0.04279],"tcp_start":[0.49952,-0.01432,0.13873],"tcp_to_object_dist_end":0.01755,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50368,-0.01588,0.0259],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31249,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13113,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11039.0,"raw_peak_contact_force":0.14436,"subtask_id":"grasp_1","tcp_end":[0.49035,-0.01553,0.03393],"tcp_start":[0.49863,-0.0156,0.04279],"tcp_to_object_dist_end":0.01556,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1351.0,"n_steps_budget":1000.0,"object_pos_end":[0.55103,0.09187,0.31983],"object_pos_start":[0.50368,-0.01588,0.0259],"object_to_goal_dist_end":0.12476,"object_to_goal_dist_start":0.31249,"object_z_max":0.38198,"peak_contact_force":0.13857,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35831.0,"raw_peak_contact_force":0.71877,"subtask_id":"transport_arc","tcp_end":[0.57764,0.16994,0.39936],"tcp_start":[0.53889,0.08986,0.34063],"tcp_to_object_dist_end":0.11458,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":13.0,"n_steps":611.0,"n_steps_budget":1000.0,"object_pos_end":[0.58858,0.18866,0.21759],"object_pos_start":[0.58551,0.17269,0.37391],"object_to_goal_dist_end":0.0306,"object_to_goal_dist_start":0.12667,"object_z_max":0.37391,"peak_contact_force":0.20441,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10958.0,"raw_peak_contact_force":0.54846,"subtask_id":"release_1","tcp_end":[0.58334,0.1853,0.25086],"tcp_start":[0.57764,0.16994,0.39936],"tcp_to_object_dist_end":0.03385,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59803,0.17758,0.01668],"object_pos_start":[0.58858,0.18866,0.21759],"object_to_goal_dist_end":0.23192,"object_to_goal_dist_start":0.0306,"object_z_max":0.21759,"peak_contact_force":0.11651,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":644.0,"raw_peak_contact_force":1.79867,"tcp_end":[0.57901,0.18381,0.27187],"tcp_start":[0.58334,0.1853,0.25086],"tcp_to_object_dist_end":0.25598,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```