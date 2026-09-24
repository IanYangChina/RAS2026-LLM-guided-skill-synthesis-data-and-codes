## Search State

- **Seed**: 3
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.1085 | 0.76 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3095 | 1.00 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0522 | 0.48 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.2603 | 0.18 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.1952 | 0.76 | ❌ rejected |

**Proposal policy**: task_score is 0.76 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.109) — your mutation base

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

- **Composite score**: 0.109
- **task_score** (E): 0.765
- **fitness_score**: 0.679  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.570

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1664 |
| descend_1 | 1.00 | 1.00 | 0.0855 |
| grasp_1 | 1.00 | 1.00 | 0.0117 |
| lift_1 | 1.00 | 1.00 | 0.1007 |
| transport_to_goal | 0.67 | 1.00 | 0.2389 |
| place_object | 1.00 | 1.00 | 0.0968 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.001, 0.139) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.001, 0.139)→(0.505, 0.002, 0.054) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.505, 0.002, 0.054)→(0.497, 0.001, 0.045) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 31.333 | 0.130 | 0.156 |
| lift_1 | lift | 1.00 / step_budget | (0.497, 0.001, 0.045)→(0.494, 0.001, 0.145) | (0.511, 0.002, 0.026)→(0.508, 0.002, 0.089) | 0.246→0.240 | 1.00 / 27.333 | 3253.504 | 0.428 |
| transport_to_goal | approach | 0.67 / step_budget | (0.494, 0.001, 0.145)→(0.610, 0.162, 0.256) | (0.508, 0.002, 0.089)→(0.594, 0.116, 0.170) | 0.240→0.126 | 1.00 / 26.000 | 10.601 | 0.129 |
| place_object | descend | 1.00 / step_budget | (0.610, 0.162, 0.256)→(0.619, 0.175, 0.162) | (0.594, 0.116, 0.170)→(0.601, 0.127, 0.113) | 0.126→0.067 | 1.00 / 24.000 | 0.109 | 0.162 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.650
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.361
- phase_breakdown.approach_1_score: 0.121
- phase_breakdown.release_1_score: 0.619
- phase_breakdown.descend_1_score: 0.782
- phase_breakdown.transport_arc_score: 0.062
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.979

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.979
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.147
- **K-run variance**: 0.0692
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.415


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24189,"average_solve_count":339.0,"average_success_count":339.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08636,"approach_1.approach_speed":0.04835,"descend_1.descend_speed":0.03153,"descend_1.grasp_z_offset":0.01,"lift_1.lift_height":0.18366,"lift_1.lift_speed":0.04805,"place_object.place_speed":0.06694,"place_object.place_z_offset":0.0043,"transport_to_goal.transport_speed":0.08468},"optimized_scores":{"best_composite_score":0.40943,"best_fitness_score":0.97943,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.45525,-0.02545,-0.00142],"force_p95":0.54949,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58417,"mean_force":0.16895,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44583,-0.0256,0.03252]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11256.0,"contact_point_centroid":[0.44319,-0.04466,0.11215],"force_p95":0.07273,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27832,"mean_force":0.04987,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44355,-0.02549,0.11057]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11071.0,"contact_point_centroid":[0.44322,-0.0063,0.11267],"force_p95":0.07196,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27693,"mean_force":0.05025,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44356,-0.02549,0.11081]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02618,-0.00206],"force_p95":0.1399,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19171,"mean_force":0.12731,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44798,-0.02567,0.03247]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4151.0,"contact_point_centroid":[0.62154,0.21917,0.19559],"force_p95":0.08203,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16259,"mean_force":0.05286,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.62108,0.20043,0.19495]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3280.0,"contact_point_centroid":[0.62144,0.18113,0.19765],"force_p95":0.09997,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16013,"mean_force":0.07079,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.62102,0.20034,0.19654]},{"body_a":"world","body_b":"grasp_target","contact_count":1336.0,"contact_point_centroid":[0.45856,-0.02632,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4805,-0.01091,0.21956]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17352.0,"contact_point_centroid":[0.53234,0.069,0.22423],"force_p95":0.07547,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12766,"mean_force":0.05079,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53215,0.08818,0.22292]},{"body_a":"world","body_b":"grasp_target","contact_count":2456.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45588,-0.02428,0.08465]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18291.0,"contact_point_centroid":[0.53547,0.1113,0.22537],"force_p95":0.07128,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10683,"mean_force":0.04793,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53532,0.09218,0.22397]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4822.0,"contact_point_centroid":[0.44688,-0.00642,0.03373],"force_p95":0.06819,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09822,"mean_force":0.04488,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44689,-0.02563,0.03144]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5169.0,"contact_point_centroid":[0.44674,-0.04486,0.03323],"force_p95":0.06692,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07888,"mean_force":0.04296,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4469,-0.02563,0.03144]}],"total_contact_groups":12},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62895,0.20425,0.11977],"final_tcp_position":[0.62425,0.20451,0.13706],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9760.30694,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":335.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1336.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.46087,-0.02273,0.13564],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10971,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":614.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2456.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45429,-0.0259,0.0385],"tcp_start":[0.46087,-0.02273,0.13564],"tcp_to_object_dist_end":0.0132,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45845,-0.0257,0.02579],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.3033,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.1373,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11791.0,"raw_peak_contact_force":0.19171,"subtask_id":"grasp_1","tcp_end":[0.44687,-0.02563,0.03141],"tcp_start":[0.45429,-0.0259,0.0385],"tcp_to_object_dist_end":0.01288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":533.0,"n_steps_budget":1000.0,"object_pos_end":[0.4542,-0.02555,0.186],"object_pos_start":[0.45845,-0.0257,0.02579],"object_to_goal_dist_end":0.30127,"object_to_goal_dist_start":0.3033,"object_z_max":0.18571,"peak_contact_force":9760.30694,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22407.0,"raw_peak_contact_force":0.58417,"tcp_end":[0.44376,-0.02548,0.19544],"tcp_start":[0.44687,-0.02563,0.03141],"tcp_to_object_dist_end":0.01408,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":875.0,"n_steps_budget":1000.0,"object_pos_end":[0.6269,0.19656,0.23679],"object_pos_start":[0.4542,-0.02555,0.186],"object_to_goal_dist_end":0.12327,"object_to_goal_dist_start":0.30127,"object_z_max":0.23676,"peak_contact_force":0.08959,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35643.0,"raw_peak_contact_force":0.12766,"subtask_id":"transport_arc","tcp_end":[0.61915,0.19683,0.25223],"tcp_start":[0.44376,-0.02548,0.19544],"tcp_to_object_dist_end":0.01728,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":205.0,"n_steps_budget":1000.0,"object_pos_end":[0.62895,0.20425,0.11977],"object_pos_start":[0.6269,0.19656,0.23679],"object_to_goal_dist_end":0.00701,"object_to_goal_dist_start":0.12327,"object_z_max":0.23679,"peak_contact_force":0.09223,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7431.0,"raw_peak_contact_force":0.16259,"subtask_id":"release_1","tcp_end":[0.62425,0.20451,0.13706],"tcp_start":[0.61915,0.19683,0.25223],"tcp_to_object_dist_end":0.01792,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28704,"average_solve_count":216.0,"average_success_count":216.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06112,"approach_1.approach_speed":0.08374,"descend_1.descend_speed":0.04755,"descend_1.grasp_z_offset":0.01017,"lift_1.lift_height":0.05055,"lift_1.lift_speed":0.05925,"place_object.place_speed":0.08487,"place_object.place_z_offset":0.01481,"transport_to_goal.transport_speed":0.03456},"optimized_scores":{"best_composite_score":0.14736,"best_fitness_score":0.71736,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.54026,0.00078,-0.0014],"force_p95":0.43997,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47029,"mean_force":0.15081,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52764,0.00083,0.04115]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2006.0,"contact_point_centroid":[0.52663,-0.0184,0.05704],"force_p95":0.13444,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30224,"mean_force":0.06798,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52569,0.00079,0.05434]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2360.0,"contact_point_centroid":[0.52657,0.01981,0.05614],"force_p95":0.11719,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28715,"mean_force":0.0603,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52569,0.00079,0.05434]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1527.0,"contact_point_centroid":[0.62919,0.15174,0.24648],"force_p95":0.13777,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20002,"mean_force":0.08269,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.62557,0.13283,0.24565]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1868.0,"contact_point_centroid":[0.62985,0.1145,0.24583],"force_p95":0.12627,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19202,"mean_force":0.07057,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.62575,0.13306,0.2451]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00103,-0.00203],"force_p95":0.13242,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15385,"mean_force":0.12543,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52999,0.00087,0.04152]},{"body_a":"world","body_b":"grasp_target","contact_count":1520.0,"contact_point_centroid":[0.54431,0.00113,-0.00191],"force_p95":0.1347,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51654,0.00046,0.20556]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17030.0,"contact_point_centroid":[0.57096,0.04221,0.17049],"force_p95":0.08864,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13709,"mean_force":0.05867,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56876,0.06121,0.16879]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17375.0,"contact_point_centroid":[0.57172,0.08103,0.17153],"force_p95":0.08226,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1271,"mean_force":0.05729,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56942,0.06209,0.17023]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.53016,-0.01835,0.04272],"force_p95":0.07629,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12287,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52876,0.00085,0.04008]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53478,0.00095,0.07069]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53004,0.01993,0.04185],"force_p95":0.06837,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09446,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52876,0.00085,0.04008]}],"total_contact_groups":12},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64436,0.14667,0.19252],"final_tcp_position":[0.63612,0.14655,0.21703],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":31.59097,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":381.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1520.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53544,0.00095,0.10893],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08338,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53697,0.001,0.04981],"tcp_start":[0.53544,0.00095,0.10893],"tcp_to_object_dist_end":0.02489,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.00076,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2505,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13064,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15385,"subtask_id":"grasp_1","tcp_end":[0.52873,0.00085,0.04004],"tcp_start":[0.53697,0.001,0.04981],"tcp_to_object_dist_end":0.02099,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":118.0,"n_steps_budget":600.0,"object_pos_end":[0.53857,0.00066,0.05622],"object_pos_start":[0.54421,0.00076,0.02587],"object_to_goal_dist_end":0.23424,"object_to_goal_dist_start":0.2505,"object_z_max":0.05596,"peak_contact_force":0.08346,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4452.0,"raw_peak_contact_force":0.47029,"tcp_end":[0.52459,0.00078,0.07109],"tcp_start":[0.52873,0.00085,0.04004],"tcp_to_object_dist_end":0.02041,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.6238,0.12161,0.24702],"object_pos_start":[0.53857,0.00066,0.05622],"object_to_goal_dist_end":0.07088,"object_to_goal_dist_start":0.23424,"object_z_max":0.24685,"peak_contact_force":31.59097,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34405.0,"raw_peak_contact_force":0.13709,"subtask_id":"transport_arc","tcp_end":[0.61708,0.12163,0.27106],"tcp_start":[0.52459,0.00078,0.07109],"tcp_to_object_dist_end":0.02497,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":124.0,"n_steps_budget":1000.0,"object_pos_end":[0.64436,0.14667,0.19252],"object_pos_start":[0.6238,0.12161,0.24702],"object_to_goal_dist_end":0.01196,"object_to_goal_dist_start":0.07088,"object_z_max":0.24708,"peak_contact_force":0.11335,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3395.0,"raw_peak_contact_force":0.20002,"subtask_id":"release_1","tcp_end":[0.63612,0.14655,0.21703],"tcp_start":[0.61708,0.12163,0.27106],"tcp_to_object_dist_end":0.02586,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.08571,"average_solve_count":315.0,"average_success_count":315.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12561,"approach_1.approach_speed":0.07637,"descend_1.descend_speed":0.03066,"descend_1.grasp_z_offset":0.02882,"lift_1.lift_height":0.12616,"lift_1.lift_speed":0.05513,"place_object.place_speed":0.0353,"place_object.place_z_offset":0.00509,"transport_to_goal.transport_speed":0.04611},"optimized_scores":{"best_composite_score":-0.23121,"best_fitness_score":0.33879,"best_task_score":0.29447},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1520.0,"contact_point_centroid":[0.53045,0.03079,-0.00199],"force_p95":0.13494,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23057,"mean_force":0.12283,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51287,0.02872,0.11553]},{"body_a":"world","body_b":"grasp_target","contact_count":1044.0,"contact_point_centroid":[0.5305,0.03079,-0.00187],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51012,0.01229,0.2376]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52247,0.02817,0.1041]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51761,0.02904,0.06478]},{"body_a":"world","body_b":"grasp_target","contact_count":2488.0,"contact_point_centroid":[0.53044,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55244,0.09987,0.20584]},{"body_a":"world","body_b":"grasp_target","contact_count":848.0,"contact_point_centroid":[0.53044,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.59369,0.171,0.19035]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13.0,"contact_point_centroid":[0.52397,0.03267,0.05599],"force_p95":0.09882,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09902,"mean_force":0.04826,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51621,0.02895,0.06326]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9.0,"contact_point_centroid":[0.52396,0.02593,0.05599],"force_p95":0.08126,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09821,"mean_force":0.03658,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51619,0.02895,0.06325]},{"body_a":"left_finger","body_b":"right_finger","contact_count":341.0,"contact_point_centroid":[0.51673,0.02897,0.06561],"force_p95":0.01382,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.0111,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51642,0.02896,0.06335]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1602.0,"contact_point_centroid":[0.51323,0.02873,0.11793],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01288,"mean_force":0.01056,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51287,0.02872,0.11573]},{"body_a":"left_finger","body_b":"right_finger","contact_count":907.0,"contact_point_centroid":[0.59425,0.171,0.193],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01042,"phase_index":5.0,"phase_name":"place_object","phase_type":"descend","tcp_position_centroid":[0.59368,0.17098,0.19075]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2639.0,"contact_point_centroid":[0.55295,0.09999,0.20809],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01265,"mean_force":0.0105,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55251,0.09998,0.2059]}],"total_contact_groups":12},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.53044,0.03079,0.02602],"final_tcp_position":[0.59607,0.17513,0.1319],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":0.23057,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1044.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52242,0.02569,0.17268],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52419,0.02946,0.07272],"tcp_start":[0.52242,0.02569,0.17268],"tcp_to_object_dist_end":0.04714,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2141.0,"raw_peak_contact_force":0.12263,"subtask_id":"grasp_1","tcp_end":[0.51642,0.02896,0.06335],"tcp_start":[0.52419,0.02946,0.07272],"tcp_to_object_dist_end":0.03994,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":380.0,"n_steps_budget":1000.0,"object_pos_end":[0.53044,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18339,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3144.0,"raw_peak_contact_force":0.23057,"tcp_end":[0.51285,0.02872,0.1699],"tcp_start":[0.51642,0.02896,0.06335],"tcp_to_object_dist_end":0.14497,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":622.0,"n_steps_budget":1000.0,"object_pos_end":[0.53044,0.03079,0.02602],"object_pos_start":[0.53044,0.03079,0.02602],"object_to_goal_dist_end":0.18339,"object_to_goal_dist_start":0.18339,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5127.0,"raw_peak_contact_force":0.12263,"subtask_id":"transport_arc","tcp_end":[0.59283,0.16761,0.24413],"tcp_start":[0.51285,0.02872,0.1699],"tcp_to_object_dist_end":0.26492,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":212.0,"n_steps_budget":1000.0,"object_pos_end":[0.53044,0.03079,0.02602],"object_pos_start":[0.53044,0.03079,0.02602],"object_to_goal_dist_end":0.18339,"object_to_goal_dist_start":0.18339,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"place_object","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1755.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.59607,0.17513,0.1319],"tcp_start":[0.59283,0.16761,0.24413],"tcp_to_object_dist_end":0.19066,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```