## Search State

- **Seed**: 0
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0188 | 0.35 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 11 | 0.3380 | 1.00 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 8 | 0.3499 | 0.73 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.1187 | 0.21 | ✅ accepted |
| 2 | insert → approach → push → retract → lift → insert → push | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | force_threshold_switch | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 8 | -0.1713 | 0.18 | ✅ accepted |

**Proposal policy**: task_score is 0.35 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`
- Frozen object start: [0.5136961687321454, -0.02302132862361297, 0.03]
- Frozen task target: [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]
- Goal object position: (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5136961687321454, -0.02302132862361297, 0.03)
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
  frozen_object_start: [0.5137, -0.023, 0.03]
  frozen_task_target: [0.5541, 0.1517, 0.222]
  frozen_object_starts: {'grasp_target': [0.5136961687321454, -0.02302132862361297, 0.03]}
  frozen_targets: {'place_target': [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea

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

## Current Skill (Q=-0.019) — your mutation base

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
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
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
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.02
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
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
    - 0.2
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
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
    - 0.0
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    transport_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    transport_x_offset:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    transport_y_offset:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
    transport_z_offset:
      type: scalar
      range:
      - 0.0
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
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15]
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02]
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.2]
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - transport_x_offset: status=consumed; consumers=target.offset.x (replace)
    - transport_y_offset: status=consumed; consumers=target.offset.y (replace)
    - transport_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: -0.019
- **task_score** (E): 0.347
- **fitness_score**: 0.651  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.670

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0661 |
| descend_1 | 1.00 | 1.00 | 0.2033 |
| grasp_1 | 1.00 | 1.00 | 0.0124 |
| lift_1 | 0.33 | 1.00 | 0.1257 |
| transport_to_goal | 1.00 | 1.00 | 0.2206 |
| release_1 | 1.00 | 1.00 | 0.0215 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.003, 0.242) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.003, 0.242)→(0.492, 0.001, 0.039) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.492, 0.001, 0.039)→(0.483, 0.000, 0.030) | (0.497, 0.001, 0.026)→(0.497, 0.000, 0.026) | 0.265→0.266 | 1.00 / 42.667 | 0.147 | 0.192 |
| lift_1 | lift | 0.33 / step_budget | (0.483, 0.000, 0.030)→(0.480, 0.000, 0.155) | (0.497, 0.000, 0.026)→(0.489, 0.000, 0.143) | 0.266→0.217 | 1.00 / 37.000 | 0.081 | 0.653 |
| transport_to_goal | approach | 1.00 / step_budget | (0.480, 0.000, 0.155)→(0.603, 0.177, 0.185) | (0.489, 0.000, 0.143)→(0.603, 0.178, 0.169) | 0.217→0.030 | 1.00 / 39.333 | 0.075 | 0.161 |
| release_1 | release | 1.00 / step_budget | (0.603, 0.177, 0.185)→(0.598, 0.175, 0.206) | (0.603, 0.178, 0.169)→(0.593, 0.172, 0.025) | 0.030→0.162 | 1.00 / 3.000 | 0.126 | 1.385 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.449
- phase_score: 0.668
- phase_breakdown.release_1_score: 0.486
- phase_breakdown.approach_1_score: 0.052
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.671
- phase_breakdown.descend_1_score: 0.733
- grasp_place_fitness: 0.702

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.702
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.449
- **Median Q (composite search score)**: -0.025
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at upper bound**: transport_to_goal.transport_x_offset
- **Final σ (mean)**: 0.366


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `096c354712624ed6bd8f9b9cbbbc2b7d35a94d9c1517cfb8353e2e383be5aaf0`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3798aa6551d21849355469c7d63897f628ac7de9267c18bb4301fe6cfaae0164`; realized-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5137,-0.02302,0.03]},{"name":"goal","value":[0.5541,0.15165,0.22199]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5137,-0.02302,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5541,0.15165,0.22199]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58084,"average_solve_count":167.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.23227,"approach_1.approach_speed":0.02852,"descend_1.descend_speed":0.06655,"descend_1.grasp_z_offset":0.00642,"lift_1.lift_height":0.18996,"lift_1.lift_speed":0.0923,"transport_to_goal.transport_speed":0.17089,"transport_to_goal.transport_tolerance":0.01629,"transport_to_goal.transport_x_offset":0.03726,"transport_to_goal.transport_y_offset":-0.01211,"transport_to_goal.transport_z_offset":0.0009},"optimized_scores":{"best_composite_score":-0.06371,"best_fitness_score":0.60629,"best_task_score":0.25999},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":193.0,"contact_point_centroid":[0.56631,0.12403,-0.00768],"force_p95":1.25693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.71122,"mean_force":0.38786,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57782,0.12897,0.22725]},{"body_a":"world","body_b":"grasp_target","contact_count":150.0,"contact_point_centroid":[0.51009,-0.02214,-0.00114],"force_p95":0.43971,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65319,"mean_force":0.1052,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49812,-0.02238,0.03313]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17222.0,"contact_point_centroid":[0.49584,-0.0415,0.10624],"force_p95":0.08019,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33402,"mean_force":0.05806,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49554,-0.02232,0.10348]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20680.0,"contact_point_centroid":[0.49703,-0.00335,0.10411],"force_p95":0.0746,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32924,"mean_force":0.04986,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49555,-0.02232,0.10239]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1216.0,"contact_point_centroid":[0.57753,0.14862,0.21276],"force_p95":0.0696,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2009,"mean_force":0.04324,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58131,0.12995,0.21003]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51371,-0.02308,-0.00205],"force_p95":0.14001,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17162,"mean_force":0.12693,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.501,-0.02243,0.03276]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1236.0,"contact_point_centroid":[0.58505,0.11101,0.21105],"force_p95":0.06979,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16379,"mean_force":0.04197,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58129,0.12994,0.20999]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12398.0,"contact_point_centroid":[0.54166,0.03786,0.19633],"force_p95":0.07171,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15287,"mean_force":0.04897,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53985,0.05696,0.19466]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12551.0,"contact_point_centroid":[0.53794,0.07556,0.19692],"force_p95":0.0697,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15204,"mean_force":0.04791,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53963,0.0566,0.19455]},{"body_a":"world","body_b":"grasp_target","contact_count":604.0,"contact_point_centroid":[0.5137,-0.02302,-0.00179],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12343,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50281,-0.00782,0.28374]},{"body_a":"world","body_b":"grasp_target","contact_count":2912.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50667,-0.01968,0.15264]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5309.0,"contact_point_centroid":[0.50069,-0.00335,0.03333],"force_p95":0.06736,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10874,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49976,-0.02241,0.03142]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4170.0,"contact_point_centroid":[0.4991,-0.04168,0.03427],"force_p95":0.07968,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08764,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49976,-0.02241,0.03142]}],"total_contact_groups":13},"final_pose_error":0.01629,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.57329,0.12733,0.02231],"final_tcp_position":[0.58277,0.12989,0.21298],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":1.71122,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":152.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":604.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50734,-0.01686,0.26689],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.24103,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":728.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2912.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.5084,-0.02256,0.04086],"tcp_start":[0.50734,-0.01686,0.26689],"tcp_to_object_dist_end":0.01577,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51358,-0.02286,0.0258],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26568,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.13977,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11279.0,"raw_peak_contact_force":0.17162,"subtask_id":"grasp_1","tcp_end":[0.49973,-0.02241,0.03138],"tcp_start":[0.5084,-0.02256,0.04086],"tcp_to_object_dist_end":0.01494,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50554,-0.02293,0.16573],"object_pos_start":[0.51358,-0.02286,0.0258],"object_to_goal_dist_end":0.18974,"object_to_goal_dist_start":0.26568,"object_z_max":0.16556,"peak_contact_force":0.08274,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38052.0,"raw_peak_contact_force":0.65319,"tcp_end":[0.49596,-0.02232,0.17916],"tcp_start":[0.49973,-0.02241,0.03138],"tcp_to_object_dist_end":0.0165,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":607.0,"n_steps_budget":1000.0,"object_pos_end":[0.58402,0.13075,0.1969],"object_pos_start":[0.50554,-0.02293,0.16573],"object_to_goal_dist_end":0.04429,"object_to_goal_dist_start":0.18974,"object_z_max":0.19687,"peak_contact_force":0.07005,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24949.0,"raw_peak_contact_force":0.15287,"subtask_id":"transport_arc","tcp_end":[0.58277,0.12989,0.21298],"tcp_start":[0.49596,-0.02232,0.17916],"tcp_to_object_dist_end":0.01615,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57329,0.12733,0.02231],"object_pos_start":[0.58402,0.13075,0.1969],"object_to_goal_dist_end":0.20207,"object_to_goal_dist_start":0.04429,"object_z_max":0.1969,"peak_contact_force":0.16493,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2645.0,"raw_peak_contact_force":1.71122,"subtask_id":"release_1","tcp_end":[0.57777,0.12897,0.23481],"tcp_start":[0.58277,0.12989,0.21298],"tcp_to_object_dist_end":0.21255,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `ed2df336ade3d991e9495251c8398520a59dd014a70bd2d7bb71dc7aefccaa8a`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27094,"average_solve_count":203.0,"average_success_count":203.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13983,"approach_1.approach_speed":0.04758,"descend_1.descend_speed":0.05201,"descend_1.grasp_z_offset":0.00118,"lift_1.lift_height":0.25903,"lift_1.lift_speed":0.06453,"transport_to_goal.transport_speed":0.10653,"transport_to_goal.transport_tolerance":0.01798,"transport_to_goal.transport_x_offset":0.0232,"transport_to_goal.transport_y_offset":0.01026,"transport_to_goal.transport_z_offset":0.02369},"optimized_scores":{"best_composite_score":0.03231,"best_fitness_score":0.70231,"best_task_score":0.44874},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":197.0,"contact_point_centroid":[0.56394,0.23591,-0.0071],"force_p95":1.22044,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.32038,"mean_force":0.36099,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5732,0.24101,0.17131]},{"body_a":"world","body_b":"grasp_target","contact_count":171.0,"contact_point_centroid":[0.49605,0.04172,-0.00121],"force_p95":0.47733,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68687,"mean_force":0.11749,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48563,0.04322,0.02826]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.48308,0.0622,0.08173],"force_p95":0.08376,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31643,"mean_force":0.05864,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48299,0.043,0.07899]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20791.0,"contact_point_centroid":[0.48498,0.02408,0.0797],"force_p95":0.07869,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29211,"mean_force":0.04937,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48298,0.043,0.07818]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50127,0.04492,-0.00215],"force_p95":0.16535,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23376,"mean_force":0.13389,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48861,0.04351,0.02764]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1101.0,"contact_point_centroid":[0.57043,0.26041,0.16281],"force_p95":0.07803,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23182,"mean_force":0.04741,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57709,0.24285,0.15738]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4997.0,"contact_point_centroid":[0.48922,0.02441,0.02773],"force_p95":0.07634,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18967,"mean_force":0.04311,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48737,0.04339,0.02634]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1355.0,"contact_point_centroid":[0.58284,0.2244,0.15785],"force_p95":0.06997,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18495,"mean_force":0.03976,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57708,0.24284,0.15736]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15623.0,"contact_point_centroid":[0.53667,0.12949,0.14556],"force_p95":0.07675,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1455,"mean_force":0.05028,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53177,0.14786,0.14508]},{"body_a":"world","body_b":"grasp_target","contact_count":1748.0,"contact_point_centroid":[0.50118,0.04505,-0.00192],"force_p95":0.13393,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49769,0.01939,0.23902]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12893.0,"contact_point_centroid":[0.52827,0.16553,0.14841],"force_p95":0.08961,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12957,"mean_force":0.05929,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53128,0.14686,0.14492]},{"body_a":"world","body_b":"grasp_target","contact_count":1936.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49524,0.04201,0.10594]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4245.0,"contact_point_centroid":[0.48756,0.06273,0.02903],"force_p95":0.08438,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09785,"mean_force":0.05197,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48738,0.0434,0.02635]}],"total_contact_groups":13},"final_pose_error":0.01792,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.5659,0.23656,0.02687],"final_tcp_position":[0.57877,0.24309,0.16056],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.32038,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":438.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1748.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49744,0.04012,0.17768],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":484.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1936.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49595,0.04416,0.03542],"tcp_start":[0.49744,0.04012,0.17768],"tcp_to_object_dist_end":0.01079,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50116,0.0439,0.02549],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.2431,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16226,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11042.0,"raw_peak_contact_force":0.23376,"subtask_id":"grasp_1","tcp_end":[0.48734,0.04339,0.02631],"tcp_start":[0.49595,0.04416,0.03542],"tcp_to_object_dist_end":0.01385,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49373,0.04393,0.12279],"object_pos_start":[0.50116,0.0439,0.02549],"object_to_goal_dist_end":0.21435,"object_to_goal_dist_start":0.2431,"object_z_max":0.12267,"peak_contact_force":0.08107,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37962.0,"raw_peak_contact_force":0.68687,"tcp_end":[0.48318,0.04302,0.13226],"tcp_start":[0.48734,0.04339,0.02631],"tcp_to_object_dist_end":0.01421,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":764.0,"n_steps_budget":1000.0,"object_pos_end":[0.5806,0.24526,0.14611],"object_pos_start":[0.49373,0.04393,0.12279],"object_to_goal_dist_end":0.0162,"object_to_goal_dist_start":0.21435,"object_z_max":0.14608,"peak_contact_force":0.07895,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28516.0,"raw_peak_contact_force":0.1455,"subtask_id":"transport_arc","tcp_end":[0.57877,0.24309,0.16056],"tcp_start":[0.48318,0.04302,0.13226],"tcp_to_object_dist_end":0.01473,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5659,0.23656,0.02687],"object_pos_start":[0.5806,0.24526,0.14611],"object_to_goal_dist_end":0.1202,"object_to_goal_dist_start":0.0162,"object_z_max":0.14611,"peak_contact_force":0.12884,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2653.0,"raw_peak_contact_force":1.32038,"subtask_id":"release_1","tcp_end":[0.57312,0.24098,0.18162],"tcp_start":[0.57877,0.24309,0.16056],"tcp_to_object_dist_end":0.15498,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `291bc6f2bd023fc25503740a7343328e565e43fc71fa3c9c5d2fdbe2d4351fd2`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3105,"average_solve_count":219.0,"average_success_count":219.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.24719,"approach_1.approach_speed":0.09474,"descend_1.descend_speed":0.02433,"descend_1.grasp_z_offset":0.00472,"lift_1.lift_height":0.2346,"lift_1.lift_speed":0.07526,"transport_to_goal.transport_speed":0.13548,"transport_to_goal.transport_tolerance":0.01645,"transport_to_goal.transport_x_offset":0.05,"transport_to_goal.transport_y_offset":0.02562,"transport_to_goal.transport_z_offset":0.0067},"optimized_scores":{"best_composite_score":-0.0251,"best_fitness_score":0.6449,"best_task_score":0.3336},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":241.0,"contact_point_centroid":[0.63905,0.15311,-0.00633],"force_p95":0.93,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.1232,"mean_force":0.29363,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64281,0.15558,0.19241]},{"body_a":"world","body_b":"grasp_target","contact_count":150.0,"contact_point_centroid":[0.47213,-0.01892,-0.00121],"force_p95":0.36609,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61748,"mean_force":0.09498,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4618,-0.01953,0.03276]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1177.0,"contact_point_centroid":[0.64305,0.1754,0.18179],"force_p95":0.07143,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31437,"mean_force":0.0453,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.64673,0.15676,0.17837]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21004.0,"contact_point_centroid":[0.46045,-0.00043,0.09337],"force_p95":0.07228,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30773,"mean_force":0.04866,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45922,-0.01947,0.09159]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18501.0,"contact_point_centroid":[0.45919,-0.03865,0.09431],"force_p95":0.07763,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30557,"mean_force":0.054,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45921,-0.01947,0.09156]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1248.0,"contact_point_centroid":[0.65053,0.13785,0.17902],"force_p95":0.0699,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25089,"mean_force":0.04258,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6467,0.15675,0.17831]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19972.0,"contact_point_centroid":[0.55909,0.05382,0.16838],"force_p95":0.07166,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18389,"mean_force":0.05009,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55688,0.07285,0.167]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19973.0,"contact_point_centroid":[0.5547,0.09147,0.16941],"force_p95":0.07016,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17944,"mean_force":0.04942,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55655,0.07256,0.16694]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02017,-0.00205],"force_p95":0.1389,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1702,"mean_force":0.12649,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46461,-0.01958,0.03238]},{"body_a":"world","body_b":"grasp_target","contact_count":412.0,"contact_point_centroid":[0.47616,-0.02015,-0.0017],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12384,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4913,-0.00589,0.29069]},{"body_a":"world","body_b":"grasp_target","contact_count":3260.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47578,-0.01636,0.1589]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5066.0,"contact_point_centroid":[0.46454,-0.00047,0.03272],"force_p95":0.06773,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10876,"mean_force":0.04309,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46341,-0.01955,0.0312]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4414.0,"contact_point_centroid":[0.46295,-0.03881,0.03393],"force_p95":0.07748,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08889,"mean_force":0.04913,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46341,-0.01955,0.0312]}],"total_contact_groups":13},"final_pose_error":0.0456,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.6385,0.15333,0.0256],"final_tcp_position":[0.64847,0.15685,0.18216],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.1232,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":104.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.1223,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":412.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48207,-0.0131,0.28057],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25472,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":815.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3260.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.47174,-0.01968,0.03951],"tcp_start":[0.48207,-0.0131,0.28057],"tcp_to_object_dist_end":0.0142,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47605,-0.01992,0.02582],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28841,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13878,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11280.0,"raw_peak_contact_force":0.1702,"subtask_id":"grasp_1","tcp_end":[0.46338,-0.01955,0.03117],"tcp_start":[0.47174,-0.01968,0.03951],"tcp_to_object_dist_end":0.01375,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4687,-0.01999,0.14167],"object_pos_start":[0.47605,-0.01992,0.02582],"object_to_goal_dist_end":0.24682,"object_to_goal_dist_start":0.28841,"object_z_max":0.14156,"peak_contact_force":0.07975,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39655.0,"raw_peak_contact_force":0.61748,"tcp_end":[0.45952,-0.01947,0.15436],"tcp_start":[0.46338,-0.01955,0.03117],"tcp_to_object_dist_end":0.01567,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.64512,0.15726,0.16437],"object_pos_start":[0.4687,-0.01999,0.14167],"object_to_goal_dist_end":0.02914,"object_to_goal_dist_start":0.24682,"object_z_max":0.16436,"peak_contact_force":0.07467,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":39945.0,"raw_peak_contact_force":0.18389,"subtask_id":"transport_arc","tcp_end":[0.64847,0.15685,0.18216],"tcp_start":[0.45952,-0.01947,0.15436],"tcp_to_object_dist_end":0.0181,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6385,0.15333,0.0256],"object_pos_start":[0.64512,0.15726,0.16437],"object_to_goal_dist_end":0.16467,"object_to_goal_dist_start":0.02914,"object_z_max":0.16437,"peak_contact_force":0.08369,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2666.0,"raw_peak_contact_force":1.1232,"subtask_id":"release_1","tcp_end":[0.64275,0.15557,0.20146],"tcp_start":[0.64847,0.15685,0.18216],"tcp_to_object_dist_end":0.17593,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```