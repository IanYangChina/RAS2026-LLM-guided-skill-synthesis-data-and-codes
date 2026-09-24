## Search State

- **Seed**: 3
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0522 | 0.48 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.2603 | 0.18 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.1952 | 0.76 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3928 | 1.00 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.3147 | 0.94 | ❌ rejected |

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

## Current Skill (Q=0.052) — your mutation base

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
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_z_offset:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
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
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: transport_to_goal
  type: approach
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: place_object
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    place_z_offset:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **place_object** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.052
- **task_score** (E): 0.482
- **fitness_score**: 0.702  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.650

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0808 |
| descend_1 | 1.00 | 1.00 | 0.1733 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 1.00 | 1.00 | 0.1430 |
| transport_to_goal | 1.00 | 1.00 | 0.2285 |
| place_object | 1.00 | 1.00 | 0.1277 |
| release_1 | 1.00 | 1.00 | 0.0195 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.504, 0.008, 0.229) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.122 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.504, 0.008, 0.229)→(0.506, 0.003, 0.056) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.003, 0.056)→(0.498, 0.003, 0.047) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.025) | 0.246→0.246 | 1.00 / 44.000 | 0.187 | 0.232 |
| lift_1 | lift | 1.00 / step_budget | (0.498, 0.003, 0.047)→(0.494, 0.003, 0.190) | (0.511, 0.002, 0.025)→(0.502, 0.002, 0.164) | 0.246→0.225 | 1.00 / 35.667 | 0.094 | 0.409 |
| transport_to_goal | approach | 1.00 / step_budget | (0.494, 0.003, 0.190)→(0.617, 0.171, 0.274) | (0.502, 0.002, 0.164)→(0.619, 0.171, 0.244) | 0.225→0.107 | 1.00 / 28.000 | 0.111 | 0.121 |
| place_object | descend | 1.00 / step_budget | (0.617, 0.171, 0.274)→(0.621, 0.178, 0.147) | (0.619, 0.171, 0.244)→(0.622, 0.178, 0.114) | 0.107→0.030 | 1.00 / 25.333 | 0.132 | 0.272 |
| release_1 | release | 1.00 / step_budget | (0.621, 0.178, 0.147)→(0.614, 0.176, 0.165) | (0.622, 0.178, 0.114)→(0.608, 0.182, 0.026) | 0.030→0.114 | 1.00 / 3.000 | 0.176 | 1.144 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.567
- phase_score: 0.366
- phase_breakdown.approach_1_score: 0.007
- phase_breakdown.release_1_score: 0.662
- phase_breakdown.descend_1_score: 0.826
- phase_breakdown.transport_arc_score: 0.062
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.744

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.744
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.567
- **Median Q (composite search score)**: 0.085
- **K-run variance**: 0.0028
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.350


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.07849,"average_solve_count":344.0,"average_success_count":344.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15476,"approach_1.approach_speed":0.06903,"approach_1.arc_height":0.1139,"descend_1.descend_speed":0.04093,"descend_1.grasp_z_offset":0.01109,"lift_1.lift_height":0.14098,"lift_1.lift_speed":0.04305,"place_object.place_speed":0.05771,"place_object.place_z_offset":0.02538,"transport_to_goal.transport_speed":0.03305},"optimized_scores":{"best_composite_score":0.08512,"best_fitness_score":0.73512,"best_task_score":0.5496},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":136.0,"contact_point_centroid":[0.61164,0.20181,-0.00887],"force_p95":1.27357,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.41161,"mean_force":0.53889,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61784,0.202,0.16129]},{"body_a":"world","body_b":"grasp_target","contact_count":90.0,"contact_point_centroid":[0.45474,-0.02294,-0.00174],"force_p95":0.37828,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.477,"mean_force":0.1399,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44635,-0.02325,0.04979]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":591.0,"contact_point_centroid":[0.62143,0.22198,0.1473],"force_p95":0.19328,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40307,"mean_force":0.122,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62192,0.2036,0.15233]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1507.0,"contact_point_centroid":[0.62208,0.21916,0.20098],"force_p95":0.15734,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31623,"mean_force":0.11223,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.62133,0.20056,0.20493]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":660.0,"contact_point_centroid":[0.62281,0.1862,0.14805],"force_p95":0.13386,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29688,"mean_force":0.07563,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62185,0.20357,0.1522]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6393.0,"contact_point_centroid":[0.44501,-0.00401,0.10403],"force_p95":0.11755,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28982,"mean_force":0.06787,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44415,-0.02315,0.10437]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7986.0,"contact_point_centroid":[0.44424,-0.04179,0.10877],"force_p95":0.09355,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26772,"mean_force":0.05509,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44414,-0.02315,0.10794]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1802.0,"contact_point_centroid":[0.62202,0.18245,0.20239],"force_p95":0.13503,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26766,"mean_force":0.09242,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.62128,0.20048,0.20636]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45868,-0.02625,-0.00226],"force_p95":0.25474,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26373,"mean_force":0.17456,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44845,-0.02332,0.04937]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4574.0,"contact_point_centroid":[0.44725,-0.00406,0.04817],"force_p95":0.08983,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16703,"mean_force":0.05991,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44741,-0.02328,0.04837]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11409.0,"contact_point_centroid":[0.53106,0.10737,0.20664],"force_p95":0.11225,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14416,"mean_force":0.07995,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53138,0.08846,0.20943]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16661.0,"contact_point_centroid":[0.52442,0.06246,0.20594],"force_p95":0.08979,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1391,"mean_force":0.05631,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52542,0.08104,0.2066]},{"body_a":"world","body_b":"grasp_target","contact_count":964.0,"contact_point_centroid":[0.45856,-0.02632,-0.00186],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12313,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48001,0.01031,0.24619]},{"body_a":"world","body_b":"grasp_target","contact_count":1148.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45701,-0.01571,0.12609]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5583.0,"contact_point_centroid":[0.44664,-0.04247,0.04878],"force_p95":0.07678,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08978,"mean_force":0.04713,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44742,-0.02328,0.04838]}],"total_contact_groups":15},"final_pose_error":0.01962,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62276,0.22072,0.02552],"final_tcp_position":[0.62423,0.20429,0.1578],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.41161,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":242.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":964.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46052,-0.0084,0.19336],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1683,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":287.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1148.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45514,-0.02347,0.05616],"tcp_start":[0.46052,-0.0084,0.19336],"tcp_to_object_dist_end":0.03047,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45861,-0.02441,0.02501],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30245,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.25357,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11957.0,"raw_peak_contact_force":0.26373,"subtask_id":"grasp_1","tcp_end":[0.44738,-0.02328,0.04835],"tcp_start":[0.45514,-0.02347,0.05616],"tcp_to_object_dist_end":0.02593,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":399.0,"n_steps_budget":1000.0,"object_pos_end":[0.4505,-0.02444,0.14342],"object_pos_start":[0.45861,-0.02441,0.02501],"object_to_goal_dist_end":0.29539,"object_to_goal_dist_start":0.30245,"object_z_max":0.14313,"peak_contact_force":0.11718,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14469.0,"raw_peak_contact_force":0.477,"tcp_end":[0.44409,-0.02313,0.16989],"tcp_start":[0.44738,-0.02328,0.04835],"tcp_to_object_dist_end":0.02726,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":978.0,"n_steps_budget":1000.0,"object_pos_end":[0.61988,0.19633,0.21818],"object_pos_start":[0.4505,-0.02444,0.14342],"object_to_goal_dist_end":0.10524,"object_to_goal_dist_start":0.29539,"object_z_max":0.21812,"peak_contact_force":0.132,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28070.0,"raw_peak_contact_force":0.14416,"subtask_id":"transport_arc","tcp_end":[0.61957,0.19726,0.25122],"tcp_start":[0.44409,-0.02313,0.16989],"tcp_to_object_dist_end":0.03306,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":171.0,"n_steps_budget":1000.0,"object_pos_end":[0.62674,0.20333,0.12299],"object_pos_start":[0.61988,0.19633,0.21818],"object_to_goal_dist_end":0.01068,"object_to_goal_dist_start":0.10524,"object_z_max":0.21818,"peak_contact_force":0.17398,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3309.0,"raw_peak_contact_force":0.31623,"subtask_id":"release_1","tcp_end":[0.62423,0.20429,0.1578],"tcp_start":[0.61957,0.19726,0.25122],"tcp_to_object_dist_end":0.03491,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62276,0.22072,0.02552],"object_pos_start":[0.62674,0.20333,0.12299],"object_to_goal_dist_end":0.08978,"object_to_goal_dist_start":0.01068,"object_z_max":0.12299,"peak_contact_force":0.27645,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1387.0,"raw_peak_contact_force":1.41161,"subtask_id":"release_1","tcp_end":[0.61772,0.20195,0.17552],"tcp_start":[0.62423,0.20429,0.1578],"tcp_to_object_dist_end":0.15126,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.91435,"average_solve_count":467.0,"average_success_count":467.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17543,"approach_1.approach_speed":0.03674,"approach_1.arc_height":0.13063,"descend_1.descend_speed":0.03097,"descend_1.grasp_z_offset":0.01006,"lift_1.lift_height":0.16617,"lift_1.lift_speed":0.02582,"place_object.place_speed":0.06929,"place_object.place_z_offset":-0.0316,"transport_to_goal.transport_speed":0.04157},"optimized_scores":{"best_composite_score":-0.02207,"best_fitness_score":0.62793,"best_task_score":0.32891},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":242.0,"contact_point_centroid":[0.62075,0.15336,-0.0057],"force_p95":1.17779,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.33352,"mean_force":0.29738,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63704,0.15398,0.18626]},{"body_a":"world","body_b":"grasp_target","contact_count":108.0,"contact_point_centroid":[0.54062,0.00224,-0.00157],"force_p95":0.33704,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37016,"mean_force":0.15782,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52829,0.00219,0.04506]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11039.0,"contact_point_centroid":[0.52628,0.02134,0.11579],"force_p95":0.07785,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23237,"mean_force":0.05349,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52577,0.00214,0.11302]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12034.0,"contact_point_centroid":[0.52599,-0.01699,0.11614],"force_p95":0.07477,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22846,"mean_force":0.04995,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52577,0.00214,0.11369]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4254.0,"contact_point_centroid":[0.6409,0.17154,0.25259],"force_p95":0.11309,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21943,"mean_force":0.06802,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.64131,0.15261,0.25291]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4664.0,"contact_point_centroid":[0.64065,0.13358,0.25456],"force_p95":0.11078,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21189,"mean_force":0.06623,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.64127,0.15254,0.2546]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54434,0.00123,-0.0021],"force_p95":0.14867,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20923,"mean_force":0.13002,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5308,0.00224,0.04567]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1110.0,"contact_point_centroid":[0.63879,0.13607,0.17318],"force_p95":0.08009,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15572,"mean_force":0.0489,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6409,0.15516,0.17292]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1126.0,"contact_point_centroid":[0.63918,0.17428,0.17226],"force_p95":0.07733,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15564,"mean_force":0.04845,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64089,0.15516,0.17291]},{"body_a":"world","body_b":"grasp_target","contact_count":824.0,"contact_point_centroid":[0.54431,0.00113,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12322,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51452,0.01301,0.26106]},{"body_a":"world","body_b":"grasp_target","contact_count":1296.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53445,0.00693,0.13777]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5063.0,"contact_point_centroid":[0.53049,0.0214,0.04728],"force_p95":0.06734,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10506,"mean_force":0.04278,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5296,0.00222,0.04427]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17268.0,"contact_point_centroid":[0.58399,0.05882,0.25812],"force_p95":0.07171,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10401,"mean_force":0.049,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58297,0.07785,0.25697]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15395.0,"contact_point_centroid":[0.5837,0.09641,0.25762],"force_p95":0.07679,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10007,"mean_force":0.05497,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58252,0.07727,0.25643]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4953.0,"contact_point_centroid":[0.53066,-0.01707,0.04609],"force_p95":0.07107,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07284,"mean_force":0.04485,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5296,0.00222,0.04428]}],"total_contact_groups":15},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.62382,0.15397,0.02607],"final_tcp_position":[0.64321,0.15572,0.1787],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.33352,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":207.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":824.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53282,0.01127,0.21778],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19237,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":324.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1296.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53842,0.00245,0.05503],"tcp_start":[0.53282,0.01127,0.21778],"tcp_to_object_dist_end":0.02963,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54425,0.00186,0.02564],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.24994,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.1453,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11816.0,"raw_peak_contact_force":0.20923,"subtask_id":"grasp_1","tcp_end":[0.52957,0.00222,0.04423],"tcp_start":[0.53842,0.00245,0.05503],"tcp_to_object_dist_end":0.02369,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":560.0,"n_steps_budget":1000.0,"object_pos_end":[0.53514,0.0021,0.16826],"object_pos_start":[0.54425,0.00186,0.02564],"object_to_goal_dist_end":0.19366,"object_to_goal_dist_start":0.24994,"object_z_max":0.16801,"peak_contact_force":0.07813,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23181.0,"raw_peak_contact_force":0.37016,"tcp_end":[0.52607,0.00215,0.19072],"tcp_start":[0.52957,0.00222,0.04423],"tcp_to_object_dist_end":0.02422,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":868.0,"n_steps_budget":1000.0,"object_pos_end":[0.64402,0.14963,0.29758],"object_pos_start":[0.53514,0.0021,0.16826],"object_to_goal_dist_end":0.10687,"object_to_goal_dist_start":0.19366,"object_z_max":0.29745,"peak_contact_force":0.08891,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32663.0,"raw_peak_contact_force":0.10401,"subtask_id":"transport_arc","tcp_end":[0.64012,0.14988,0.32461],"tcp_start":[0.52607,0.00215,0.19072],"tcp_to_object_dist_end":0.02731,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":251.0,"n_steps_budget":1000.0,"object_pos_end":[0.63877,0.15491,0.14993],"object_pos_start":[0.64402,0.14963,0.29758],"object_to_goal_dist_end":0.04224,"object_to_goal_dist_start":0.10687,"object_z_max":0.29758,"peak_contact_force":0.08003,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8918.0,"raw_peak_contact_force":0.21943,"subtask_id":"release_1","tcp_end":[0.64321,0.15572,0.1787],"tcp_start":[0.64012,0.14988,0.32461],"tcp_to_object_dist_end":0.02913,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62382,0.15397,0.02607],"object_pos_start":[0.63877,0.15491,0.14993],"object_to_goal_dist_end":0.1668,"object_to_goal_dist_start":0.04224,"object_z_max":0.14993,"peak_contact_force":0.10621,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2478.0,"raw_peak_contact_force":1.33352,"subtask_id":"release_1","tcp_end":[0.63699,0.15397,0.19607],"tcp_start":[0.64321,0.15572,0.1787],"tcp_to_object_dist_end":0.17051,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96919,"average_solve_count":357.0,"average_success_count":357.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.23408,"approach_1.approach_speed":0.05723,"approach_1.arc_height":0.11356,"descend_1.descend_speed":0.03829,"descend_1.grasp_z_offset":0.01294,"lift_1.lift_height":0.18028,"lift_1.lift_speed":0.04179,"place_object.place_speed":0.05963,"place_object.place_z_offset":-0.02333,"transport_to_goal.transport_speed":0.05147},"optimized_scores":{"best_composite_score":0.09358,"best_fitness_score":0.74358,"best_task_score":0.56699},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":318.0,"contact_point_centroid":[0.5812,0.17214,-0.00314],"force_p95":0.62233,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68763,"mean_force":0.20018,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5884,0.17288,0.11097]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":687.0,"contact_point_centroid":[0.59427,0.15592,0.09421],"force_p95":0.30739,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.46471,"mean_force":0.10431,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59259,0.17426,0.09762]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":707.0,"contact_point_centroid":[0.59441,0.19249,0.09305],"force_p95":0.27481,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42507,"mean_force":0.10109,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59259,0.17426,0.09761]},{"body_a":"world","body_b":"grasp_target","contact_count":95.0,"contact_point_centroid":[0.52684,0.0288,-0.00156],"force_p95":0.35279,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37932,"mean_force":0.13477,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51531,0.02883,0.04861]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2897.0,"contact_point_centroid":[0.5947,0.1882,0.17758],"force_p95":0.14836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28098,"mean_force":0.09504,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.59293,0.16991,0.18075]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11527.0,"contact_point_centroid":[0.51321,0.04776,0.1258],"force_p95":0.08263,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2673,"mean_force":0.05448,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51284,0.02867,0.1247]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10752.0,"contact_point_centroid":[0.51284,0.00954,0.12798],"force_p95":0.08235,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24226,"mean_force":0.05711,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51284,0.02867,0.12714]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2566.0,"contact_point_centroid":[0.5947,0.1517,0.17713],"force_p95":0.14356,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23614,"mean_force":0.10067,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.59296,0.16997,0.17964]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53056,0.03068,-0.00215],"force_p95":0.16524,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22265,"mean_force":0.13378,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51766,0.02899,0.04883]},{"body_a":"world","body_b":"grasp_target","contact_count":364.0,"contact_point_centroid":[0.5305,0.03079,-0.00166],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12406,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50894,0.00991,0.29001]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4326.0,"contact_point_centroid":[0.51705,0.00973,0.04864],"force_p95":0.07672,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13434,"mean_force":0.04954,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5165,0.02892,0.04749]},{"body_a":"world","body_b":"grasp_target","contact_count":1728.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52093,0.02492,0.1676]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8963.0,"contact_point_centroid":[0.54984,0.07561,0.22393],"force_p95":0.10354,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11535,"mean_force":0.06021,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54976,0.09459,0.22429]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9218.0,"contact_point_centroid":[0.55076,0.11354,0.22463],"force_p95":0.09185,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11123,"mean_force":0.0562,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54984,0.09473,0.22432]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5030.0,"contact_point_centroid":[0.51727,0.04812,0.04867],"force_p95":0.0742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07626,"mean_force":0.04406,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5165,0.02892,0.0475]}],"total_contact_groups":15},"final_pose_error":0.01971,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5788,0.17212,0.02633],"final_tcp_position":[0.59585,0.17516,0.10332],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.68763,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":92.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.026],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18337,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12212,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":364.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.51874,0.02062,0.27604],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25052,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":432.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.026],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18337,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1728.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.52508,0.02945,0.05773],"tcp_start":[0.51874,0.02062,0.27604],"tcp_to_object_dist_end":0.0322,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53048,0.02954,0.02545],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18463,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.16141,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11156.0,"raw_peak_contact_force":0.22265,"subtask_id":"grasp_1","tcp_end":[0.51647,0.02892,0.04746],"tcp_start":[0.52508,0.02945,0.05773],"tcp_to_object_dist_end":0.02609,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":579.0,"n_steps_budget":1000.0,"object_pos_end":[0.52004,0.02914,0.18168],"object_pos_start":[0.53048,0.02954,0.02545],"object_to_goal_dist_end":0.18544,"object_to_goal_dist_start":0.18463,"object_z_max":0.18142,"peak_contact_force":0.08744,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22374.0,"raw_peak_contact_force":0.37932,"tcp_end":[0.5132,0.02869,0.20826],"tcp_start":[0.51647,0.02892,0.04746],"tcp_to_object_dist_end":0.02746,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":536.0,"n_steps_budget":1000.0,"object_pos_end":[0.59457,0.16677,0.21559],"object_pos_start":[0.52004,0.02914,0.18168],"object_to_goal_dist_end":0.10837,"object_to_goal_dist_start":0.18544,"object_z_max":0.21553,"peak_contact_force":0.11105,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18181.0,"raw_peak_contact_force":0.11535,"subtask_id":"transport_arc","tcp_end":[0.59187,0.1659,0.24616],"tcp_start":[0.5132,0.02869,0.20826],"tcp_to_object_dist_end":0.0307,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":264.0,"n_steps_budget":1000.0,"object_pos_end":[0.6005,0.17536,0.06997],"object_pos_start":[0.59457,0.16677,0.21559],"object_to_goal_dist_end":0.03827,"object_to_goal_dist_start":0.10837,"object_z_max":0.21559,"peak_contact_force":0.14158,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5463.0,"raw_peak_contact_force":0.28098,"subtask_id":"release_1","tcp_end":[0.59585,0.17516,0.10332],"tcp_start":[0.59187,0.1659,0.24616],"tcp_to_object_dist_end":0.03368,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5788,0.17212,0.02633],"object_pos_start":[0.6005,0.17536,0.06997],"object_to_goal_dist_end":0.08511,"object_to_goal_dist_start":0.03827,"object_z_max":0.06997,"peak_contact_force":0.14549,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1712.0,"raw_peak_contact_force":0.68763,"subtask_id":"release_1","tcp_end":[0.58826,0.17283,0.12277],"tcp_start":[0.59585,0.17516,0.10332],"tcp_to_object_dist_end":0.09691,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```