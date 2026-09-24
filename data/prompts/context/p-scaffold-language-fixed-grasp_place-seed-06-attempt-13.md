## Search State

- **Seed**: 6
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.0287 | 0.20 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 11 | -0.2414 | 0.17 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.0143 | 0.22 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.2622 | 0.71 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0408 | 0.24 | ❌ rejected |

**Proposal policy**: task_score is 0.20 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`
- Frozen object start: [0.5038164351471943, -0.015672913018666156, 0.03]
- Frozen task target: [0.5869067239795378, 0.18744967655878825, 0.24811674852797]
- Goal object position: (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5038164351471943, -0.015672913018666156, 0.03)
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
  frozen_object_start: [0.5038, -0.0157, 0.03]
  frozen_task_target: [0.5869, 0.1874, 0.2481]
  frozen_object_starts: {'grasp_target': [0.5038164351471943, -0.015672913018666156, 0.03]}
  frozen_targets: {'place_target': [0.5869067239795378, 0.18744967655878825, 0.24811674852797]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22

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

## Current Skill (Q=-0.029) — your mutation base

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
    tolerance: 0.01
    orientation:
      mode: keep_current
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
    speed:
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
  control: admittance_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
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
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
- id: transport_arc
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.2
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: place_descend
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **place_descend** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.029
- **task_score** (E): 0.202
- **fitness_score**: 0.571  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.600

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1294 |
| descend_1 | 1.00 | 1.00 | 0.1286 |
| grasp_1 | 1.00 | 1.00 | 0.0115 |
| lift_1 | 0.33 | 1.00 | 0.1063 |
| transport_arc | 1.00 | 1.00 | 0.2496 |
| place_descend | 1.00 | 1.00 | 0.0908 |
| release_1 | 1.00 | 1.00 | 0.0206 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.022, 0.177) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 5.945 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.022, 0.177)→(0.495, 0.024, 0.048) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.024, 0.048)→(0.487, 0.023, 0.040) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 44.000 | 0.144 | 0.200 |
| lift_1 | lift | 0.33 / step_budget | (0.487, 0.023, 0.040)→(0.483, 0.023, 0.146) | (0.500, 0.024, 0.026)→(0.493, 0.023, 0.124) | 0.272→0.224 | 1.00 / 31.000 | 0.094 | 0.493 |
| transport_arc | approach | 1.00 / step_budget | (0.483, 0.023, 0.146)→(0.587, 0.181, 0.305) | (0.493, 0.023, 0.124)→(0.522, 0.058, 0.016) | 0.224→0.251 | 1.00 / 8.000 | 3249.710 | 1.899 |
| place_descend | descend | 1.00 / step_budget | (0.587, 0.181, 0.305)→(0.594, 0.193, 0.216) | (0.522, 0.058, 0.016)→(0.522, 0.058, 0.016) | 0.251→0.251 | 1.00 / 8.667 | 182004.356 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.594, 0.193, 0.216)→(0.589, 0.191, 0.235) | (0.522, 0.058, 0.016)→(0.522, 0.058, 0.016) | 0.251→0.251 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.320
- phase_score: 0.391
- phase_breakdown.descend_1_score: 0.843
- phase_breakdown.transport_arc_score: 0.127
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.074
- phase_breakdown.release_1_score: 0.554
- grasp_place_fitness: 0.635

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.635
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.320
- **Median Q (composite search score)**: -0.055
- **K-run variance**: 0.0021
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.321


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `daf90631fcbaf423e19452d0c9b90b9715013985cc94ef12ca0cd881e96195aa`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `94660347aa4f41f6801e53bd449f8df59691da8bebfa4fef4947a3513fe04781`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.77871,"average_solve_count":357.0,"average_success_count":357.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13221,"approach_1.speed":0.03998,"descend_1.grasp_z_offset":0.02859,"descend_1.speed":0.01914,"lift_1.lift_height":0.13698,"lift_1.speed":0.18276,"place_descend.speed":0.078,"transport_arc.arc_height":0.06136,"transport_arc.speed":0.0393},"optimized_scores":{"best_composite_score":-0.06635,"best_fitness_score":0.53365,"best_task_score":0.14321},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1962.0,"contact_point_centroid":[0.53284,0.01948,-0.00268],"force_p95":0.2303,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.7883,"mean_force":0.1495,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54306,0.10118,0.32512]},{"body_a":"world","body_b":"grasp_target","contact_count":131.0,"contact_point_centroid":[0.50129,-0.01538,-0.0011],"force_p95":0.23369,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45337,"mean_force":0.06209,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48968,-0.01539,0.04886]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8071.0,"contact_point_centroid":[0.49007,0.0036,0.09878],"force_p95":0.10645,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32809,"mean_force":0.06939,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4874,-0.01534,0.09807]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8779.0,"contact_point_centroid":[0.48995,-0.03422,0.09817],"force_p95":0.1015,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30745,"mean_force":0.06457,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4874,-0.01534,0.09749]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3736.0,"contact_point_centroid":[0.49763,0.01624,0.21412],"force_p95":0.15104,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22559,"mean_force":0.09635,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49133,-0.00233,0.21496]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4558.0,"contact_point_centroid":[0.49796,-0.01961,0.21579],"force_p95":0.1286,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18619,"mean_force":0.08032,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49178,-0.00143,0.21691]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01562,-0.00203],"force_p95":0.1319,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15267,"mean_force":0.12522,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4923,-0.01542,0.04839]},{"body_a":"world","body_b":"grasp_target","contact_count":1720.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49884,-0.00674,0.23602]},{"body_a":"world","body_b":"grasp_target","contact_count":3260.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49772,-0.01474,0.10937]},{"body_a":"world","body_b":"grasp_target","contact_count":956.0,"contact_point_centroid":[0.53283,0.01956,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.5797,0.17704,0.29918]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53283,0.01956,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57965,0.1826,0.25681]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4362.0,"contact_point_centroid":[0.49161,0.00378,0.04874],"force_p95":0.07248,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09944,"mean_force":0.04939,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49115,-0.01541,0.04714]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4879.0,"contact_point_centroid":[0.49156,-0.03454,0.04847],"force_p95":0.06832,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0866,"mean_force":0.04462,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49115,-0.01541,0.04714]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1956.0,"contact_point_centroid":[0.54564,0.1056,0.32975],"force_p95":0.01137,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0162,"mean_force":0.01053,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54527,0.1056,0.32754]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1025.0,"contact_point_centroid":[0.58025,0.17709,0.30122],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.0104,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57972,0.17708,0.29895]},{"body_a":"left_finger","body_b":"right_finger","contact_count":218.0,"contact_point_centroid":[0.58198,0.18337,0.2549],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01266,"mean_force":0.01016,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58148,0.18335,0.2527]}],"total_contact_groups":16},"final_pose_error":0.00986,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.53283,0.01956,0.01602],"final_tcp_position":[0.58281,0.1837,0.25626],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273006.6879,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":431.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1720.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49979,-0.01397,0.17114],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14519,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":815.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3260.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49893,-0.01551,0.05565],"tcp_start":[0.49979,-0.01397,0.17114],"tcp_to_object_dist_end":0.03003,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50373,-0.01542,0.02587],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.3122,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13127,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11041.0,"raw_peak_contact_force":0.15267,"subtask_id":"grasp_1","tcp_end":[0.49112,-0.0154,0.04711],"tcp_start":[0.49893,-0.01551,0.05565],"tcp_to_object_dist_end":0.0247,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49935,-0.01542,0.13989],"object_pos_start":[0.50373,-0.01542,0.02587],"object_to_goal_dist_end":0.24604,"object_to_goal_dist_start":0.3122,"object_z_max":0.13973,"peak_contact_force":0.1025,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16981.0,"raw_peak_contact_force":0.45337,"tcp_end":[0.48759,-0.01534,0.16943],"tcp_start":[0.49112,-0.0154,0.04711],"tcp_to_object_dist_end":0.03179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":978.0,"n_steps_budget":1000.0,"object_pos_end":[0.53283,0.01956,0.01602],"object_pos_start":[0.49935,-0.01542,0.13989],"object_to_goal_dist_end":0.29151,"object_to_goal_dist_start":0.24604,"object_z_max":0.23196,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12212.0,"raw_peak_contact_force":1.7883,"subtask_id":"transport_arc","tcp_end":[0.57787,0.1712,0.34151],"tcp_start":[0.48759,-0.01534,0.16943],"tcp_to_object_dist_end":0.36189,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":239.0,"n_steps_budget":1000.0,"object_pos_end":[0.53283,0.01956,0.01602],"object_pos_start":[0.53283,0.01956,0.01602],"object_to_goal_dist_end":0.29151,"object_to_goal_dist_start":0.29151,"object_z_max":0.01602,"peak_contact_force":273006.6879,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1981.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.58281,0.1837,0.25626],"tcp_start":[0.57787,0.1712,0.34151],"tcp_to_object_dist_end":0.29522,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53283,0.01956,0.01602],"object_pos_start":[0.53283,0.01956,0.01602],"object_to_goal_dist_end":0.29151,"object_to_goal_dist_start":0.29151,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57864,0.18216,0.27661],"tcp_start":[0.58281,0.1837,0.25626],"tcp_to_object_dist_end":0.31055,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fe7e0be33c0bb4db9d2bbbb069b6113d0e5a69a675a0d70bc1f582243e99e3cf`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26374,"average_solve_count":273.0,"average_success_count":273.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12227,"approach_1.speed":0.03414,"descend_1.grasp_z_offset":0.01908,"descend_1.speed":0.0354,"lift_1.lift_height":0.16523,"lift_1.speed":0.06467,"place_descend.speed":0.04872,"transport_arc.arc_height":0.16822,"transport_arc.speed":0.13396},"optimized_scores":{"best_composite_score":0.03544,"best_fitness_score":0.63544,"best_task_score":0.31998},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1104.0,"contact_point_centroid":[0.54163,0.10008,-0.00314],"force_p95":0.50579,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.01735,"mean_force":0.17677,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.57414,0.11975,0.2555]},{"body_a":"world","body_b":"grasp_target","contact_count":176.0,"contact_point_centroid":[0.50927,0.03786,-0.00121],"force_p95":0.34661,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5583,"mean_force":0.08808,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4979,0.0384,0.03614]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17313.0,"contact_point_centroid":[0.49702,0.05722,0.08445],"force_p95":0.08682,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3172,"mean_force":0.05892,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49538,0.0382,0.08284]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17185.0,"contact_point_centroid":[0.49698,0.01921,0.08603],"force_p95":0.08706,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31233,"mean_force":0.05881,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49536,0.0382,0.08421]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3029.0,"contact_point_centroid":[0.5051,0.06361,0.17959],"force_p95":0.14687,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28394,"mean_force":0.09227,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49989,0.04505,0.18001]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3126.0,"contact_point_centroid":[0.50464,0.02632,0.17922],"force_p95":0.14951,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26592,"mean_force":0.09006,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49957,0.04477,0.17976]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51254,0.03949,-0.0021],"force_p95":0.15274,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21955,"mean_force":0.1307,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50082,0.03865,0.03569]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4079.0,"contact_point_centroid":[0.50009,0.01932,0.0372],"force_p95":0.08067,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14355,"mean_force":0.05195,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49964,0.03855,0.03439]},{"body_a":"world","body_b":"grasp_target","contact_count":2000.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13259,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50261,0.01746,0.22989]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50628,0.03786,0.08573]},{"body_a":"world","body_b":"grasp_target","contact_count":1112.0,"contact_point_centroid":[0.54175,0.10035,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61612,0.16378,0.19862]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54175,0.10035,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6167,0.16786,0.15179]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5170.0,"contact_point_centroid":[0.4998,0.05767,0.03658],"force_p95":0.06957,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08165,"mean_force":0.04304,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49964,0.03855,0.0344]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1002.0,"contact_point_centroid":[0.58011,0.12529,0.25866],"force_p95":0.01273,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01586,"mean_force":0.01073,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.57963,0.12527,0.25637]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1172.0,"contact_point_centroid":[0.61651,0.1638,0.20103],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01056,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61611,0.16377,0.19869]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.62018,0.16881,0.15051],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.01007,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61955,0.16878,0.14821]}],"total_contact_groups":16},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.54175,0.10035,0.01602],"final_tcp_position":[0.62139,0.16924,0.15207],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":273006.25813,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":501.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2000.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50764,0.03588,0.15992],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13404,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50753,0.0392,0.04308],"tcp_start":[0.50764,0.03588,0.15992],"tcp_to_object_dist_end":0.01778,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51242,0.03856,0.02564],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2132,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14774,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11049.0,"raw_peak_contact_force":0.21955,"subtask_id":"grasp_1","tcp_end":[0.49961,0.03855,0.03436],"tcp_start":[0.50753,0.0392,0.04308],"tcp_to_object_dist_end":0.0155,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50607,0.03812,0.12111],"object_pos_start":[0.51242,0.03856,0.02564],"object_to_goal_dist_end":0.18275,"object_to_goal_dist_start":0.2132,"object_z_max":0.12099,"peak_contact_force":0.11017,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34674.0,"raw_peak_contact_force":0.5583,"tcp_end":[0.49544,0.03822,0.13941],"tcp_start":[0.49961,0.03855,0.03436],"tcp_to_object_dist_end":0.02116,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":667.0,"n_steps_budget":1000.0,"object_pos_end":[0.54175,0.10035,0.01602],"object_pos_start":[0.50607,0.03812,0.12111],"object_to_goal_dist_end":0.17092,"object_to_goal_dist_start":0.18275,"object_z_max":0.20072,"peak_contact_force":9748.88357,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8261.0,"raw_peak_contact_force":2.01735,"subtask_id":"transport_arc","tcp_end":[0.61319,0.15916,0.24628],"tcp_start":[0.49544,0.03822,0.13941],"tcp_to_object_dist_end":0.24816,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":278.0,"n_steps_budget":1000.0,"object_pos_end":[0.54175,0.10035,0.01602],"object_pos_start":[0.54175,0.10035,0.01602],"object_to_goal_dist_end":0.17092,"object_to_goal_dist_start":0.17092,"object_z_max":0.01602,"peak_contact_force":273006.25813,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2284.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.62139,0.16924,0.15207],"tcp_start":[0.61319,0.15916,0.24628],"tcp_to_object_dist_end":0.17204,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54175,0.10035,0.01602],"object_pos_start":[0.54175,0.10035,0.01602],"object_to_goal_dist_end":0.17092,"object_to_goal_dist_start":0.17092,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.615,0.1673,0.17123],"tcp_start":[0.62139,0.16924,0.15207],"tcp_to_object_dist_end":0.18422,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `28f75809d7d1d0a11ca1a36dd459ad950e5a80b6bae34006f33ac9620425f5e5`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15358,"average_solve_count":293.0,"average_success_count":293.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16094,"approach_1.speed":0.06241,"descend_1.grasp_z_offset":0.01512,"descend_1.speed":0.02601,"lift_1.lift_height":0.20582,"lift_1.speed":0.01435,"place_descend.speed":0.06665,"transport_arc.arc_height":0.22932,"transport_arc.speed":0.14755},"optimized_scores":{"best_composite_score":-0.05506,"best_fitness_score":0.54494,"best_task_score":0.14382},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1944.0,"contact_point_centroid":[0.49138,0.05435,-0.00262],"force_p95":0.2261,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.8912,"mean_force":0.14988,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5194,0.13229,0.31744]},{"body_a":"world","body_b":"grasp_target","contact_count":183.0,"contact_point_centroid":[0.47771,0.04635,-0.00127],"force_p95":0.39841,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46876,"mean_force":0.10666,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46878,0.047,0.03917]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4129.0,"contact_point_centroid":[0.46473,0.06198,0.17501],"force_p95":0.13199,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30634,"mean_force":0.07489,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46166,0.043,0.17369]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4557.0,"contact_point_centroid":[0.46508,0.02448,0.17869],"force_p95":0.11405,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29842,"mean_force":0.06952,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.4617,0.04313,0.17779]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20940.0,"contact_point_centroid":[0.46612,0.06596,0.08455],"force_p95":0.07078,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27148,"mean_force":0.04894,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46637,0.04678,0.0829]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20819.0,"contact_point_centroid":[0.46618,0.02761,0.08594],"force_p95":0.07139,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23498,"mean_force":0.04841,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46637,0.04678,0.08386]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48274,0.04855,-0.00213],"force_p95":0.15983,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22823,"mean_force":0.13261,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47158,0.04729,0.03872]},{"body_a":"world","body_b":"grasp_target","contact_count":1444.0,"contact_point_centroid":[0.4827,0.04873,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49014,0.02046,0.24965]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5038.0,"contact_point_centroid":[0.47022,0.02793,0.04034],"force_p95":0.0695,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12585,"mean_force":0.04299,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47046,0.04718,0.03757]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47817,0.04526,0.11772]},{"body_a":"world","body_b":"grasp_target","contact_count":1036.0,"contact_point_centroid":[0.4913,0.05447,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57336,0.21826,0.28348]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.4913,0.05447,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57407,0.2235,0.2389]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5505.0,"contact_point_centroid":[0.47004,0.06649,0.03975],"force_p95":0.06947,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07422,"mean_force":0.04096,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47047,0.04718,0.03758]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1900.0,"contact_point_centroid":[0.52329,0.13773,0.32322],"force_p95":0.0116,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01654,"mean_force":0.01061,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52289,0.13771,0.321]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1098.0,"contact_point_centroid":[0.5738,0.2183,0.2855],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01052,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57337,0.21827,0.28336]},{"body_a":"left_finger","body_b":"right_finger","contact_count":227.0,"contact_point_centroid":[0.57682,0.2245,0.23756],"force_p95":0.01085,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01252,"mean_force":0.00984,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.576,0.22445,0.23491]}],"total_contact_groups":16},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.4913,0.05447,0.01602],"final_tcp_position":[0.57737,0.22494,0.2385],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":17.58876,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":362.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":17.58876,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1444.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48147,0.04266,0.19867],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47807,0.04792,0.04543],"tcp_start":[0.48147,0.04266,0.19867],"tcp_to_object_dist_end":0.01997,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48264,0.04752,0.02553],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29109,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.1544,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12343.0,"raw_peak_contact_force":0.22823,"subtask_id":"grasp_1","tcp_end":[0.47043,0.04717,0.03754],"tcp_start":[0.47807,0.04792,0.04543],"tcp_to_object_dist_end":0.01712,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47288,0.04678,0.11029],"object_pos_start":[0.48264,0.04752,0.02553],"object_to_goal_dist_end":0.24388,"object_to_goal_dist_start":0.29109,"object_z_max":0.11022,"peak_contact_force":0.06789,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41942.0,"raw_peak_contact_force":0.46876,"tcp_end":[0.46646,0.0468,0.12872],"tcp_start":[0.47043,0.04717,0.03754],"tcp_to_object_dist_end":0.01952,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":905.0,"n_steps_budget":1000.0,"object_pos_end":[0.4913,0.05447,0.01602],"object_pos_start":[0.47288,0.04678,0.11029],"object_to_goal_dist_end":0.29088,"object_to_goal_dist_start":0.24388,"object_z_max":0.21453,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12530.0,"raw_peak_contact_force":1.8912,"subtask_id":"transport_arc","tcp_end":[0.57082,0.21249,0.32852],"tcp_start":[0.46646,0.0468,0.12872],"tcp_to_object_dist_end":0.3591,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":259.0,"n_steps_budget":1000.0,"object_pos_end":[0.4913,0.05447,0.01602],"object_pos_start":[0.4913,0.05447,0.01602],"object_to_goal_dist_end":0.29088,"object_to_goal_dist_start":0.29088,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2134.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57737,0.22494,0.2385],"tcp_start":[0.57082,0.21249,0.32852],"tcp_to_object_dist_end":0.2932,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4913,0.05447,0.01602],"object_pos_start":[0.4913,0.05447,0.01602],"object_to_goal_dist_end":0.29088,"object_to_goal_dist_start":0.29088,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.573,0.22294,0.25864],"tcp_start":[0.57737,0.22494,0.2385],"tcp_to_object_dist_end":0.30646,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```