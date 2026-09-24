## Search State

- **Seed**: 3
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | 0.2522 | 0.47 | ❌ rejected |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | 0.1848 | 0.48 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | 0.1851 | 0.48 | ❌ rejected |
| 0 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7 | 0.0374 | 0.17 | ✅ accepted |

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

## Current Skill (Q=0.252) — your mutation base

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
    - 0.15
  parameters:
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
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
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
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: duration.max_time
        mode: add
- id: retract_1
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
    - 0.15
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
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
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15]
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03]
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (add)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15]
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.252
- **task_score** (E): 0.467
- **fitness_score**: 0.707  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1442 |
| descend_1 | 1.00 | 1.00 | 0.1185 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 0.33 | 1.00 | 0.1491 |
| transport_1 | 1.00 | 1.00 | 0.2136 |
| descend_2 | 1.00 | 1.00 | 0.0179 |
| release_1 | 1.00 | 1.00 | 0.0208 |
| retract_1 | 1.00 | 1.00 | 0.0387 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.002, 0.163) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.507, 0.002, 0.163)→(0.506, 0.002, 0.044) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.002, 0.044)→(0.497, 0.002, 0.035) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 42.667 | 0.142 | 0.180 |
| lift_1 | lift | 0.33 / step_budget | (0.497, 0.002, 0.035)→(0.505, 0.002, 0.184) | (0.511, 0.002, 0.026)→(0.515, 0.002, 0.167) | 0.246→0.222 | 1.00 / 35.667 | 0.093 | 0.575 |
| transport_1 | approach | 1.00 / step_budget | (0.505, 0.002, 0.184)→(0.607, 0.156, 0.276) | (0.515, 0.002, 0.167)→(0.609, 0.157, 0.251) | 0.222→0.118 | 1.00 / 36.000 | 0.087 | 0.289 |
| descend_2 | descend | 1.00 / force_exceeded | (0.607, 0.156, 0.276)→(0.606, 0.157, 0.258) | (0.609, 0.157, 0.251)→(0.608, 0.159, 0.232) | 0.118→0.100 | 1.00 / 34.667 | 700.012 | 0.261 |
| release_1 | release | 1.00 / step_budget | (0.606, 0.157, 0.258)→(0.602, 0.156, 0.278) | (0.608, 0.159, 0.232)→(0.602, 0.154, 0.013) | 0.100→0.132 | 1.00 / 2.667 | 0.317 | 1.885 |
| retract_1 | retract | 1.00 / step_budget | (0.602, 0.156, 0.278)→(0.621, 0.178, 0.280) | (0.602, 0.154, 0.013)→(0.611, 0.160, 0.023) | 0.132→0.119 | 1.00 / 3.333 | 0.168 | 0.371 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.576
- phase_score: 0.280
- phase_breakdown.release_1_score: 0.041
- phase_breakdown.descend_1_score: 0.845
- phase_breakdown.transport_arc_score: 0.057
- phase_breakdown.approach_1_score: 0.163
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.762

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.762
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.576
- **Median Q (composite search score)**: 0.277
- **K-run variance**: 0.0033
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.334


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.97826,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15761,"descend_1.grasp_z_offset":0.01019,"descend_2.descend_distance":0.19049,"descend_2.place_force_threshold":5.83305,"lift_1.lift_height":0.23337,"release_1.release_duration":0.23714,"retract_1.retract_speed":0.22859,"transport_1.transport_speed":0.36274},"optimized_scores":{"best_composite_score":0.27674,"best_fitness_score":0.73174,"best_task_score":0.51652},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":152.0,"contact_point_centroid":[0.59817,0.17634,-0.00953],"force_p95":1.29068,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.10304,"mean_force":0.49817,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59879,0.17461,0.27403]},{"body_a":"world","body_b":"grasp_target","contact_count":128.0,"contact_point_centroid":[0.45577,-0.02527,-0.00111],"force_p95":0.30506,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.52126,"mean_force":0.06701,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44485,-0.02564,0.03904]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18742.0,"contact_point_centroid":[0.5245,0.05083,0.24404],"force_p95":0.08633,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3848,"mean_force":0.05398,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52234,0.06974,0.24292]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18124.0,"contact_point_centroid":[0.5161,0.08246,0.2422],"force_p95":0.08517,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33747,"mean_force":0.05479,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.51762,0.06354,0.24053]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.59957,0.19438,0.25873],"force_p95":0.25162,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31081,"mean_force":0.10446,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60303,0.1758,0.26039]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18315.0,"contact_point_centroid":[0.44672,-0.04491,0.11956],"force_p95":0.07895,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29307,"mean_force":0.05476,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4469,-0.02573,0.1168]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21124.0,"contact_point_centroid":[0.44836,-0.00671,0.11839],"force_p95":0.07308,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29249,"mean_force":0.04867,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44691,-0.02573,0.11666]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":663.0,"contact_point_centroid":[0.59757,0.19418,0.25376],"force_p95":0.11603,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27858,"mean_force":0.07628,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60147,0.17555,0.2555]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":91.0,"contact_point_centroid":[0.60858,0.15819,0.25641],"force_p95":0.19192,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26194,"mean_force":0.08999,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.60303,0.1758,0.26039]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":834.0,"contact_point_centroid":[0.60688,0.15797,0.25144],"force_p95":0.09333,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2617,"mean_force":0.06225,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60151,0.17557,0.25559]},{"body_a":"world","body_b":"grasp_target","contact_count":1392.0,"contact_point_centroid":[0.59796,0.17624,-0.00207],"force_p95":0.13301,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18636,"mean_force":0.11733,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61284,0.19138,0.26472]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02638,-0.00205],"force_p95":0.13958,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17367,"mean_force":0.12673,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44726,-0.02571,0.0383]},{"body_a":"world","body_b":"grasp_target","contact_count":1308.0,"contact_point_centroid":[0.45856,-0.02632,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48014,-0.01095,0.24904]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5309.0,"contact_point_centroid":[0.44703,-0.00657,0.03862],"force_p95":0.06845,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12708,"mean_force":0.04134,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4461,-0.02567,0.03719]},{"body_a":"world","body_b":"grasp_target","contact_count":1936.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45607,-0.02438,0.12019]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4407.0,"contact_point_centroid":[0.44547,-0.04494,0.03996],"force_p95":0.07949,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08944,"mean_force":0.04917,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4461,-0.02567,0.03719]}],"total_contact_groups":16},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.59795,0.17623,0.02602],"final_tcp_position":[0.62453,0.20433,0.2568],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1573.09317,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":328.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1308.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46041,-0.02295,0.19668],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1707,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":484.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1936.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45419,-0.0259,0.04501],"tcp_start":[0.46041,-0.02295,0.19668],"tcp_to_object_dist_end":0.01949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45847,-0.02615,0.02581],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30363,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13949,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11516.0,"raw_peak_contact_force":0.17367,"tcp_end":[0.44607,-0.02567,0.03716],"tcp_start":[0.45419,-0.0259,0.04501],"tcp_to_object_dist_end":0.01682,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4604,-0.02656,0.18084],"object_pos_start":[0.45847,-0.02615,0.02581],"object_to_goal_dist_end":0.29728,"object_to_goal_dist_start":0.30363,"object_z_max":0.18065,"peak_contact_force":0.08215,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39567.0,"raw_peak_contact_force":0.52126,"tcp_end":[0.45196,-0.02591,0.1996],"tcp_start":[0.44607,-0.02567,0.03716],"tcp_to_object_dist_end":0.02059,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59829,0.17574,0.23151],"object_pos_start":[0.4604,-0.02656,0.18084],"object_to_goal_dist_end":0.12589,"object_to_goal_dist_start":0.29728,"object_z_max":0.23701,"peak_contact_force":0.1073,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36866.0,"raw_peak_contact_force":0.3848,"subtask_id":"transport_arc","tcp_end":[0.60307,0.17563,0.26078],"tcp_start":[0.45196,-0.02591,0.1996],"tcp_to_object_dist_end":0.02966,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.59846,0.17618,0.23009],"object_pos_start":[0.59829,0.17574,0.23151],"object_to_goal_dist_end":0.12441,"object_to_goal_dist_start":0.12589,"object_z_max":0.23151,"peak_contact_force":1573.09317,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":175.0,"raw_peak_contact_force":0.31081,"tcp_end":[0.60298,0.17596,0.25956],"tcp_start":[0.60307,0.17563,0.26078],"tcp_to_object_dist_end":0.02981,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59354,0.17202,0.01644],"object_pos_start":[0.59846,0.17618,0.23009],"object_to_goal_dist_end":0.1104,"object_to_goal_dist_start":0.12441,"object_z_max":0.23009,"peak_contact_force":0.19659,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1649.0,"raw_peak_contact_force":2.10304,"tcp_end":[0.59876,0.17461,0.27993],"tcp_start":[0.60298,0.17596,0.25956],"tcp_to_object_dist_end":0.26355,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":348.0,"n_steps_budget":600.0,"object_pos_end":[0.59795,0.17623,0.02602],"object_pos_start":[0.59354,0.17202,0.01644],"object_to_goal_dist_end":0.0991,"object_to_goal_dist_start":0.1104,"object_z_max":0.0269,"peak_contact_force":0.12265,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1392.0,"raw_peak_contact_force":0.18636,"tcp_end":[0.62453,0.20433,0.2568],"tcp_start":[0.59876,0.17461,0.27993],"tcp_to_object_dist_end":0.234,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92029,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13524,"descend_1.grasp_z_offset":0.01005,"descend_2.descend_distance":0.14128,"descend_2.place_force_threshold":16.10701,"lift_1.lift_height":0.14425,"release_1.release_duration":0.23116,"retract_1.retract_speed":0.31313,"transport_1.transport_speed":0.29538},"optimized_scores":{"best_composite_score":0.17333,"best_fitness_score":0.62833,"best_task_score":0.30877},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.62233,0.13261,-0.01505],"force_p95":1.7678,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.83682,"mean_force":1.02537,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62238,0.13187,0.28271]},{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.54108,0.00081,-0.0011],"force_p95":0.46878,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59717,"mean_force":0.08857,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52846,0.0008,0.03543]},{"body_a":"world","body_b":"grasp_target","contact_count":1730.0,"contact_point_centroid":[0.64546,0.1371,-0.00236],"force_p95":0.2135,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57357,"mean_force":0.13283,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.6338,0.14536,0.30885]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13938.0,"contact_point_centroid":[0.53362,0.01999,0.09765],"force_p95":0.08045,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33789,"mean_force":0.05683,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53253,0.00086,0.09535]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15333.0,"contact_point_centroid":[0.53316,-0.01817,0.09402],"force_p95":0.07673,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31605,"mean_force":0.05234,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53218,0.00086,0.09193]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18213.0,"contact_point_centroid":[0.5796,0.04003,0.24544],"force_p95":0.08609,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23793,"mean_force":0.05589,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57673,0.05883,0.24421]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3841.0,"contact_point_centroid":[0.6226,0.14976,0.29518],"force_p95":0.06833,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22571,"mean_force":0.0462,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62564,0.13091,0.29234]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17796.0,"contact_point_centroid":[0.57438,0.07481,0.24256],"force_p95":0.08395,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21658,"mean_force":0.05663,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.57464,0.05585,0.24068]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1222.0,"contact_point_centroid":[0.62264,0.1516,0.26859],"force_p95":0.06823,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21594,"mean_force":0.04341,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62511,0.13261,0.2649]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1399.0,"contact_point_centroid":[0.62914,0.11375,0.26576],"force_p95":0.06452,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20099,"mean_force":0.03893,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62511,0.13261,0.26489]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3727.0,"contact_point_centroid":[0.62912,0.1119,0.2947],"force_p95":0.07024,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17313,"mean_force":0.0481,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.62563,0.13082,0.29368]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00116,-0.00203],"force_p95":0.13333,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15365,"mean_force":0.12533,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53097,0.00086,0.03525]},{"body_a":"world","body_b":"grasp_target","contact_count":1784.0,"contact_point_centroid":[0.54431,0.00113,-0.00192],"force_p95":0.1336,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1229,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51694,0.00047,0.23506]},{"body_a":"world","body_b":"grasp_target","contact_count":1540.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53616,0.00097,0.10711]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.53087,-0.01822,0.03544],"force_p95":0.06859,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1019,"mean_force":0.04467,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5297,0.00083,0.03377]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4149.0,"contact_point_centroid":[0.53093,0.02005,0.03633],"force_p95":0.07521,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09579,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5297,0.00083,0.03377]}],"total_contact_groups":16},"final_pose_error":0.01358,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64891,0.13766,0.01602],"final_tcp_position":[0.64368,0.15553,0.32837],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":227.25093,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":447.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1784.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53651,0.00097,0.17119],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14538,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":385.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1540.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53855,0.00101,0.0442],"tcp_start":[0.53651,0.00097,0.17119],"tcp_to_object_dist_end":0.01907,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54418,0.00106,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25032,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13337,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10789.0,"raw_peak_contact_force":0.15365,"tcp_end":[0.52967,0.00083,0.03373],"tcp_start":[0.53855,0.00101,0.0442],"tcp_to_object_dist_end":0.01651,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.55013,0.00103,0.14318],"object_pos_start":[0.54418,0.00106,0.02587],"object_to_goal_dist_end":0.19097,"object_to_goal_dist_start":0.25032,"object_z_max":0.14306,"peak_contact_force":0.07981,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29416.0,"raw_peak_contact_force":0.59717,"tcp_end":[0.53951,0.00098,0.15723],"tcp_start":[0.52967,0.00083,0.03373],"tcp_to_object_dist_end":0.01762,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63145,0.13105,0.29487],"object_pos_start":[0.55013,0.00103,0.14318],"object_to_goal_dist_end":0.10844,"object_to_goal_dist_start":0.19097,"object_z_max":0.2948,"peak_contact_force":0.06832,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36009.0,"raw_peak_contact_force":0.23793,"subtask_id":"transport_arc","tcp_end":[0.62593,0.1292,0.31678],"tcp_start":[0.53951,0.00098,0.15723],"tcp_to_object_dist_end":0.02268,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":176.0,"n_steps_budget":1000.0,"object_pos_end":[0.63053,0.1345,0.24581],"object_pos_start":[0.63145,0.13105,0.29487],"object_to_goal_dist_end":0.06197,"object_to_goal_dist_start":0.10844,"object_z_max":0.29487,"peak_contact_force":227.25093,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7568.0,"raw_peak_contact_force":0.22571,"tcp_end":[0.62651,0.13289,0.26896],"tcp_start":[0.62593,0.1292,0.31678],"tcp_to_object_dist_end":0.02355,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62383,0.13009,0.00842],"object_pos_start":[0.63053,0.1345,0.24581],"object_to_goal_dist_end":0.18634,"object_to_goal_dist_start":0.06197,"object_z_max":0.24581,"peak_contact_force":0.38515,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2699.0,"raw_peak_contact_force":1.83682,"tcp_end":[0.62236,0.13187,0.28875],"tcp_start":[0.62651,0.13289,0.26896],"tcp_to_object_dist_end":0.28034,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.64891,0.13766,0.01602],"object_pos_start":[0.62383,0.13009,0.00842],"object_to_goal_dist_end":0.17628,"object_to_goal_dist_start":0.18634,"object_z_max":0.03044,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1730.0,"raw_peak_contact_force":0.57357,"tcp_end":[0.64368,0.15553,0.32837],"tcp_start":[0.62236,0.13187,0.28875],"tcp_to_object_dist_end":0.3129,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79137,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08354,"descend_1.grasp_z_offset":0.01002,"descend_2.descend_distance":0.21774,"descend_2.place_force_threshold":12.07753,"lift_1.lift_height":0.23976,"release_1.release_duration":0.40211,"retract_1.retract_speed":0.45172,"transport_1.transport_speed":0.41223},"optimized_scores":{"best_composite_score":0.30668,"best_fitness_score":0.76168,"best_task_score":0.5764},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":87.0,"contact_point_centroid":[0.58654,0.16414,-0.01363],"force_p95":1.62406,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.71442,"mean_force":0.89484,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58551,0.16182,0.25977]},{"body_a":"world","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.52731,0.02887,-0.0012],"force_p95":0.4182,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60688,"mean_force":0.08426,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51447,0.0294,0.03588]},{"body_a":"world","body_b":"grasp_target","contact_count":224.0,"contact_point_centroid":[0.58609,0.16527,-0.00426],"force_p95":0.27152,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35273,"mean_force":0.20321,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58991,0.16749,0.2594]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16547.0,"contact_point_centroid":[0.51808,0.04865,0.11243],"force_p95":0.1131,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34152,"mean_force":0.06409,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51689,0.02945,0.11043]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20323.0,"contact_point_centroid":[0.51898,0.01085,0.11359],"force_p95":0.08517,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31587,"mean_force":0.05007,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51702,0.02945,0.11201]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":323.0,"contact_point_centroid":[0.58879,0.18242,0.2517],"force_p95":0.11804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24749,"mean_force":0.06754,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59042,0.16321,0.24825]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19144.0,"contact_point_centroid":[0.55981,0.07866,0.2313],"force_p95":0.08938,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24442,"mean_force":0.05285,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5555,0.09676,0.23057]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13267.0,"contact_point_centroid":[0.55646,0.11704,0.23303],"force_p95":0.11746,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23273,"mean_force":0.0773,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55604,0.09777,0.2309]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53055,0.03076,-0.00211],"force_p95":0.15401,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21244,"mean_force":0.13087,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51717,0.02959,0.03548]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":437.0,"contact_point_centroid":[0.59545,0.14482,0.24871],"force_p95":0.09286,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18135,"mean_force":0.05082,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59042,0.16321,0.24825]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5273.0,"contact_point_centroid":[0.51713,0.01049,0.03611],"force_p95":0.06707,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16758,"mean_force":0.04108,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51592,0.02951,0.03406]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":949.0,"contact_point_centroid":[0.58658,0.18203,0.24415],"force_p95":0.09289,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16397,"mean_force":0.05432,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58845,0.16275,0.24183]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1340.0,"contact_point_centroid":[0.59348,0.14442,0.24191],"force_p95":0.07832,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15569,"mean_force":0.03973,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58848,0.16275,0.24188]},{"body_a":"world","body_b":"grasp_target","contact_count":2336.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51087,0.01398,0.20974]},{"body_a":"world","body_b":"grasp_target","contact_count":956.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52315,0.02915,0.08205]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4220.0,"contact_point_centroid":[0.51661,0.04884,0.03684],"force_p95":0.08129,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08433,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51592,0.02951,0.03406]}],"total_contact_groups":16},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58709,0.16495,0.02787],"final_tcp_position":[0.59458,0.17327,0.25337],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":299.69321,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":585.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2336.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52416,0.02839,0.12059],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09481,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":239.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":956.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52463,0.03008,0.04404],"tcp_start":[0.52416,0.02839,0.12059],"tcp_to_object_dist_end":0.01897,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53044,0.0301,0.02561],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18413,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.15195,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11293.0,"raw_peak_contact_force":0.21244,"tcp_end":[0.51589,0.02951,0.03402],"tcp_start":[0.52463,0.03008,0.04404],"tcp_to_object_dist_end":0.01682,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53327,0.03004,0.17745],"object_pos_start":[0.53044,0.0301,0.02561],"object_to_goal_dist_end":0.17758,"object_to_goal_dist_start":0.18413,"object_z_max":0.17726,"peak_contact_force":0.11668,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37017.0,"raw_peak_contact_force":0.60688,"tcp_end":[0.52274,0.0297,0.19484],"tcp_start":[0.51589,0.02951,0.03402],"tcp_to_object_dist_end":0.02033,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59646,0.16481,0.22623],"object_pos_start":[0.53327,0.03004,0.17745],"object_to_goal_dist_end":0.11905,"object_to_goal_dist_start":0.17758,"object_z_max":0.22632,"peak_contact_force":0.08614,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32411.0,"raw_peak_contact_force":0.24442,"subtask_id":"transport_arc","tcp_end":[0.59069,0.16295,0.25007],"tcp_start":[0.52274,0.0297,0.19484],"tcp_to_object_dist_end":0.0246,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":19.0,"n_steps_budget":1000.0,"object_pos_end":[0.5953,0.16502,0.22125],"object_pos_start":[0.59646,0.16481,0.22623],"object_to_goal_dist_end":0.11414,"object_to_goal_dist_start":0.11905,"object_z_max":0.22623,"peak_contact_force":299.69321,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":760.0,"raw_peak_contact_force":0.24749,"tcp_end":[0.58997,0.1632,0.24557],"tcp_start":[0.59069,0.16295,0.25007],"tcp_to_object_dist_end":0.02496,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58833,0.15901,0.01298],"object_pos_start":[0.5953,0.16502,0.22125],"object_to_goal_dist_end":0.098,"object_to_goal_dist_start":0.11414,"object_z_max":0.22125,"peak_contact_force":0.36918,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2376.0,"raw_peak_contact_force":1.71442,"tcp_end":[0.58547,0.16181,0.26648],"tcp_start":[0.58997,0.1632,0.24557],"tcp_to_object_dist_end":0.25353,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":112.0,"n_steps_budget":600.0,"object_pos_end":[0.58709,0.16495,0.02787],"object_pos_start":[0.58833,0.15901,0.01298],"object_to_goal_dist_end":0.08264,"object_to_goal_dist_start":0.098,"object_z_max":0.03038,"peak_contact_force":0.25749,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":224.0,"raw_peak_contact_force":0.35273,"tcp_end":[0.59458,0.17327,0.25337],"tcp_start":[0.58547,0.16181,0.26648],"tcp_to_object_dist_end":0.22578,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```