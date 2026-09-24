## Search State

- **Seed**: 3
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0772 | 0.47 | ❌ rejected |
| 6 | approach → descend → grasp → lift → grasp → approach → descend → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | — | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 9 | 0.2272 | 0.77 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | 0.1426 | 0.46 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.1155 | 0.43 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | 0.2522 | 0.47 | ❌ rejected |

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

- **Composite score**: 0.077
- **task_score** (E): 0.467
- **fitness_score**: 0.707  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.630

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1174 |
| descend_1 | 1.00 | 1.00 | 0.1460 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 0.67 | 1.00 | 0.1343 |
| transport_1 | 0.33 | 1.00 | 0.1464 |
| descend_2 | 1.00 | 1.00 | 0.0801 |
| release_1 | 1.00 | 1.00 | 0.0213 |
| retract_1 | 1.00 | 1.00 | 0.0230 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.002, 0.191) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.507, 0.002, 0.191)→(0.506, 0.002, 0.045) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.002, 0.045)→(0.497, 0.002, 0.035) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 42.667 | 0.141 | 0.179 |
| lift_1 | lift | 0.67 / step_budget | (0.497, 0.002, 0.035)→(0.506, 0.002, 0.169) | (0.511, 0.002, 0.026)→(0.516, 0.002, 0.153) | 0.246→0.218 | 1.00 / 37.667 | 0.079 | 0.570 |
| transport_1 | approach | 0.33 / step_budget | (0.506, 0.002, 0.169)→(0.572, 0.111, 0.191) | (0.516, 0.002, 0.153)→(0.574, 0.112, 0.169) | 0.218→0.093 | 1.00 / 41.000 | 0.073 | 0.221 |
| descend_2 | descend | 1.00 / step_budget | (0.572, 0.111, 0.191)→(0.614, 0.170, 0.158) | (0.574, 0.112, 0.169)→(0.611, 0.170, 0.132) | 0.093→0.022 | 1.00 / 34.333 | 0.087 | 0.224 |
| release_1 | release | 1.00 / step_budget | (0.614, 0.170, 0.158)→(0.608, 0.168, 0.179) | (0.611, 0.170, 0.132)→(0.599, 0.166, 0.026) | 0.022→0.118 | 1.00 / 3.667 | 0.132 | 1.268 |
| retract_1 | retract | 1.00 / step_budget | (0.608, 0.168, 0.179)→(0.621, 0.179, 0.182) | (0.599, 0.166, 0.026)→(0.597, 0.165, 0.026) | 0.118→0.118 | 1.00 / 4.000 | 0.123 | 0.151 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.561
- phase_score: 0.603
- phase_breakdown.release_1_score: 0.400
- phase_breakdown.descend_1_score: 0.853
- phase_breakdown.transport_arc_score: 0.557
- phase_breakdown.approach_1_score: 0.033
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.754

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.754
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.561
- **Median Q (composite search score)**: 0.100
- **K-run variance**: 0.0026
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.345


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88235,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16247,"descend_1.grasp_z_offset":0.01033,"descend_2.fine_place_offset":0.0239,"lift_1.lift_height":0.13302,"release_1.release_duration":0.29472,"retract_1.retract_height":0.0426,"transport_1.arc_height":0.05024,"transport_1.transport_height_offset":0.01256,"transport_1.transport_speed":0.14957},"optimized_scores":{"best_composite_score":0.10002,"best_fitness_score":0.73002,"best_task_score":0.51333},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":303.0,"contact_point_centroid":[0.59586,0.17554,-0.00446],"force_p95":0.70421,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.24209,"mean_force":0.22327,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59732,0.17649,0.14982]},{"body_a":"world","body_b":"grasp_target","contact_count":135.0,"contact_point_centroid":[0.45641,-0.0252,-0.0011],"force_p95":0.29526,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50903,"mean_force":0.05724,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44498,-0.02564,0.03925]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13252.0,"contact_point_centroid":[0.44779,-0.04497,0.09632],"force_p95":0.07815,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28812,"mean_force":0.05289,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44828,-0.02579,0.09352]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14867.0,"contact_point_centroid":[0.44942,-0.00672,0.09382],"force_p95":0.07263,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28628,"mean_force":0.04826,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44814,-0.02578,0.09208]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18419.0,"contact_point_centroid":[0.5738,0.11692,0.15641],"force_p95":0.09164,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23739,"mean_force":0.05402,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.5703,0.13545,0.15695]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15688.0,"contact_point_centroid":[0.56632,0.1534,0.15859],"force_p95":0.10001,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22641,"mean_force":0.06173,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.5697,0.13467,0.15728]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":706.0,"contact_point_centroid":[0.59785,0.19641,0.13522],"force_p95":0.10836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19567,"mean_force":0.07053,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60159,0.17783,0.13672]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":785.0,"contact_point_centroid":[0.6061,0.16004,0.13209],"force_p95":0.09802,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19267,"mean_force":0.06578,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60155,0.17782,0.13666]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19283.0,"contact_point_centroid":[0.49803,0.01565,0.17377],"force_p95":0.0775,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17861,"mean_force":0.05099,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49631,0.03472,0.17158]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02638,-0.00205],"force_p95":0.13957,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17366,"mean_force":0.12673,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44727,-0.02571,0.03844]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19801.0,"contact_point_centroid":[0.49351,0.05046,0.17284],"force_p95":0.07353,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16837,"mean_force":0.04965,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.49385,0.03143,0.17042]},{"body_a":"world","body_b":"grasp_target","contact_count":1256.0,"contact_point_centroid":[0.45856,-0.02632,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48025,-0.0109,0.25131]},{"body_a":"world","body_b":"grasp_target","contact_count":1716.0,"contact_point_centroid":[0.59588,0.17549,-0.00198],"force_p95":0.1257,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12993,"mean_force":0.12255,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61088,0.19193,0.15152]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5309.0,"contact_point_centroid":[0.44705,-0.00657,0.03875],"force_p95":0.06846,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12724,"mean_force":0.04134,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44611,-0.02568,0.03733]},{"body_a":"world","body_b":"grasp_target","contact_count":1992.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4562,-0.02433,0.12261]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4407.0,"contact_point_centroid":[0.44548,-0.04494,0.0401],"force_p95":0.0795,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08938,"mean_force":0.04916,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44611,-0.02568,0.03733]}],"total_contact_groups":16},"final_pose_error":0.0114,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.59589,0.17549,0.02602],"final_tcp_position":[0.62337,0.20435,0.14839],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.24209,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":315.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1256.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.4606,-0.02285,0.20131],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17534,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":498.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1992.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45421,-0.0259,0.04515],"tcp_start":[0.4606,-0.02285,0.20131],"tcp_to_object_dist_end":0.01962,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45847,-0.02615,0.02581],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30363,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13948,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11516.0,"raw_peak_contact_force":0.17366,"tcp_end":[0.44608,-0.02567,0.0373],"tcp_start":[0.45421,-0.0259,0.04515],"tcp_to_object_dist_end":0.01691,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.46375,-0.02659,0.13078],"object_pos_start":[0.45847,-0.02615,0.02581],"object_to_goal_dist_end":0.28826,"object_to_goal_dist_start":0.30363,"object_z_max":0.13066,"peak_contact_force":0.07763,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28254.0,"raw_peak_contact_force":0.50903,"tcp_end":[0.454,-0.026,0.1475],"tcp_start":[0.44608,-0.02567,0.0373],"tcp_to_object_dist_end":0.01936,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53907,0.08958,0.15976],"object_pos_start":[0.46375,-0.02659,0.13078],"object_to_goal_dist_end":0.15636,"object_to_goal_dist_start":0.28826,"object_z_max":0.16062,"peak_contact_force":0.06857,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":39084.0,"raw_peak_contact_force":0.17861,"subtask_id":"transport_arc","tcp_end":[0.53687,0.08864,0.18095],"tcp_start":[0.454,-0.026,0.1475],"tcp_to_object_dist_end":0.02132,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60008,0.17906,0.11135],"object_pos_start":[0.53907,0.08958,0.15976],"object_to_goal_dist_end":0.04196,"object_to_goal_dist_start":0.15636,"object_z_max":0.15976,"peak_contact_force":0.10955,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":34107.0,"raw_peak_contact_force":0.23739,"subtask_id":"release_1","tcp_end":[0.60345,0.17828,0.14017],"tcp_start":[0.53687,0.08864,0.18095],"tcp_to_object_dist_end":0.02902,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59572,0.17541,0.02643],"object_pos_start":[0.60008,0.17906,0.11135],"object_to_goal_dist_end":0.09975,"object_to_goal_dist_start":0.04196,"object_z_max":0.11135,"peak_contact_force":0.11922,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1794.0,"raw_peak_contact_force":1.24209,"tcp_end":[0.59722,0.17646,0.16101],"tcp_start":[0.60345,0.17828,0.14017],"tcp_to_object_dist_end":0.13459,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":429.0,"n_steps_budget":600.0,"object_pos_end":[0.59589,0.17549,0.02602],"object_pos_start":[0.59572,0.17541,0.02643],"object_to_goal_dist_end":0.10003,"object_to_goal_dist_start":0.09975,"object_z_max":0.02644,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1716.0,"raw_peak_contact_force":0.12993,"tcp_end":[0.62337,0.20435,0.14839],"tcp_start":[0.59722,0.17646,0.16101],"tcp_to_object_dist_end":0.1287,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86928,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13388,"descend_1.grasp_z_offset":0.01037,"descend_2.fine_place_offset":0.02047,"lift_1.lift_height":0.15311,"release_1.release_duration":0.39928,"retract_1.retract_height":0.06307,"transport_1.arc_height":0.13092,"transport_1.transport_height_offset":0.02413,"transport_1.transport_speed":0.12148},"optimized_scores":{"best_composite_score":0.00716,"best_fitness_score":0.63716,"best_task_score":0.32688},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":217.0,"contact_point_centroid":[0.62032,0.14907,-0.00666],"force_p95":1.19408,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.48241,"mean_force":0.33865,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.637,0.15334,0.21492]},{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.54108,0.00081,-0.00112],"force_p95":0.46518,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59377,"mean_force":0.09003,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52844,0.0008,0.03571]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15015.0,"contact_point_centroid":[0.53365,0.01999,0.10226],"force_p95":0.08023,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33827,"mean_force":0.0567,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53256,0.00086,0.09996]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16476.0,"contact_point_centroid":[0.53321,-0.01816,0.09855],"force_p95":0.07676,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31632,"mean_force":0.05234,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53222,0.00086,0.09646]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16761.0,"contact_point_centroid":[0.55676,0.00787,0.22039],"force_p95":0.08715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20923,"mean_force":0.05863,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5543,0.02673,0.21916]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16800.0,"contact_point_centroid":[0.61811,0.09769,0.22467],"force_p95":0.07214,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20389,"mean_force":0.04891,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61517,0.1166,0.22436]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15817.0,"contact_point_centroid":[0.61257,0.13611,0.22607],"force_p95":0.07256,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19759,"mean_force":0.0509,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61568,0.11733,0.22395]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16686.0,"contact_point_centroid":[0.55446,0.04447,0.21931],"force_p95":0.08565,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17427,"mean_force":0.05843,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55342,0.02549,0.21795]},{"body_a":"world","body_b":"grasp_target","contact_count":1579.0,"contact_point_centroid":[0.61973,0.14852,-0.00197],"force_p95":0.14528,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16702,"mean_force":0.1217,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.64001,0.1552,0.23261]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1162.0,"contact_point_centroid":[0.63498,0.17271,0.20105],"force_p95":0.07162,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15707,"mean_force":0.04441,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64066,0.15439,0.2003]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00116,-0.00203],"force_p95":0.13333,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1537,"mean_force":0.12534,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53096,0.00086,0.03555]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1179.0,"contact_point_centroid":[0.64306,0.13533,0.19884],"force_p95":0.07134,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14806,"mean_force":0.04455,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64063,0.15438,0.20025]},{"body_a":"world","body_b":"grasp_target","contact_count":1796.0,"contact_point_centroid":[0.54431,0.00113,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51697,0.00047,0.23428]},{"body_a":"world","body_b":"grasp_target","contact_count":1516.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53616,0.00097,0.10663]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.53086,-0.01822,0.03573],"force_p95":0.06859,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10203,"mean_force":0.04467,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52969,0.00083,0.03407]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4149.0,"contact_point_centroid":[0.53093,0.02005,0.03663],"force_p95":0.07521,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09575,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52969,0.00083,0.03407]}],"total_contact_groups":16},"final_pose_error":0.01203,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.61962,0.14839,0.02602],"final_tcp_position":[0.6437,0.15689,0.24286],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.48241,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":450.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1796.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53652,0.00097,0.1699],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14409,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":379.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1516.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53853,0.00101,0.04449],"tcp_start":[0.53652,0.00097,0.1699],"tcp_to_object_dist_end":0.01936,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54418,0.00106,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25032,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13336,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10789.0,"raw_peak_contact_force":0.1537,"tcp_end":[0.52966,0.00083,0.03403],"tcp_start":[0.53853,0.00101,0.04449],"tcp_to_object_dist_end":0.01666,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.5499,0.00103,0.1514],"object_pos_start":[0.54418,0.00106,0.02587],"object_to_goal_dist_end":0.18918,"object_to_goal_dist_start":0.25032,"object_z_max":0.15129,"peak_contact_force":0.07975,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":31636.0,"raw_peak_contact_force":0.59377,"tcp_end":[0.53965,0.00098,0.16614],"tcp_start":[0.52966,0.00083,0.03403],"tcp_to_object_dist_end":0.01795,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58904,0.07023,0.23448],"object_pos_start":[0.5499,0.00103,0.1514],"object_to_goal_dist_end":0.11416,"object_to_goal_dist_start":0.18918,"object_z_max":0.23447,"peak_contact_force":0.07568,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33447.0,"raw_peak_contact_force":0.20923,"subtask_id":"transport_arc","tcp_end":[0.58367,0.06907,0.2561],"tcp_start":[0.53965,0.00098,0.16614],"tcp_to_object_dist_end":0.0223,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":805.0,"n_steps_budget":1000.0,"object_pos_end":[0.63745,0.15511,0.17588],"object_pos_start":[0.58904,0.07023,0.23448],"object_to_goal_dist_end":0.01855,"object_to_goal_dist_start":0.11416,"object_z_max":0.23448,"peak_contact_force":0.07195,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":32617.0,"raw_peak_contact_force":0.20389,"subtask_id":"release_1","tcp_end":[0.64217,0.15467,0.20392],"tcp_start":[0.58367,0.06907,0.2561],"tcp_to_object_dist_end":0.02844,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62567,0.15041,0.02471],"object_pos_start":[0.63745,0.15511,0.17588],"object_to_goal_dist_end":0.16801,"object_to_goal_dist_start":0.01855,"object_z_max":0.17588,"peak_contact_force":0.13587,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2558.0,"raw_peak_contact_force":1.48241,"tcp_end":[0.63696,0.15333,0.22351],"tcp_start":[0.64217,0.15467,0.20392],"tcp_to_object_dist_end":0.19914,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":397.0,"n_steps_budget":600.0,"object_pos_end":[0.61962,0.14839,0.02602],"object_pos_start":[0.62567,0.15041,0.02471],"object_to_goal_dist_end":0.16772,"object_to_goal_dist_start":0.16801,"object_z_max":0.02678,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1579.0,"raw_peak_contact_force":0.16702,"tcp_end":[0.6437,0.15689,0.24286],"tcp_start":[0.63696,0.15333,0.22351],"tcp_to_object_dist_end":0.21834,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51282,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16442,"descend_1.grasp_z_offset":0.01014,"descend_2.fine_place_offset":0.01566,"lift_1.lift_height":0.21891,"release_1.release_duration":0.37543,"retract_1.retract_height":0.05605,"transport_1.arc_height":0.123,"transport_1.transport_height_offset":0.02088,"transport_1.transport_speed":0.1882},"optimized_scores":{"best_composite_score":0.12441,"best_fitness_score":0.75441,"best_task_score":0.56113},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":307.0,"contact_point_centroid":[0.57527,0.1715,-0.00405],"force_p95":0.92458,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.08009,"mean_force":0.23686,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58929,0.1738,0.1406]},{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.52746,0.02906,-0.0012],"force_p95":0.41254,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60603,"mean_force":0.08307,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51487,0.02948,0.03606]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.51839,0.04873,0.11548],"force_p95":0.0823,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34121,"mean_force":0.05883,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5178,0.02954,0.11273]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20447.0,"contact_point_centroid":[0.51953,0.0106,0.113],"force_p95":0.07765,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31488,"mean_force":0.05034,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51771,0.02954,0.11136]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19769.0,"contact_point_centroid":[0.5649,0.08838,0.20368],"force_p95":0.07476,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27366,"mean_force":0.04869,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56124,0.10701,0.2027]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1161.0,"contact_point_centroid":[0.58956,0.19376,0.13113],"force_p95":0.07531,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25999,"mean_force":0.04583,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59365,0.17514,0.12742]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1402.0,"contact_point_centroid":[0.59795,0.15635,0.128],"force_p95":0.07101,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24297,"mean_force":0.03951,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59365,0.17514,0.12743]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":418.0,"contact_point_centroid":[0.59163,0.19408,0.13783],"force_p95":0.08278,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22975,"mean_force":0.05726,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59576,0.17553,0.13417]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16289.0,"contact_point_centroid":[0.55979,0.12658,0.20491],"force_p95":0.09137,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22454,"mean_force":0.05933,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56153,0.10756,0.20193]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":506.0,"contact_point_centroid":[0.59994,0.15675,0.13486],"force_p95":0.07861,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21687,"mean_force":0.0492,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59576,0.17553,0.13417]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03077,-0.0021],"force_p95":0.15261,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21049,"mean_force":0.13051,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51756,0.02967,0.03567]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5277.0,"contact_point_centroid":[0.51741,0.01055,0.0362],"force_p95":0.06756,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16924,"mean_force":0.0411,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5163,0.02958,0.03425]},{"body_a":"world","body_b":"grasp_target","contact_count":1032.0,"contact_point_centroid":[0.57463,0.17142,-0.00196],"force_p95":0.14608,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15613,"mean_force":0.12261,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.59296,0.17557,0.15265]},{"body_a":"world","body_b":"grasp_target","contact_count":1408.0,"contact_point_centroid":[0.5305,0.03079,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51061,0.01321,0.2498]},{"body_a":"world","body_b":"grasp_target","contact_count":1896.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52299,0.02855,0.12165]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4213.0,"contact_point_centroid":[0.51686,0.0489,0.03707],"force_p95":0.08168,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08428,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51631,0.02958,0.03426]}],"total_contact_groups":16},"final_pose_error":0.01097,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5746,0.17141,0.02602],"final_tcp_position":[0.59606,0.17685,0.15479],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.08009,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":353.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1408.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52358,0.02711,0.20039],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17455,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":474.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1896.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52503,0.03016,0.04425],"tcp_start":[0.52358,0.02711,0.20039],"tcp_to_object_dist_end":0.01905,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53044,0.03016,0.02563],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18407,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15088,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11290.0,"raw_peak_contact_force":0.21049,"tcp_end":[0.51628,0.02958,0.03422],"tcp_start":[0.52503,0.03016,0.04425],"tcp_to_object_dist_end":0.01657,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5331,0.03049,0.17736],"object_pos_start":[0.53044,0.03016,0.02563],"object_to_goal_dist_end":0.17723,"object_to_goal_dist_start":0.18407,"object_z_max":0.17718,"peak_contact_force":0.08109,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37595.0,"raw_peak_contact_force":0.60603,"tcp_end":[0.52379,0.0298,0.19396],"tcp_start":[0.51628,0.02958,0.03422],"tcp_to_object_dist_end":0.01905,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":935.0,"n_steps_budget":1000.0,"object_pos_end":[0.5949,0.1767,0.11398],"object_pos_start":[0.5331,0.03049,0.17736],"object_to_goal_dist_end":0.00907,"object_to_goal_dist_start":0.17723,"object_z_max":0.20293,"peak_contact_force":0.07622,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36058.0,"raw_peak_contact_force":0.27366,"subtask_id":"transport_arc","tcp_end":[0.59645,0.17559,0.13676],"tcp_start":[0.52379,0.0298,0.19396],"tcp_to_object_dist_end":0.02286,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":22.0,"n_steps_budget":1000.0,"object_pos_end":[0.59496,0.17711,0.10845],"object_pos_start":[0.5949,0.1767,0.11398],"object_to_goal_dist_end":0.00675,"object_to_goal_dist_start":0.00907,"object_z_max":0.11398,"peak_contact_force":0.0786,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":924.0,"raw_peak_contact_force":0.22975,"subtask_id":"release_1","tcp_end":[0.59577,0.17572,0.1313],"tcp_start":[0.59645,0.17559,0.13676],"tcp_to_object_dist_end":0.02291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57568,0.17148,0.02662],"object_pos_start":[0.59496,0.17711,0.10845],"object_to_goal_dist_end":0.08577,"object_to_goal_dist_start":0.00675,"object_z_max":0.10845,"peak_contact_force":0.14094,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2870.0,"raw_peak_contact_force":1.08009,"tcp_end":[0.58918,0.17376,0.15197],"tcp_start":[0.59577,0.17572,0.1313],"tcp_to_object_dist_end":0.12609,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":258.0,"n_steps_budget":600.0,"object_pos_end":[0.5746,0.17141,0.02602],"object_pos_start":[0.57568,0.17148,0.02662],"object_to_goal_dist_end":0.08667,"object_to_goal_dist_start":0.08577,"object_z_max":0.02662,"peak_contact_force":0.12265,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1032.0,"raw_peak_contact_force":0.15613,"tcp_end":[0.59606,0.17685,0.15479],"tcp_start":[0.58918,0.17376,0.15197],"tcp_to_object_dist_end":0.13066,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```