## Search State

- **Seed**: 3
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0768 | 0.47 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.3400 | 0.83 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0779 | 0.47 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | 0.1362 | 0.48 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0772 | 0.47 | ❌ rejected |

**Proposal policy**: task_score is 0.47 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `51caab5aeef033bda3880e250ac3d834b494dfd11f1563b679caeea40811318b`
- Frozen object start: [0.45856491671436245, -0.02631894934039003, 0.03]
- Frozen task target: [0.6301274465206397, 0.20821620360643678, 0.11411929633605988]
- Goal object position: (0.6301274465206397, 0.20821620360643678, 0.11411929633605988)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6301274465206397, 0.20821620360643678, 0.11411929633605988)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.45856491671436245, -0.02631894934039003, 0.03)
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
  frozen_object_start: [0.4586, -0.0263, 0.03]
  frozen_task_target: [0.6301, 0.2082, 0.1141]
  frozen_object_starts: {'grasp_target': [0.45856491671436245, -0.02631894934039003, 0.03]}
  frozen_targets: {'place_target': [0.6301274465206397, 0.20821620360643678, 0.11411929633605988]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 51caab5aeef033bda3880e250ac3d834b494dfd11f1563b679caeea40811318b

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

## Current Skill (Q=0.077) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
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
    - 0.1
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
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
    offset:
    - 0.0
    - 0.0
    - 0.03
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
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
  guards:
  - id: grasp_check
    when: during_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
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
    - 0.05
  parameters:
    approach_z_offset:
      type: scalar
      range:
      - 0.03
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: descend_2
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
  parameters:
    place_z_offset:
      type: scalar
      range:
      - 0.015
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: release_1
- id: final_hold
  type: grasp
  control: impedance_control
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
    hold_duration:
      type: scalar
      range:
      - 0.2
      - 0.6
      default: 0.4
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: hold_check
    when: during_phase
    predicate: object_lifted
    threshold: 0.1
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1]
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.03]
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=repeat
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15]
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05]
  - parameter_bindings:
    - approach_z_offset: status=consumed; consumers=target.offset.z (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03]
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **final_hold** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - hold_duration: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=hold_check, when=during_phase, predicate=object_lifted, on_failure=retry, threshold=0.1
  - retries: max_attempts=1, strategy=repeat

## Design Metrics

- **Composite score**: 0.077
- **task_score** (E): 0.467
- **fitness_score**: 0.707  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1398 |
| descend_1 | 1.00 | 1.00 | 0.1227 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 0.67 | 1.00 | 0.1471 |
| transport_1 | 0.67 | 1.00 | 0.1855 |
| descend_2 | 1.00 | 1.00 | 0.0862 |
| release_1 | 1.00 | 1.00 | 0.0209 |
| retract_1 | 0.33 | 1.00 | 0.1422 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.505, 0.001, 0.167) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.505, 0.001, 0.167)→(0.506, 0.002, 0.045) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.002, 0.045)→(0.497, 0.002, 0.035) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 43.000 | 0.141 | 0.181 |
| lift_1 | lift | 0.67 / step_budget | (0.497, 0.002, 0.035)→(0.505, 0.002, 0.182) | (0.511, 0.002, 0.026)→(0.514, 0.002, 0.165) | 0.246→0.218 | 1.00 / 37.000 | 0.081 | 0.572 |
| transport_1 | approach | 0.67 / step_budget | (0.505, 0.002, 0.182)→(0.599, 0.147, 0.222) | (0.514, 0.002, 0.165)→(0.598, 0.148, 0.197) | 0.218→0.075 | 1.00 / 40.333 | 0.077 | 0.318 |
| descend_2 | descend | 1.00 / step_budget | (0.599, 0.147, 0.222)→(0.620, 0.177, 0.147) | (0.598, 0.148, 0.197)→(0.616, 0.175, 0.092) | 0.075→0.048 | 1.00 / 27.333 | 95.853 | 0.587 |
| release_1 | release | 1.00 / step_budget | (0.620, 0.177, 0.147)→(0.613, 0.176, 0.167) | (0.616, 0.175, 0.092)→(0.605, 0.172, 0.023) | 0.048→0.118 | 1.00 / 3.667 | 0.134 | 1.111 |
| retract_1 | retract | 0.33 / step_budget | (0.613, 0.176, 0.167)→(0.611, 0.175, 0.309) | (0.605, 0.172, 0.023)→(0.603, 0.171, 0.023) | 0.118→0.118 | 1.00 / 4.000 | 0.123 | 0.149 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.562
- phase_score: 0.511
- phase_breakdown.release_1_score: 0.511
- phase_breakdown.descend_1_score: 0.852
- phase_breakdown.transport_arc_score: 0.359
- phase_breakdown.approach_1_score: 0.029
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.755

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.755
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.562
- **Median Q (composite search score)**: 0.099
- **K-run variance**: 0.0026
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.396


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `952d4e9e12c194d228cf63d10b31c959edc327920598c352d26dcf1284463776`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ab36b663de63a40a5839be0af4fc1d53d37f9e78d4183a3de7f11063534632b8`; realized-scene SHA-256: `51caab5aeef033bda3880e250ac3d834b494dfd11f1563b679caeea40811318b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89674,"average_solve_count":184.0,"average_success_count":184.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05022,"descend_1.grasp_z_offset":0.01022,"descend_2.place_z_offset":0.00973,"lift_1.lift_height":0.143,"release_1.release_duration":0.18464,"retract_1.retract_height":0.21632,"transport_1.approach_z_offset":0.05672,"transport_1.arc_height":0.09183,"transport_1.transport_speed":0.23353},"optimized_scores":{"best_composite_score":0.0988,"best_fitness_score":0.7288,"best_task_score":0.51165},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":36.0,"contact_point_centroid":[0.6173,0.18656,-0.00357],"force_p95":1.03267,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.17344,"mean_force":0.73831,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62197,0.20189,0.12256]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.61384,0.1935,-0.00281],"force_p95":0.2887,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68021,"mean_force":0.13638,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61747,0.20093,0.12209]},{"body_a":"world","body_b":"grasp_target","contact_count":135.0,"contact_point_centroid":[0.45642,-0.02514,-0.00111],"force_p95":0.2929,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51036,"mean_force":0.05884,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44449,-0.02549,0.03906]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7379.0,"contact_point_centroid":[0.58416,0.17623,0.18935],"force_p95":0.12298,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34769,"mean_force":0.07763,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58815,0.15768,0.18964]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19145.0,"contact_point_centroid":[0.50851,0.02807,0.22641],"force_p95":0.07838,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31483,"mean_force":0.05257,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50628,0.04714,0.22435]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16081.0,"contact_point_centroid":[0.44932,-0.00661,0.09829],"force_p95":0.07279,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28906,"mean_force":0.0484,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44788,-0.02564,0.09649]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13829.0,"contact_point_centroid":[0.44766,-0.04483,0.09985],"force_p95":0.07952,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28707,"mean_force":0.05488,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44794,-0.02564,0.09709]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19768.0,"contact_point_centroid":[0.50163,0.06038,0.22355],"force_p95":0.07277,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26639,"mean_force":0.05061,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50194,0.04141,0.22134]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8841.0,"contact_point_centroid":[0.59267,0.14061,0.18535],"force_p95":0.10568,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24581,"mean_force":0.0672,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.58896,0.15873,0.18805]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02636,-0.00206],"force_p95":0.14268,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17817,"mean_force":0.12752,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4468,-0.02555,0.03824]},{"body_a":"world","body_b":"grasp_target","contact_count":2544.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.13046,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47774,-0.01204,0.1947]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5097.0,"contact_point_centroid":[0.447,-0.00644,0.03857],"force_p95":0.06862,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12562,"mean_force":0.04293,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44564,-0.02552,0.03713]},{"body_a":"world","body_b":"grasp_target","contact_count":632.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4544,-0.02508,0.06732]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.61384,0.19356,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61261,0.19926,0.21828]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4416.0,"contact_point_centroid":[0.44511,-0.04477,0.03992],"force_p95":0.07926,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08532,"mean_force":0.04914,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44564,-0.02552,0.03713]}],"total_contact_groups":15},"final_pose_error":0.05803,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61384,0.19356,0.01602],"final_tcp_position":[0.6133,0.19943,0.29995],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.17344,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":637.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2544.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45699,-0.02449,0.08971],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.06374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":158.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":632.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45371,-0.02574,0.04492],"tcp_start":[0.45699,-0.02449,0.08971],"tcp_to_object_dist_end":0.01952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45849,-0.02602,0.02577],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30354,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14228,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11313.0,"raw_peak_contact_force":0.17817,"tcp_end":[0.44561,-0.02552,0.0371],"tcp_start":[0.45371,-0.02574,0.04492],"tcp_to_object_dist_end":0.01716,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.4639,-0.02654,0.14026],"object_pos_start":[0.45849,-0.02602,0.02577],"object_to_goal_dist_end":0.28883,"object_to_goal_dist_start":0.30354,"object_z_max":0.14015,"peak_contact_force":0.07859,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":30045.0,"raw_peak_contact_force":0.51036,"tcp_end":[0.45412,-0.02587,0.1574],"tcp_start":[0.44561,-0.02552,0.0371],"tcp_to_object_dist_end":0.01974,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56728,0.1277,0.21849],"object_pos_start":[0.4639,-0.02654,0.14026],"object_to_goal_dist_end":0.14604,"object_to_goal_dist_start":0.28883,"object_z_max":0.22693,"peak_contact_force":0.08023,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38913.0,"raw_peak_contact_force":0.31483,"subtask_id":"transport_arc","tcp_end":[0.56633,0.12658,0.2431],"tcp_start":[0.45412,-0.02587,0.1574],"tcp_to_object_dist_end":0.02465,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":640.0,"n_steps_budget":1000.0,"object_pos_end":[0.61428,0.19398,0.0071],"object_pos_start":[0.56728,0.1277,0.21849],"object_to_goal_dist_end":0.10912,"object_to_goal_dist_start":0.14604,"object_z_max":0.21849,"peak_contact_force":0.72076,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16256.0,"raw_peak_contact_force":1.17344,"tcp_end":[0.62229,0.20238,0.12178],"tcp_start":[0.56633,0.12658,0.2431],"tcp_to_object_dist_end":0.11527,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61384,0.19356,0.01602],"object_pos_start":[0.61428,0.19398,0.0071],"object_to_goal_dist_end":0.10052,"object_to_goal_dist_start":0.10912,"object_z_max":0.01643,"peak_contact_force":0.12262,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":800.0,"raw_peak_contact_force":0.68021,"subtask_id":"release_1","tcp_end":[0.61563,0.20029,0.1416],"tcp_start":[0.62229,0.20238,0.12178],"tcp_to_object_dist_end":0.12577,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61384,0.19356,0.01602],"object_pos_start":[0.61384,0.19356,0.01602],"object_to_goal_dist_end":0.10052,"object_to_goal_dist_start":0.10052,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6133,0.19943,0.29995],"tcp_start":[0.61563,0.20029,0.1416],"tcp_to_object_dist_end":0.28399,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `aa6ec658384c70fac6b4eb656cc8c53536c3d5c760368ab2b384dccf294e2c48`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.99419,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16986,"descend_1.grasp_z_offset":0.01076,"descend_2.place_z_offset":0.00293,"lift_1.lift_height":0.26582,"release_1.release_duration":0.20491,"retract_1.retract_height":0.22736,"transport_1.approach_z_offset":0.05241,"transport_1.arc_height":0.12201,"transport_1.transport_speed":0.22097},"optimized_scores":{"best_composite_score":0.00679,"best_fitness_score":0.63679,"best_task_score":0.32651},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":219.0,"contact_point_centroid":[0.61984,0.14835,-0.00652],"force_p95":1.23196,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.67523,"mean_force":0.33354,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63569,0.15213,0.21031]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.5413,0.00113,-0.00112],"force_p95":0.43424,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59872,"mean_force":0.08394,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52834,0.0008,0.0362]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17756.0,"contact_point_centroid":[0.57913,0.0423,0.26644],"force_p95":0.08601,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37161,"mean_force":0.05716,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57613,0.06114,0.2655]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3481.0,"contact_point_centroid":[0.63084,0.16493,0.2317],"force_p95":0.08485,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35709,"mean_force":0.05531,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63611,0.14656,0.23082]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17886.0,"contact_point_centroid":[0.53179,0.01996,0.11751],"force_p95":0.07999,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34445,"mean_force":0.05644,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53046,0.00084,0.11526]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17071.0,"contact_point_centroid":[0.57416,0.07749,0.26575],"force_p95":0.08557,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32674,"mean_force":0.05821,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57427,0.05856,0.26406]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19272.0,"contact_point_centroid":[0.53156,-0.01819,0.11365],"force_p95":0.07716,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32223,"mean_force":0.05303,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53026,0.00084,0.11167]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1161.0,"contact_point_centroid":[0.63386,0.17154,0.19655],"force_p95":0.07085,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28417,"mean_force":0.04612,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63932,0.15317,0.19563]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3481.0,"contact_point_centroid":[0.63863,0.12759,0.22979],"force_p95":0.08787,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26874,"mean_force":0.05589,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63611,0.14656,0.23082]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1179.0,"contact_point_centroid":[0.64183,0.13413,0.19428],"force_p95":0.0712,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25233,"mean_force":0.04599,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63929,0.15317,0.19558]},{"body_a":"world","body_b":"grasp_target","contact_count":3991.0,"contact_point_centroid":[0.619,0.14749,-0.00198],"force_p95":0.12576,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16871,"mean_force":0.12232,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.63341,0.1515,0.29624]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00115,-0.00203],"force_p95":0.13137,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1537,"mean_force":0.12535,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53108,0.00086,0.036]},{"body_a":"world","body_b":"grasp_target","contact_count":1408.0,"contact_point_centroid":[0.54431,0.00113,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51664,0.00046,0.25186]},{"body_a":"world","body_b":"grasp_target","contact_count":1924.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53593,0.00096,0.12429]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4149.0,"contact_point_centroid":[0.53102,0.02013,0.03708],"force_p95":0.07645,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09659,"mean_force":0.05218,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52982,0.00083,0.03452]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5327.0,"contact_point_centroid":[0.53033,-0.0182,0.03714],"force_p95":0.06271,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08758,"mean_force":0.04072,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52981,0.00083,0.03452]}],"total_contact_groups":16},"final_pose_error":0.06829,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.61896,0.14743,0.02602],"final_tcp_position":[0.63421,0.15166,0.37818],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.67523,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":353.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1408.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53589,0.00095,0.20504],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17922,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":481.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1924.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53866,0.00102,0.04495],"tcp_start":[0.53589,0.00095,0.20504],"tcp_to_object_dist_end":0.01976,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54419,0.0011,0.02586],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2503,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13108,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11276.0,"raw_peak_contact_force":0.1537,"tcp_end":[0.52978,0.00083,0.03448],"tcp_start":[0.53866,0.00102,0.04495],"tcp_to_object_dist_end":0.01679,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54481,0.00095,0.17895],"object_pos_start":[0.54419,0.0011,0.02586],"object_to_goal_dist_end":0.18817,"object_to_goal_dist_start":0.2503,"object_z_max":0.17876,"peak_contact_force":0.08308,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37302.0,"raw_peak_contact_force":0.59872,"tcp_end":[0.53551,0.00094,0.19588],"tcp_start":[0.52978,0.00083,0.03448],"tcp_to_object_dist_end":0.01932,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62958,0.14086,0.23585],"object_pos_start":[0.54481,0.00095,0.17895],"object_to_goal_dist_end":0.05123,"object_to_goal_dist_start":0.18817,"object_z_max":0.2707,"peak_contact_force":0.07394,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34827.0,"raw_peak_contact_force":0.37161,"subtask_id":"transport_arc","tcp_end":[0.63304,0.14047,0.26267],"tcp_start":[0.53551,0.00094,0.19588],"tcp_to_object_dist_end":0.02705,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":183.0,"n_steps_budget":1000.0,"object_pos_end":[0.63762,0.15427,0.17238],"object_pos_start":[0.62958,0.14086,0.23585],"object_to_goal_dist_end":0.02157,"object_to_goal_dist_start":0.05123,"object_z_max":0.23585,"peak_contact_force":0.07265,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6962.0,"raw_peak_contact_force":0.35709,"tcp_end":[0.64115,0.1535,0.20002],"tcp_start":[0.63304,0.14047,0.26267],"tcp_to_object_dist_end":0.02787,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62523,0.14919,0.02502],"object_pos_start":[0.63762,0.15427,0.17238],"object_to_goal_dist_end":0.16782,"object_to_goal_dist_start":0.02157,"object_z_max":0.17238,"peak_contact_force":0.13103,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2559.0,"raw_peak_contact_force":1.67523,"subtask_id":"release_1","tcp_end":[0.63564,0.15212,0.2191],"tcp_start":[0.64115,0.1535,0.20002],"tcp_to_object_dist_end":0.19438,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61896,0.14743,0.02602],"object_pos_start":[0.62523,0.14919,0.02502],"object_to_goal_dist_end":0.16789,"object_to_goal_dist_start":0.16782,"object_z_max":0.02671,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3991.0,"raw_peak_contact_force":0.16871,"tcp_end":[0.63421,0.15166,0.37818],"tcp_start":[0.63564,0.15212,0.2191],"tcp_to_object_dist_end":0.35252,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e1209649252ffcf03853fe0727696e22a1eda11729c6c1ae21659980557d7e98`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89571,"average_solve_count":163.0,"average_success_count":163.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17148,"descend_1.grasp_z_offset":0.01001,"descend_2.place_z_offset":0.00247,"lift_1.lift_height":0.21306,"release_1.release_duration":0.30082,"retract_1.retract_height":0.12332,"transport_1.approach_z_offset":0.04322,"transport_1.arc_height":0.06878,"transport_1.transport_speed":0.1801},"optimized_scores":{"best_composite_score":0.12475,"best_fitness_score":0.75475,"best_task_score":0.56163},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":325.0,"contact_point_centroid":[0.57578,0.17193,-0.0037],"force_p95":0.8506,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.9764,"mean_force":0.22469,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58922,0.17432,0.12702]},{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.52746,0.02906,-0.0012],"force_p95":0.41276,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60681,"mean_force":0.08339,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51489,0.02947,0.03596]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.5185,0.04874,0.11503],"force_p95":0.08234,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34103,"mean_force":0.05881,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51794,0.02954,0.11228]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20477.0,"contact_point_centroid":[0.51962,0.0106,0.1125],"force_p95":0.07759,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31461,"mean_force":0.05024,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51784,0.02954,0.11086]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19980.0,"contact_point_centroid":[0.56298,0.08434,0.21611],"force_p95":0.07448,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26633,"mean_force":0.04896,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55934,0.10293,0.21519]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1161.0,"contact_point_centroid":[0.58994,0.19439,0.11771],"force_p95":0.07508,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25283,"mean_force":0.04561,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5937,0.17568,0.11441]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1348.0,"contact_point_centroid":[0.59853,0.15705,0.11475],"force_p95":0.07267,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24163,"mean_force":0.04106,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5937,0.17568,0.11441]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2269.0,"contact_point_centroid":[0.59159,0.19406,0.14213],"force_p95":0.07705,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22996,"mean_force":0.05361,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59535,0.17539,0.13878]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16405.0,"contact_point_centroid":[0.55788,0.12227,0.21724],"force_p95":0.09111,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22735,"mean_force":0.06029,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55949,0.10323,0.21434]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03077,-0.0021],"force_p95":0.15266,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21063,"mean_force":0.13052,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51758,0.02966,0.03558]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2715.0,"contact_point_centroid":[0.6002,0.1568,0.13927],"force_p95":0.07227,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21047,"mean_force":0.04686,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59535,0.1754,0.13854]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5277.0,"contact_point_centroid":[0.51743,0.01055,0.03611],"force_p95":0.06754,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16902,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51632,0.02958,0.03416]},{"body_a":"world","body_b":"grasp_target","contact_count":2772.0,"contact_point_centroid":[0.57496,0.17174,-0.00198],"force_p95":0.12545,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15426,"mean_force":0.12268,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58583,0.17332,0.19148]},{"body_a":"world","body_b":"grasp_target","contact_count":1332.0,"contact_point_centroid":[0.5305,0.03079,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51055,0.01311,0.25325]},{"body_a":"world","body_b":"grasp_target","contact_count":1984.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52294,0.02846,0.12503]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4213.0,"contact_point_centroid":[0.51687,0.0489,0.03698],"force_p95":0.08167,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0843,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51633,0.02958,0.03417]}],"total_contact_groups":16},"final_pose_error":0.0146,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57495,0.17174,0.02602],"final_tcp_position":[0.58617,0.1734,0.24803],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":286.76638,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":334.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1332.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52347,0.02693,0.20723],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18138,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":496.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1984.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52505,0.03015,0.04417],"tcp_start":[0.52347,0.02693,0.20723],"tcp_to_object_dist_end":0.01896,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53044,0.03015,0.02563],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18408,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15093,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11290.0,"raw_peak_contact_force":0.21063,"tcp_end":[0.51629,0.02958,0.03413],"tcp_start":[0.52505,0.03015,0.04417],"tcp_to_object_dist_end":0.01651,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53337,0.0305,0.17679],"object_pos_start":[0.53044,0.03015,0.02563],"object_to_goal_dist_end":0.1769,"object_to_goal_dist_start":0.18408,"object_z_max":0.17661,"peak_contact_force":0.08105,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37625.0,"raw_peak_contact_force":0.60681,"tcp_end":[0.52405,0.0298,0.19316],"tcp_start":[0.51629,0.02958,0.03413],"tcp_to_object_dist_end":0.01885,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":956.0,"n_steps_budget":1000.0,"object_pos_end":[0.59577,0.17614,0.13608],"object_pos_start":[0.53337,0.0305,0.17679],"object_to_goal_dist_end":0.02868,"object_to_goal_dist_start":0.1769,"object_z_max":0.215,"peak_contact_force":0.07586,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36385.0,"raw_peak_contact_force":0.26633,"subtask_id":"transport_arc","tcp_end":[0.59632,0.17494,0.15885],"tcp_start":[0.52405,0.0298,0.19316],"tcp_to_object_dist_end":0.0228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":120.0,"n_steps_budget":1000.0,"object_pos_end":[0.59594,0.17793,0.09516],"object_pos_start":[0.59577,0.17614,0.13608],"object_to_goal_dist_end":0.0141,"object_to_goal_dist_start":0.02868,"object_z_max":0.13608,"peak_contact_force":286.76638,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4984.0,"raw_peak_contact_force":0.22996,"tcp_end":[0.59594,0.17632,0.11836],"tcp_start":[0.59632,0.17494,0.15885],"tcp_to_object_dist_end":0.02326,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57535,0.17175,0.02659],"object_pos_start":[0.59594,0.17793,0.09516],"object_to_goal_dist_end":0.08588,"object_to_goal_dist_start":0.0141,"object_z_max":0.09516,"peak_contact_force":0.14749,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2834.0,"raw_peak_contact_force":0.9764,"subtask_id":"release_1","tcp_end":[0.58908,0.17428,0.13899],"tcp_start":[0.59594,0.17632,0.11836],"tcp_to_object_dist_end":0.11327,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.57495,0.17174,0.02602],"object_pos_start":[0.57535,0.17175,0.02659],"object_to_goal_dist_end":0.08654,"object_to_goal_dist_start":0.08588,"object_z_max":0.02659,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2772.0,"raw_peak_contact_force":0.15426,"tcp_end":[0.58617,0.1734,0.24803],"tcp_start":[0.58908,0.17428,0.13899],"tcp_to_object_dist_end":0.2223,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```