## Search State

- **Seed**: 3
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0779 | 0.47 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | 0.1362 | 0.48 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0772 | 0.47 | ❌ rejected |
| 6 | approach → descend → grasp → lift → grasp → approach → descend → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | — | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 9 | 0.2272 | 0.77 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | 0.1426 | 0.46 | ❌ rejected |

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

## Current Skill (Q=0.078) — your mutation base

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
- id: secure_grasp
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
    squeeze_duration:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: duration.max_time
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
    - 0.024
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
    transport_height_offset:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.024
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: descend_2
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
    - 0.024
  parameters:
    fine_place_offset:
      type: scalar
      range:
      - 0.015
      - 0.035
      default: 0.024
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: release_1
- id: hold_final
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
    hold_duration:
      type: scalar
      range:
      - 0.2
      - 0.8
      default: 0.4
      binds_to:
      - path: duration.max_time
        mode: replace

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
- **secure_grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - squeeze_duration: status=consumed; consumers=duration.max_time (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.024]
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_height_offset: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.024]
  - parameter_bindings:
    - fine_place_offset: status=consumed; consumers=target.offset.z (replace)
- **hold_final** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - hold_duration: status=consumed; consumers=duration.max_time (replace)

## Design Metrics

- **Composite score**: 0.078
- **task_score** (E): 0.468
- **fitness_score**: 0.708  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1337 |
| descend_1 | 1.00 | 1.00 | 0.1291 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 0.67 | 1.00 | 0.1348 |
| transport_1 | 0.67 | 1.00 | 0.1693 |
| descend_2 | 1.00 | 1.00 | 0.0615 |
| release_1 | 1.00 | 1.00 | 0.0210 |
| retract_1 | 1.00 | 1.00 | 0.1265 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.001, 0.173) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.001, 0.173)→(0.506, 0.002, 0.044) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.002, 0.044)→(0.497, 0.002, 0.035) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 42.667 | 0.141 | 0.179 |
| lift_1 | lift | 0.67 / step_budget | (0.497, 0.002, 0.035)→(0.505, 0.002, 0.169) | (0.511, 0.002, 0.026)→(0.515, 0.002, 0.154) | 0.246→0.214 | 1.00 / 37.000 | 0.081 | 0.575 |
| transport_1 | approach | 0.67 / step_budget | (0.505, 0.002, 0.169)→(0.591, 0.137, 0.206) | (0.515, 0.002, 0.154)→(0.591, 0.138, 0.183) | 0.214→0.073 | 1.00 / 42.000 | 0.070 | 0.279 |
| descend_2 | descend | 1.00 / step_budget | (0.591, 0.137, 0.206)→(0.620, 0.177, 0.171) | (0.591, 0.138, 0.183)→(0.617, 0.178, 0.144) | 0.073→0.013 | 1.00 / 37.000 | 0.088 | 0.272 |
| release_1 | release | 1.00 / step_budget | (0.620, 0.177, 0.171)→(0.614, 0.175, 0.191) | (0.617, 0.178, 0.144)→(0.608, 0.171, 0.022) | 0.013→0.118 | 1.00 / 4.000 | 0.126 | 1.317 |
| retract_1 | retract | 1.00 / step_budget | (0.614, 0.175, 0.191)→(0.612, 0.175, 0.317) | (0.608, 0.171, 0.022)→(0.605, 0.171, 0.023) | 0.118→0.118 | 1.00 / 4.000 | 0.123 | 0.143 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.565
- phase_score: 0.583
- phase_breakdown.release_1_score: 0.366
- phase_breakdown.descend_1_score: 0.854
- phase_breakdown.transport_arc_score: 0.530
- phase_breakdown.approach_1_score: 0.027
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.756

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.756
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.565
- **Median Q (composite search score)**: 0.100
- **K-run variance**: 0.0026
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.312


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10757,"descend_1.grasp_z_offset":0.01,"descend_2.descent_offset":0.03942,"lift_1.lift_height":0.14793,"release_1.release_duration":0.19033,"retract_1.retract_height":0.14668,"transport_1.arc_height":0.10827,"transport_1.transport_height_offset":0.01005,"transport_1.transport_speed":0.16151},"optimized_scores":{"best_composite_score":0.09989,"best_fitness_score":0.72989,"best_task_score":0.51268},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":519.0,"contact_point_centroid":[0.61737,0.19199,-0.00364],"force_p95":0.6908,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.13192,"mean_force":0.18972,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61682,0.20052,0.15127]},{"body_a":"world","body_b":"grasp_target","contact_count":132.0,"contact_point_centroid":[0.4565,-0.02531,-0.00111],"force_p95":0.30178,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51563,"mean_force":0.05941,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44477,-0.02563,0.0388]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":195.0,"contact_point_centroid":[0.62655,0.18641,0.14149],"force_p95":0.16195,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31696,"mean_force":0.04827,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62201,0.20234,0.1474]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14787.0,"contact_point_centroid":[0.5737,0.16228,0.19713],"force_p95":0.10927,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29879,"mean_force":0.06608,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57748,0.14364,0.19612]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14640.0,"contact_point_centroid":[0.44777,-0.04496,0.10227],"force_p95":0.07903,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28897,"mean_force":0.0539,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44809,-0.02577,0.09949]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16745.0,"contact_point_centroid":[0.44942,-0.00672,0.10074],"force_p95":0.07279,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28819,"mean_force":0.04827,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44805,-0.02577,0.09895]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17063.0,"contact_point_centroid":[0.58142,0.1258,0.1945],"force_p95":0.09805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25294,"mean_force":0.05902,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.57793,0.14423,0.19564]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19199.0,"contact_point_centroid":[0.49565,0.01156,0.22229],"force_p95":0.07802,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22666,"mean_force":0.0516,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.4938,0.03063,0.22016]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19627.0,"contact_point_centroid":[0.49071,0.04527,0.21944],"force_p95":0.07256,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2008,"mean_force":0.05052,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49047,0.02621,0.21718]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02638,-0.00205],"force_p95":0.13968,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17388,"mean_force":0.12675,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44709,-0.0257,0.03803]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":57.0,"contact_point_centroid":[0.61706,0.2203,0.14394],"force_p95":0.15257,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.172,"mean_force":0.09209,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6224,0.20238,0.14817]},{"body_a":"world","body_b":"grasp_target","contact_count":1868.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47879,-0.01159,0.22396]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5309.0,"contact_point_centroid":[0.4469,-0.00657,0.03838],"force_p95":0.0684,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1268,"mean_force":0.04133,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44592,-0.02567,0.03693]},{"body_a":"world","body_b":"grasp_target","contact_count":3372.0,"contact_point_centroid":[0.61729,0.19227,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12348,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61356,0.19939,0.23179]},{"body_a":"world","body_b":"grasp_target","contact_count":1320.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45499,-0.02485,0.09552]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4409.0,"contact_point_centroid":[0.44534,-0.04494,0.0397],"force_p95":0.07944,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08967,"mean_force":0.04916,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44593,-0.02567,0.03693]}],"total_contact_groups":16},"final_pose_error":0.01509,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.61729,0.19227,0.01602],"final_tcp_position":[0.61413,0.19954,0.30011],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.13192,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":468.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1868.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45843,-0.0239,0.14699],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12099,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":330.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1320.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45402,-0.0259,0.04473],"tcp_start":[0.45843,-0.0239,0.14699],"tcp_to_object_dist_end":0.01926,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45847,-0.02614,0.02581],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30362,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13958,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11518.0,"raw_peak_contact_force":0.17388,"tcp_end":[0.4459,-0.02567,0.0369],"tcp_start":[0.45402,-0.0259,0.04473],"tcp_to_object_dist_end":0.01677,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.46376,-0.02665,0.14528],"object_pos_start":[0.45847,-0.02614,0.02581],"object_to_goal_dist_end":0.2895,"object_to_goal_dist_start":0.30362,"object_z_max":0.14516,"peak_contact_force":0.0785,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":31517.0,"raw_peak_contact_force":0.51563,"tcp_end":[0.45418,-0.02599,0.16234],"tcp_start":[0.4459,-0.02567,0.0369],"tcp_to_object_dist_end":0.01958,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54386,0.09196,0.2229],"object_pos_start":[0.46376,-0.02665,0.14528],"object_to_goal_dist_end":0.18108,"object_to_goal_dist_start":0.2895,"object_z_max":0.22339,"peak_contact_force":0.07057,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38826.0,"raw_peak_contact_force":0.22666,"subtask_id":"transport_arc","tcp_end":[0.53913,0.09066,0.24493],"tcp_start":[0.45418,-0.02599,0.16234],"tcp_to_object_dist_end":0.02257,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61853,0.2031,0.11522],"object_pos_start":[0.54386,0.09196,0.2229],"object_to_goal_dist_end":0.01272,"object_to_goal_dist_start":0.18108,"object_z_max":0.2229,"peak_contact_force":0.12375,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":31850.0,"raw_peak_contact_force":0.29879,"subtask_id":"release_1","tcp_end":[0.62255,0.20232,0.14847],"tcp_start":[0.53913,0.09066,0.24493],"tcp_to_object_dist_end":0.03351,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61729,0.19226,0.01601],"object_pos_start":[0.61853,0.2031,0.11522],"object_to_goal_dist_end":0.10022,"object_to_goal_dist_start":0.01272,"object_z_max":0.11522,"peak_contact_force":0.12354,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":771.0,"raw_peak_contact_force":1.13192,"tcp_end":[0.61641,0.20037,0.16833],"tcp_start":[0.62255,0.20232,0.14847],"tcp_to_object_dist_end":0.15253,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.61729,0.19227,0.01602],"object_pos_start":[0.61729,0.19226,0.01601],"object_to_goal_dist_end":0.10021,"object_to_goal_dist_start":0.10022,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3372.0,"raw_peak_contact_force":0.12348,"tcp_end":[0.61413,0.19954,0.30011],"tcp_start":[0.61641,0.20037,0.16833],"tcp_to_object_dist_end":0.2842,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81818,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12609,"descend_1.grasp_z_offset":0.01022,"descend_2.descent_offset":0.0402,"lift_1.lift_height":0.24743,"release_1.release_duration":0.21408,"retract_1.retract_height":0.14308,"transport_1.arc_height":0.10218,"transport_1.transport_height_offset":0.02469,"transport_1.transport_speed":0.24283},"optimized_scores":{"best_composite_score":0.00752,"best_fitness_score":0.63752,"best_task_score":0.32729},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":194.0,"contact_point_centroid":[0.62063,0.14811,-0.00792],"force_p95":1.2004,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.6231,"mean_force":0.38849,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63553,0.15105,0.24006]},{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.54051,0.00081,-0.00115],"force_p95":0.44776,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61538,"mean_force":0.09605,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52823,0.0008,0.03537]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18417.0,"contact_point_centroid":[0.58377,0.04857,0.2622],"force_p95":0.08593,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36292,"mean_force":0.05535,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58108,0.06748,0.26112]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18017.0,"contact_point_centroid":[0.53198,0.01995,0.11669],"force_p95":0.07985,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34438,"mean_force":0.05618,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53071,0.00083,0.11447]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19183.0,"contact_point_centroid":[0.53178,-0.0182,0.11347],"force_p95":0.07747,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32179,"mean_force":0.05326,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53053,0.00083,0.11142]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17436.0,"contact_point_centroid":[0.57835,0.0835,0.26175],"force_p95":0.08586,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31542,"mean_force":0.05715,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57904,0.06461,0.25982]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":934.0,"contact_point_centroid":[0.63334,0.16829,0.23392],"force_p95":0.07558,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27741,"mean_force":0.05177,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63875,0.15,0.23136]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1109.0,"contact_point_centroid":[0.63358,0.17046,0.22581],"force_p95":0.07305,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27575,"mean_force":0.04812,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63887,0.15205,0.22429]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":983.0,"contact_point_centroid":[0.6408,0.13086,0.23158],"force_p95":0.07619,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22979,"mean_force":0.05033,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63877,0.15002,0.23131]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1172.0,"contact_point_centroid":[0.6413,0.13296,0.22355],"force_p95":0.07104,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22763,"mean_force":0.04621,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63884,0.15204,0.22421]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00116,-0.00203],"force_p95":0.13334,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15368,"mean_force":0.12533,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53093,0.00086,0.03528]},{"body_a":"world","body_b":"grasp_target","contact_count":3252.0,"contact_point_centroid":[0.62087,0.14813,-0.00199],"force_p95":0.12491,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14932,"mean_force":0.12132,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.63344,0.15047,0.30898]},{"body_a":"world","body_b":"grasp_target","contact_count":1888.0,"contact_point_centroid":[0.54431,0.00113,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51697,0.00047,0.23065]},{"body_a":"world","body_b":"grasp_target","contact_count":1432.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5362,0.00097,0.10273]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.53084,-0.01822,0.03546],"force_p95":0.06859,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10191,"mean_force":0.04467,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52966,0.00083,0.0338]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4149.0,"contact_point_centroid":[0.53091,0.02005,0.03635],"force_p95":0.07522,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0958,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52966,0.00083,0.0338]}],"total_contact_groups":16},"final_pose_error":0.01516,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.62087,0.14813,0.02602],"final_tcp_position":[0.63405,0.15059,0.37546],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.6231,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":473.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1888.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53663,0.00097,0.1622],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1364,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":358.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1432.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.5385,0.00101,0.04422],"tcp_start":[0.53663,0.00097,0.1622],"tcp_to_object_dist_end":0.0191,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54418,0.00106,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25032,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13337,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10789.0,"raw_peak_contact_force":0.15368,"tcp_end":[0.52963,0.00083,0.03376],"tcp_start":[0.5385,0.00101,0.04422],"tcp_to_object_dist_end":0.01656,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54576,0.00099,0.1798],"object_pos_start":[0.54418,0.00106,0.02587],"object_to_goal_dist_end":0.18757,"object_to_goal_dist_start":0.25032,"object_z_max":0.17962,"peak_contact_force":0.08592,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37345.0,"raw_peak_contact_force":0.61538,"tcp_end":[0.53623,0.00093,0.19607],"tcp_start":[0.52963,0.00083,0.03376],"tcp_to_object_dist_end":0.01886,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63266,0.14846,0.20973],"object_pos_start":[0.54576,0.00099,0.1798],"object_to_goal_dist_end":0.02576,"object_to_goal_dist_start":0.18757,"object_z_max":0.26807,"peak_contact_force":0.07205,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35853.0,"raw_peak_contact_force":0.36292,"subtask_id":"transport_arc","tcp_end":[0.6382,0.14836,0.23566],"tcp_start":[0.53623,0.00093,0.19607],"tcp_to_object_dist_end":0.02652,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":46.0,"n_steps_budget":1000.0,"object_pos_end":[0.63545,0.15256,0.20193],"object_pos_start":[0.63266,0.14846,0.20973],"object_to_goal_dist_end":0.0172,"object_to_goal_dist_start":0.02576,"object_z_max":0.20973,"peak_contact_force":0.07227,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1917.0,"raw_peak_contact_force":0.27741,"subtask_id":"release_1","tcp_end":[0.64032,0.15223,0.22796],"tcp_start":[0.6382,0.14836,0.23566],"tcp_to_object_dist_end":0.02648,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62648,0.14912,0.02217],"object_pos_start":[0.63545,0.15256,0.20193],"object_to_goal_dist_end":0.17048,"object_to_goal_dist_start":0.0172,"object_z_max":0.20193,"peak_contact_force":0.11865,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2475.0,"raw_peak_contact_force":1.6231,"tcp_end":[0.63549,0.15104,0.24747],"tcp_start":[0.64032,0.15223,0.22796],"tcp_to_object_dist_end":0.22548,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.62087,0.14813,0.02602],"object_pos_start":[0.62648,0.14912,0.02217],"object_to_goal_dist_end":0.16753,"object_to_goal_dist_start":0.17048,"object_z_max":0.02686,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3252.0,"raw_peak_contact_force":0.14932,"tcp_end":[0.63405,0.15059,0.37546],"tcp_start":[0.63549,0.15104,0.24747],"tcp_to_object_dist_end":0.3497,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75325,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17542,"descend_1.grasp_z_offset":0.0102,"descend_2.descent_offset":0.03624,"lift_1.lift_height":0.13713,"release_1.release_duration":0.17142,"retract_1.retract_height":0.13394,"transport_1.arc_height":0.17056,"transport_1.transport_height_offset":0.03054,"transport_1.transport_speed":0.21587},"optimized_scores":{"best_composite_score":0.12629,"best_fitness_score":0.75629,"best_task_score":0.56489},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":301.0,"contact_point_centroid":[0.5781,0.1729,-0.0043],"force_p95":0.94646,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.19507,"mean_force":0.24126,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59048,0.17491,0.14576]},{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.52752,0.02888,-0.00119],"force_p95":0.38682,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59507,"mean_force":0.08234,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51511,0.02948,0.03609]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12291.0,"contact_point_centroid":[0.51933,0.04877,0.09365],"force_p95":0.08278,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33651,"mean_force":0.0591,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51888,0.02958,0.09088]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15028.0,"contact_point_centroid":[0.52025,0.01062,0.0913],"force_p95":0.07821,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30933,"mean_force":0.04978,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51874,0.02957,0.08957]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20551.0,"contact_point_centroid":[0.56187,0.08199,0.16824],"force_p95":0.07281,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24699,"mean_force":0.04823,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55856,0.10077,0.16717]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5061.0,"contact_point_centroid":[0.59157,0.19369,0.14019],"force_p95":0.06664,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2401,"mean_force":0.04589,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59539,0.1751,0.1356]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03077,-0.0021],"force_p95":0.15273,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21066,"mean_force":0.13055,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51759,0.02966,0.03571]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17172.0,"contact_point_centroid":[0.55667,0.12,0.17036],"force_p95":0.07855,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21055,"mean_force":0.05535,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55872,0.10107,0.16684]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5784.0,"contact_point_centroid":[0.59997,0.15631,0.13692],"force_p95":0.06222,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20576,"mean_force":0.04144,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59539,0.1751,0.1356]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5277.0,"contact_point_centroid":[0.51743,0.01055,0.03623],"force_p95":0.06753,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16921,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51633,0.02958,0.03429]},{"body_a":"world","body_b":"grasp_target","contact_count":3012.0,"contact_point_centroid":[0.57767,0.17275,-0.00198],"force_p95":0.12565,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15647,"mean_force":0.12259,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58734,0.17397,0.21466]},{"body_a":"world","body_b":"grasp_target","contact_count":1288.0,"contact_point_centroid":[0.5305,0.03079,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51049,0.01302,0.25524]},{"body_a":"world","body_b":"grasp_target","contact_count":2028.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52289,0.02839,0.12701]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4214.0,"contact_point_centroid":[0.51688,0.0489,0.03711],"force_p95":0.08166,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08431,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51634,0.02958,0.0343]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1274.0,"contact_point_centroid":[0.5909,0.19487,0.13721],"force_p95":0.06678,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07195,"mean_force":0.03969,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5949,0.17627,0.13264]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1459.0,"contact_point_centroid":[0.59942,0.15742,0.13386],"force_p95":0.0618,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0647,"mean_force":0.03595,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5949,0.17627,0.13263]}],"total_contact_groups":16},"final_pose_error":0.0146,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57766,0.17275,0.02602],"final_tcp_position":[0.58778,0.17407,0.27652],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.19507,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":323.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1288.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52336,0.02679,0.21116],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18532,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":507.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2028.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52505,0.03015,0.0443],"tcp_start":[0.52336,0.02679,0.21116],"tcp_to_object_dist_end":0.01908,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53044,0.03015,0.02563],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18408,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.151,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11291.0,"raw_peak_contact_force":0.21066,"tcp_end":[0.5163,0.02958,0.03426],"tcp_start":[0.52505,0.03015,0.0443],"tcp_to_object_dist_end":0.01658,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.53646,0.03055,0.13563],"object_pos_start":[0.53044,0.03015,0.02563],"object_to_goal_dist_end":0.16403,"object_to_goal_dist_start":0.18408,"object_z_max":0.13552,"peak_contact_force":0.07979,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27464.0,"raw_peak_contact_force":0.59507,"tcp_end":[0.52571,0.02987,0.15003],"tcp_start":[0.5163,0.02958,0.03426],"tcp_to_object_dist_end":0.01798,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":973.0,"n_steps_budget":1000.0,"object_pos_end":[0.59587,0.17362,0.11786],"object_pos_start":[0.53646,0.03055,0.13563],"object_to_goal_dist_end":0.01233,"object_to_goal_dist_start":0.16403,"object_z_max":0.16074,"peak_contact_force":0.0668,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37723.0,"raw_peak_contact_force":0.24699,"subtask_id":"transport_arc","tcp_end":[0.59439,0.1717,0.13825],"tcp_start":[0.52571,0.02987,0.15003],"tcp_to_object_dist_end":0.02054,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":241.0,"n_steps_budget":1000.0,"object_pos_end":[0.5976,0.17865,0.11469],"object_pos_start":[0.59587,0.17362,0.11786],"object_to_goal_dist_end":0.00768,"object_to_goal_dist_start":0.01233,"object_z_max":0.11786,"peak_contact_force":0.06714,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10845.0,"raw_peak_contact_force":0.2401,"subtask_id":"release_1","tcp_end":[0.59663,0.17676,0.13581],"tcp_start":[0.59439,0.1717,0.13825],"tcp_to_object_dist_end":0.02123,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57905,0.17279,0.02662],"object_pos_start":[0.5976,0.17865,0.11469],"object_to_goal_dist_end":0.08471,"object_to_goal_dist_start":0.00768,"object_z_max":0.11469,"peak_contact_force":0.13632,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":3034.0,"raw_peak_contact_force":1.19507,"tcp_end":[0.59038,0.17488,0.15692],"tcp_start":[0.59663,0.17676,0.13581],"tcp_to_object_dist_end":0.13081,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.57766,0.17275,0.02602],"object_pos_start":[0.57905,0.17279,0.02662],"object_to_goal_dist_end":0.08567,"object_to_goal_dist_start":0.08471,"object_z_max":0.02665,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3012.0,"raw_peak_contact_force":0.15647,"tcp_end":[0.58778,0.17407,0.27652],"tcp_start":[0.59038,0.17488,0.15692],"tcp_to_object_dist_end":0.25071,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```