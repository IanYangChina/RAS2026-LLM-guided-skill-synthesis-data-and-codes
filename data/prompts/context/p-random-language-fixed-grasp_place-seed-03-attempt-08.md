## Search State

- **Seed**: 3
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | 0.1362 | 0.48 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9 | 0.0772 | 0.47 | ❌ rejected |
| 6 | approach → descend → grasp → lift → grasp → approach → descend → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | — | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 9 | 0.2272 | 0.77 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | 0.1426 | 0.46 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.1155 | 0.43 | ❌ rejected |

**Proposal policy**: task_score is 0.48 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.136) — your mutation base

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

- **Composite score**: 0.136
- **task_score** (E): 0.484
- **fitness_score**: 0.716  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1210 |
| descend_1 | 1.00 | 1.00 | 0.1425 |
| grasp_1 | 0.00 | 1.00 | 0.0000 |
| lift_1 | 1.00 | 1.00 | 0.1414 |
| transport_1 | 1.00 | 1.00 | 0.1930 |
| descend_2 | 1.00 | 1.00 | 0.0411 |
| release_1 | 1.00 | 1.00 | 0.0210 |
| retract_1 | 1.00 | 1.00 | 0.0235 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.002, 0.187) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.507, 0.002, 0.187)→(0.506, 0.002, 0.044) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 0.00 / guard_failure | (0.501, 0.002, 0.039)→(0.501, 0.002, 0.039) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 44.000 | 0.137 | 0.168 |
| lift_1 | lift | 1.00 / step_budget | (0.501, 0.002, 0.039)→(0.507, 0.002, 0.180) | (0.511, 0.002, 0.026)→(0.515, 0.002, 0.162) | 0.246→0.216 | 1.00 / 38.667 | 0.076 | 0.548 |
| transport_1 | approach | 1.00 / step_budget | (0.507, 0.002, 0.180)→(0.611, 0.163, 0.182) | (0.515, 0.002, 0.162)→(0.609, 0.164, 0.158) | 0.216→0.037 | 1.00 / 33.667 | 623.105 | 0.278 |
| descend_2 | descend | 1.00 / step_budget | (0.611, 0.163, 0.182)→(0.620, 0.177, 0.147) | (0.609, 0.164, 0.158)→(0.620, 0.179, 0.121) | 0.037→0.019 | 1.00 / 33.000 | 524.430 | 0.325 |
| release_1 | release | 1.00 / step_budget | (0.620, 0.177, 0.147)→(0.613, 0.175, 0.167) | (0.620, 0.179, 0.121)→(0.613, 0.175, 0.026) | 0.019→0.113 | 1.00 / 4.000 | 0.118 | 1.132 |
| retract_1 | retract | 1.00 / step_budget | (0.613, 0.175, 0.167)→(0.622, 0.180, 0.186) | (0.613, 0.175, 0.026)→(0.612, 0.176, 0.026) | 0.113→0.113 | 1.00 / 4.000 | 0.123 | 0.140 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.569
- phase_score: 0.436
- phase_breakdown.release_1_score: 0.431
- phase_breakdown.descend_1_score: 0.852
- phase_breakdown.transport_arc_score: 0.244
- phase_breakdown.approach_1_score: 0.044
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.758

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.758
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.569
- **Median Q (composite search score)**: 0.171
- **K-run variance**: 0.0030
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: descend_1.grasp_z_offset
- **Final σ (mean)**: 0.322


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68243,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17165,"descend_1.grasp_z_offset":0.01,"descend_2.place_z_offset":0.00859,"lift_1.lift_height":0.15351,"release_1.release_duration":0.31075,"retract_1.retract_height":0.03252,"transport_1.transport_height":0.04086,"transport_1.transport_speed":0.37299},"optimized_scores":{"best_composite_score":0.1709,"best_fitness_score":0.7509,"best_task_score":0.55541},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":344.0,"contact_point_centroid":[0.6258,0.20555,-0.00342],"force_p95":0.7598,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.87511,"mean_force":0.20212,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61744,0.20276,0.12293]},{"body_a":"world","body_b":"grasp_target","contact_count":130.0,"contact_point_centroid":[0.45587,-0.02543,-0.00111],"force_p95":0.28565,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49385,"mean_force":0.05779,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44812,-0.02572,0.04206]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3836.0,"contact_point_centroid":[0.6117,0.21248,0.12621],"force_p95":0.11582,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44776,"mean_force":0.08921,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61522,0.19397,0.12699]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20130.0,"contact_point_centroid":[0.52785,0.05427,0.15734],"force_p95":0.08345,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38419,"mean_force":0.05128,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52558,0.07308,0.15643]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4664.0,"contact_point_centroid":[0.62065,0.17662,0.12265],"force_p95":0.10374,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36585,"mean_force":0.07741,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.61529,0.19407,0.12687]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17692.0,"contact_point_centroid":[0.52218,0.08916,0.15876],"force_p95":0.08932,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32984,"mean_force":0.05656,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52339,0.07012,0.15669]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15821.0,"contact_point_centroid":[0.44905,-0.04489,0.10522],"force_p95":0.07379,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30006,"mean_force":0.04978,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44984,-0.02578,0.10327]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15695.0,"contact_point_centroid":[0.45135,-0.00666,0.10479],"force_p95":0.07382,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29726,"mean_force":0.05034,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44985,-0.02579,0.10325]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":701.0,"contact_point_centroid":[0.61931,0.22325,0.11102],"force_p95":0.106,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1938,"mean_force":0.071,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62196,0.20432,0.11177]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":854.0,"contact_point_centroid":[0.62754,0.18696,0.10706],"force_p95":0.09399,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18864,"mean_force":0.06133,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62196,0.20431,0.11177]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.45857,-0.02636,-0.00205],"force_p95":0.13726,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16541,"mean_force":0.127,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44978,-0.02577,0.0406]},{"body_a":"world","body_b":"grasp_target","contact_count":1008.0,"contact_point_centroid":[0.62658,0.20569,-0.00198],"force_p95":0.13774,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14602,"mean_force":0.12279,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.62123,0.20475,0.13504]},{"body_a":"world","body_b":"grasp_target","contact_count":1168.0,"contact_point_centroid":[0.45856,-0.02632,-0.00189],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48057,-0.01074,0.25578]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5833.0,"contact_point_centroid":[0.45089,-0.00663,0.04164],"force_p95":0.07277,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13014,"mean_force":0.04536,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44934,-0.02576,0.04017]},{"body_a":"world","body_b":"grasp_target","contact_count":2100.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45648,-0.0242,0.12702]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5542.0,"contact_point_centroid":[0.4484,-0.04493,0.04238],"force_p95":0.07765,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0935,"mean_force":0.04762,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44934,-0.02576,0.04017]}],"total_contact_groups":16},"final_pose_error":0.01168,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62659,0.2057,0.02602],"final_tcp_position":[0.62441,0.20619,0.13665],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":296.14378,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":293.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1168.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.4611,-0.02259,0.21029],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18433,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":525.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2100.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45424,-0.0259,0.04502],"tcp_start":[0.4611,-0.02259,0.21029],"tcp_to_object_dist_end":0.01949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45849,-0.02607,0.02583],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30356,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13671,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13179.0,"raw_peak_contact_force":0.16541,"tcp_end":[0.44932,-0.02576,0.04015],"tcp_start":[0.44932,-0.02576,0.04015],"tcp_to_object_dist_end":0.01701,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.46217,-0.02649,0.14858],"object_pos_start":[0.45849,-0.02608,0.02584],"object_to_goal_dist_end":0.29066,"object_to_goal_dist_start":0.30356,"object_z_max":0.14846,"peak_contact_force":0.07478,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":31646.0,"raw_peak_contact_force":0.49385,"tcp_end":[0.45441,-0.02593,0.16783],"tcp_start":[0.44932,-0.02576,0.04015],"tcp_to_object_dist_end":0.02076,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5992,0.17898,0.1202],"object_pos_start":[0.46217,-0.02649,0.14858],"object_to_goal_dist_end":0.04299,"object_to_goal_dist_start":0.29066,"object_z_max":0.14862,"peak_contact_force":296.14378,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37822.0,"raw_peak_contact_force":0.38419,"subtask_id":"transport_arc","tcp_end":[0.60528,0.17878,0.14857],"tcp_start":[0.45441,-0.02593,0.16783],"tcp_to_object_dist_end":0.02901,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":368.0,"n_steps_budget":1000.0,"object_pos_end":[0.62263,0.20715,0.08411],"object_pos_start":[0.5992,0.17898,0.1202],"object_to_goal_dist_end":0.03095,"object_to_goal_dist_start":0.04299,"object_z_max":0.1202,"peak_contact_force":0.11545,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8500.0,"raw_peak_contact_force":0.44776,"subtask_id":"release_1","tcp_end":[0.62398,0.2049,0.11556],"tcp_start":[0.60528,0.17878,0.14857],"tcp_to_object_dist_end":0.03156,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62689,0.20575,0.02638],"object_pos_start":[0.62263,0.20715,0.08411],"object_to_goal_dist_end":0.08783,"object_to_goal_dist_start":0.03095,"object_z_max":0.08411,"peak_contact_force":0.14509,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1899.0,"raw_peak_contact_force":0.87511,"tcp_end":[0.6173,0.20271,0.13545],"tcp_start":[0.62398,0.2049,0.11556],"tcp_to_object_dist_end":0.10953,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":252.0,"n_steps_budget":600.0,"object_pos_end":[0.62659,0.2057,0.02602],"object_pos_start":[0.62689,0.20575,0.02638],"object_to_goal_dist_end":0.08821,"object_to_goal_dist_start":0.08783,"object_z_max":0.02638,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1008.0,"raw_peak_contact_force":0.14602,"tcp_end":[0.62441,0.20619,0.13665],"tcp_start":[0.6173,0.20271,0.13545],"tcp_to_object_dist_end":0.11065,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71429,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12844,"descend_1.grasp_z_offset":0.01005,"descend_2.place_z_offset":0.0049,"lift_1.lift_height":0.19375,"release_1.release_duration":0.23601,"retract_1.retract_height":0.04978,"transport_1.transport_height":0.04282,"transport_1.transport_speed":0.31711},"optimized_scores":{"best_composite_score":0.05934,"best_fitness_score":0.63934,"best_task_score":0.32942},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":226.0,"contact_point_centroid":[0.62708,0.14981,-0.00668],"force_p95":1.01199,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.48654,"mean_force":0.31895,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63455,0.15076,0.20849]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.54098,0.00089,-0.00113],"force_p95":0.41828,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57691,"mean_force":0.08668,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53178,0.00087,0.03923]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19827.0,"contact_point_centroid":[0.53412,0.02013,0.11919],"force_p95":0.07473,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33779,"mean_force":0.05084,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53418,0.00093,0.11729]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21335.0,"contact_point_centroid":[0.53392,-0.01818,0.11712],"force_p95":0.07098,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30856,"mean_force":0.0477,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53407,0.00093,0.11538]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1062.0,"contact_point_centroid":[0.63481,0.17071,0.196],"force_p95":0.07922,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28468,"mean_force":0.04991,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63824,0.15183,0.1936]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21458.0,"contact_point_centroid":[0.58884,0.05499,0.20949],"force_p95":0.0676,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23875,"mean_force":0.04672,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58686,0.07404,0.2077]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1335.0,"contact_point_centroid":[0.64136,0.13288,0.19424],"force_p95":0.06747,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2346,"mean_force":0.04015,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63824,0.15183,0.19361]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1907.0,"contact_point_centroid":[0.63209,0.16577,0.21253],"force_p95":0.07567,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22874,"mean_force":0.05066,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63672,0.14724,0.20982]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19890.0,"contact_point_centroid":[0.58509,0.09353,0.21059],"force_p95":0.07387,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22178,"mean_force":0.04937,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.58719,0.07454,0.20778]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2090.0,"contact_point_centroid":[0.63978,0.12823,0.21079],"force_p95":0.06909,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18096,"mean_force":0.04722,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.63671,0.14722,0.20989]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.5443,0.00116,-0.00203],"force_p95":0.13001,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14518,"mean_force":0.12538,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53366,0.00092,0.03812]},{"body_a":"world","body_b":"grasp_target","contact_count":1472.0,"contact_point_centroid":[0.62715,0.14966,-0.00197],"force_p95":0.13084,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14324,"mean_force":0.12092,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.63893,0.15407,0.22275]},{"body_a":"world","body_b":"grasp_target","contact_count":1860.0,"contact_point_centroid":[0.54431,0.00113,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.517,0.00047,0.23164]},{"body_a":"world","body_b":"grasp_target","contact_count":1460.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53619,0.00097,0.10365]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5292.0,"contact_point_centroid":[0.53335,0.0202,0.03949],"force_p95":0.07442,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09564,"mean_force":0.0497,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53318,0.00091,0.03755]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6430.0,"contact_point_centroid":[0.53287,-0.01816,0.0391],"force_p95":0.06278,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08788,"mean_force":0.04104,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53318,0.00091,0.03755]}],"total_contact_groups":16},"final_pose_error":0.01173,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.62714,0.14966,0.02602],"final_tcp_position":[0.64331,0.15663,0.23007],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1573.09317,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":466.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1860.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.5366,0.00097,0.16453],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13872,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":365.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1460.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53851,0.00101,0.04397],"tcp_start":[0.5366,0.00097,0.16453],"tcp_to_object_dist_end":0.01886,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5442,0.00113,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25025,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12986,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13526.0,"raw_peak_contact_force":0.14518,"tcp_end":[0.53316,0.00091,0.03752],"tcp_start":[0.53316,0.00091,0.03752],"tcp_to_object_dist_end":0.01605,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54749,0.00116,0.18055],"object_pos_start":[0.54421,0.00113,0.02589],"object_to_goal_dist_end":0.18645,"object_to_goal_dist_start":0.25025,"object_z_max":0.18037,"peak_contact_force":0.07899,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41306.0,"raw_peak_contact_force":0.57691,"tcp_end":[0.53963,0.00105,0.19802],"tcp_start":[0.53316,0.00091,0.03752],"tcp_to_object_dist_end":0.01915,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63588,0.14432,0.19941],"object_pos_start":[0.54749,0.00116,0.18055],"object_to_goal_dist_end":0.01991,"object_to_goal_dist_start":0.18645,"object_z_max":0.1994,"peak_contact_force":1573.09317,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":41348.0,"raw_peak_contact_force":0.23875,"subtask_id":"transport_arc","tcp_end":[0.63447,0.14305,0.222],"tcp_start":[0.53963,0.00105,0.19802],"tcp_to_object_dist_end":0.02267,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":95.0,"n_steps_budget":1000.0,"object_pos_end":[0.64176,0.15363,0.17465],"object_pos_start":[0.63588,0.14432,0.19941],"object_to_goal_dist_end":0.01802,"object_to_goal_dist_start":0.01991,"object_z_max":0.19941,"peak_contact_force":1573.09317,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3997.0,"raw_peak_contact_force":0.22874,"subtask_id":"release_1","tcp_end":[0.63999,0.15207,0.1977],"tcp_start":[0.63447,0.14305,0.222],"tcp_to_object_dist_end":0.02317,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6294,0.14926,0.02494],"object_pos_start":[0.64176,0.15363,0.17465],"object_to_goal_dist_end":0.16739,"object_to_goal_dist_start":0.01802,"object_z_max":0.17465,"peak_contact_force":0.08054,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2623.0,"raw_peak_contact_force":1.48654,"tcp_end":[0.6345,0.15076,0.21703],"tcp_start":[0.63999,0.15207,0.1977],"tcp_to_object_dist_end":0.19216,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":368.0,"n_steps_budget":600.0,"object_pos_end":[0.62714,0.14966,0.02602],"object_pos_start":[0.6294,0.14926,0.02494],"object_to_goal_dist_end":0.16656,"object_to_goal_dist_start":0.16739,"object_z_max":0.02666,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1472.0,"raw_peak_contact_force":0.14324,"tcp_end":[0.64331,0.15663,0.23007],"tcp_start":[0.6345,0.15076,0.21703],"tcp_to_object_dist_end":0.20481,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83221,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14919,"descend_1.grasp_z_offset":0.01,"descend_2.place_z_offset":0.01247,"lift_1.lift_height":0.16086,"release_1.release_duration":0.39468,"retract_1.retract_height":0.0966,"transport_1.transport_height":0.07751,"transport_1.transport_speed":0.41526},"optimized_scores":{"best_composite_score":0.17843,"best_fitness_score":0.75843,"best_task_score":0.56858},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":324.0,"contact_point_centroid":[0.58213,0.17146,-0.00406],"force_p95":0.65113,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.03572,"mean_force":0.21221,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58859,0.17255,0.13579]},{"body_a":"world","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.52765,0.02953,-0.00119],"force_p95":0.38769,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5741,"mean_force":0.07423,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51832,0.02971,0.03985]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16148.0,"contact_point_centroid":[0.52014,0.04895,0.10898],"force_p95":0.07838,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33517,"mean_force":0.05246,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52091,0.02981,0.1068]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17658.0,"contact_point_centroid":[0.5215,0.01071,0.10448],"force_p95":0.07427,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30002,"mean_force":0.04865,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52063,0.02979,0.1031]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2686.0,"contact_point_centroid":[0.58903,0.18871,0.1547],"force_p95":0.08329,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29869,"mean_force":0.05908,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59278,0.17005,0.15212]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1050.0,"contact_point_centroid":[0.58923,0.1926,0.12559],"force_p95":0.08011,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26514,"mean_force":0.05008,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59296,0.1739,0.12305]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1236.0,"contact_point_centroid":[0.59757,0.15536,0.12255],"force_p95":0.07316,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24548,"mean_force":0.04414,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59296,0.1739,0.12305]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3160.0,"contact_point_centroid":[0.59733,0.15156,0.15196],"force_p95":0.07814,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23084,"mean_force":0.05198,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59278,0.17005,0.15212]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21116.0,"contact_point_centroid":[0.56264,0.08346,0.17438],"force_p95":0.06995,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21189,"mean_force":0.0472,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55962,0.1024,0.17295]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19775.0,"contact_point_centroid":[0.55665,0.12094,0.17582],"force_p95":0.07071,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19445,"mean_force":0.04919,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.55944,0.1021,0.17289]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53055,0.03079,-0.00211],"force_p95":0.14751,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19341,"mean_force":0.13048,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5202,0.02984,0.03859]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6008.0,"contact_point_centroid":[0.52075,0.01072,0.03939],"force_p95":0.07261,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14602,"mean_force":0.0439,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51973,0.02981,0.03804]},{"body_a":"world","body_b":"grasp_target","contact_count":1572.0,"contact_point_centroid":[0.5305,0.03079,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12294,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51066,0.01336,0.24253]},{"body_a":"world","body_b":"grasp_target","contact_count":1936.0,"contact_point_centroid":[0.58191,0.17137,-0.00198],"force_p95":0.12469,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13221,"mean_force":0.12265,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.59149,0.17451,0.16873]},{"body_a":"world","body_b":"grasp_target","contact_count":1720.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52304,0.02869,0.1143]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5333.0,"contact_point_centroid":[0.51918,0.04903,0.04043],"force_p95":0.08148,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08365,"mean_force":0.04947,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51973,0.02981,0.03805]}],"total_contact_groups":16},"final_pose_error":0.0132,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.58191,0.17137,0.02602],"final_tcp_position":[0.59696,0.17706,0.1924],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.03572,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":394.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1572.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52376,0.0274,0.1857],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15986,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":430.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1720.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52499,0.03015,0.04421],"tcp_start":[0.52376,0.0274,0.1857],"tcp_to_object_dist_end":0.01902,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53046,0.03033,0.02568],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.1839,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14535,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13145.0,"raw_peak_contact_force":0.19341,"tcp_end":[0.51971,0.02981,0.03802],"tcp_start":[0.51971,0.02981,0.03802],"tcp_to_object_dist_end":0.01638,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.53457,0.03063,0.15627],"object_pos_start":[0.53047,0.03036,0.0257],"object_to_goal_dist_end":0.16939,"object_to_goal_dist_start":0.18387,"object_z_max":0.15615,"peak_contact_force":0.07517,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33953.0,"raw_peak_contact_force":0.5741,"tcp_end":[0.52622,0.03009,0.17379],"tcp_start":[0.51971,0.02981,0.03802],"tcp_to_object_dist_end":0.01942,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59233,0.16788,0.15447],"object_pos_start":[0.53457,0.03063,0.15627],"object_to_goal_dist_end":0.04848,"object_to_goal_dist_start":0.16939,"object_z_max":0.15632,"peak_contact_force":0.07686,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40891.0,"raw_peak_contact_force":0.21189,"subtask_id":"transport_arc","tcp_end":[0.59214,0.16643,0.17687],"tcp_start":[0.52622,0.03009,0.17379],"tcp_to_object_dist_end":0.02245,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":158.0,"n_steps_budget":1000.0,"object_pos_end":[0.59595,0.17632,0.10378],"object_pos_start":[0.59233,0.16788,0.15447],"object_to_goal_dist_end":0.00741,"object_to_goal_dist_start":0.04848,"object_z_max":0.15447,"peak_contact_force":0.08135,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5846.0,"raw_peak_contact_force":0.29869,"subtask_id":"release_1","tcp_end":[0.59515,0.17443,0.12697],"tcp_start":[0.59214,0.16643,0.17687],"tcp_to_object_dist_end":0.02328,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58173,0.17131,0.02641],"object_pos_start":[0.59595,0.17632,0.10378],"object_to_goal_dist_end":0.08436,"object_to_goal_dist_start":0.00741,"object_z_max":0.10378,"peak_contact_force":0.12852,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2610.0,"raw_peak_contact_force":1.03572,"tcp_end":[0.58846,0.17251,0.14767],"tcp_start":[0.59515,0.17443,0.12697],"tcp_to_object_dist_end":0.12145,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.58191,0.17137,0.02602],"object_pos_start":[0.58173,0.17131,0.02641],"object_to_goal_dist_end":0.08469,"object_to_goal_dist_start":0.08436,"object_z_max":0.02641,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1936.0,"raw_peak_contact_force":0.13221,"tcp_end":[0.59696,0.17706,0.1924],"tcp_start":[0.58846,0.17251,0.14767],"tcp_to_object_dist_end":0.16715,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```