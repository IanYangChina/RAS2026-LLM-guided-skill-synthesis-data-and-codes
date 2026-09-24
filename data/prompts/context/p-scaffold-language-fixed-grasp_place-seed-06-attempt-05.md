## Search State

- **Seed**: 6
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.0328 | 0.18 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.0095 | 0.37 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0159 | 0.28 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0726 | 0.24 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1345 | 0.25 | ✅ accepted |

**Proposal policy**: task_score is 0.18 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.033) — your mutation base

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

- **Composite score**: -0.033
- **task_score** (E): 0.177
- **fitness_score**: 0.567  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.600

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1275 |
| descend_1 | 1.00 | 1.00 | 0.1414 |
| grasp_1 | 1.00 | 1.00 | 0.0115 |
| lift_1 | 1.00 | 0.67 | 0.1642 |
| transport_arc | 0.00 | 1.00 | 0.1502 |
| place_descend | 0.00 | 1.00 | 0.0876 |
| release_1 | 1.00 | 1.00 | 0.0276 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.022, 0.178) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.022, 0.178)→(0.495, 0.024, 0.037) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.024, 0.037)→(0.487, 0.023, 0.029) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 43.000 | 0.143 | 0.210 |
| lift_1 | lift | 1.00 / step_budget | (0.487, 0.023, 0.029)→(0.484, 0.023, 0.193) | (0.500, 0.024, 0.026)→(0.500, 0.025, 0.168) | 0.272→0.210 | 0.67 / 12.000 | 0.101 | 0.739 |
| transport_arc | approach | 0.00 / step_budget | (0.484, 0.023, 0.193)→(0.409, 0.076, 0.103) | (0.500, 0.025, 0.168)→(0.503, 0.035, 0.015) | 0.210→0.272 | 1.00 / 9.667 | 3421.952 | 974.518 |
| place_descend | descend | 0.00 / step_budget | (0.409, 0.076, 0.103)→(0.478, 0.118, 0.123) | (0.503, 0.035, 0.015)→(0.509, 0.035, 0.019) | 0.272→0.267 | 1.00 / 9.000 | 3494.120 | 377.264 |
| release_1 | release | 1.00 / step_budget | (0.478, 0.118, 0.123)→(0.476, 0.119, 0.151) | (0.509, 0.035, 0.019)→(0.509, 0.035, 0.019) | 0.267→0.267 | 1.00 / 4.333 | 65.085 | 156.659 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.262
- phase_score: 0.244
- phase_breakdown.descend_1_score: 0.700
- phase_breakdown.transport_arc_score: 0.021
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.065
- phase_breakdown.release_1_score: 0.061
- grasp_place_fitness: 0.610

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.610
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.262
- **Median Q (composite search score)**: -0.054
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.282


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9548,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14131,"approach_1.speed":0.06381,"descend_1.grasp_z_offset":0.01104,"descend_1.speed":0.05205,"lift_1.lift_height":0.15517,"lift_1.speed":0.16272,"place_descend.speed":0.0545,"transport_arc.arc_height":0.15669,"transport_arc.speed":0.08312},"optimized_scores":{"best_composite_score":-0.05351,"best_fitness_score":0.54649,"best_task_score":0.13527},"replay_outcomes":[{"contacts":{"omitted_contact_groups":13,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":216.0,"contact_point_centroid":[0.52857,-0.06571,-0.0015],"force_p95":534.99806,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1032.94432,"mean_force":141.00715,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48256,-0.03716,-0.00328]},{"body_a":"world","body_b":"link7","contact_count":810.0,"contact_point_centroid":[0.56587,-0.04039,-0.00012],"force_p95":239.95459,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":337.16233,"mean_force":188.47507,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.44354,-0.04853,0.01026]},{"body_a":"world","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.54558,-0.03613,-3e-05],"force_p95":264.57052,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":264.90952,"mean_force":261.51945,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.38527,-0.05167,0.0432]},{"body_a":"world","body_b":"link6","contact_count":15.0,"contact_point_centroid":[0.57914,-0.02631,-7e-05],"force_p95":116.31753,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":121.00268,"mean_force":86.03456,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.38398,-0.05133,0.04565]},{"body_a":"world","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.54322,-0.03552,-2e-05],"force_p95":43.60615,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":46.22591,"mean_force":26.56446,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.38431,-0.0516,0.04459]},{"body_a":"world","body_b":"left_finger","contact_count":6548.0,"contact_point_centroid":[0.4731,-0.0578,-0.00355],"force_p95":5.79053,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":36.87965,"mean_force":2.61634,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46877,-0.04219,0.00116]},{"body_a":"world","body_b":"right_finger","contact_count":6221.0,"contact_point_centroid":[0.47209,-0.02548,-0.00361],"force_p95":5.81393,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":36.76198,"mean_force":2.65197,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.47002,-0.04179,0.00085]},{"body_a":"grasp_target","body_b":"link7","contact_count":843.0,"contact_point_centroid":[0.55701,-0.01927,0.02498],"force_p95":0.81075,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.68967,"mean_force":0.57447,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.4438,-0.04834,0.01038]},{"body_a":"grasp_target","body_b":"hand","contact_count":923.0,"contact_point_centroid":[0.54736,-0.0204,0.02776],"force_p95":1.52133,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.68269,"mean_force":0.96932,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.44992,-0.04648,0.00809]},{"body_a":"world","body_b":"grasp_target","contact_count":3064.0,"contact_point_centroid":[0.55819,-0.01682,-0.00805],"force_p95":0.89131,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.08236,"mean_force":0.53048,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.45245,-0.04542,0.00793]},{"body_a":"grasp_target","body_b":"link6","contact_count":148.0,"contact_point_centroid":[0.56654,-0.00259,0.02672],"force_p95":1.42609,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.60399,"mean_force":0.42914,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.40549,-0.05319,0.02751]},{"body_a":"grasp_target","body_b":"link7","contact_count":768.0,"contact_point_centroid":[0.5339,-0.01177,0.02443],"force_p95":0.86028,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.07931,"mean_force":0.5292,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.4054,-0.0228,0.06203]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":574.0,"contact_point_centroid":[0.52837,0.00142,0.14925],"force_p95":0.4628,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.84362,"mean_force":0.21046,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52325,-0.01806,0.15129]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5347,-0.00041,-0.00348],"force_p95":0.39081,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76281,"mean_force":0.22543,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.41166,-0.01543,0.06748]},{"body_a":"world","body_b":"grasp_target","contact_count":120.0,"contact_point_centroid":[0.50101,-0.01534,-0.00109],"force_p95":0.46033,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72021,"mean_force":0.07782,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48946,-0.01542,0.03098]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":578.0,"contact_point_centroid":[0.52874,-0.03599,0.15396],"force_p95":0.46389,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.70572,"mean_force":0.18629,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52214,-0.01799,0.15493]}],"total_contact_groups":29},"final_pose_error":0.26549,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.53831,0.00356,0.01602],"final_tcp_position":[0.43819,0.01579,0.09063],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9748.83333,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":387.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1544.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49986,-0.01386,0.18014],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15418,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":888.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3552.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49885,-0.01553,0.03762],"tcp_start":[0.49986,-0.01386,0.18014],"tcp_to_object_dist_end":0.01262,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50369,-0.01529,0.02589],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31211,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12912,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10798.0,"raw_peak_contact_force":0.1555,"subtask_id":"grasp_1","tcp_end":[0.49084,-0.01543,0.02914],"tcp_start":[0.49885,-0.01553,0.03762],"tcp_to_object_dist_end":0.01325,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":572.0,"n_steps_budget":630.0,"object_pos_end":[0.50565,-0.01538,0.15462],"object_pos_start":[0.50369,-0.01529,0.02589],"object_to_goal_dist_end":0.23766,"object_to_goal_dist_start":0.31211,"object_z_max":0.15445,"peak_contact_force":0.11754,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17210.0,"raw_peak_contact_force":0.72021,"tcp_end":[0.48736,-0.01536,0.16931],"tcp_start":[0.49084,-0.01543,0.02914],"tcp_to_object_dist_end":0.02345,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":12.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53003,-0.0135,0.00483],"object_pos_start":[0.50565,-0.01538,0.15462],"object_to_goal_dist_end":0.32063,"object_to_goal_dist_start":0.23766,"object_z_max":0.15488,"peak_contact_force":258.12938,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20680.0,"raw_peak_contact_force":1032.94432,"subtask_id":"transport_arc","tcp_end":[0.38474,-0.05164,0.0439],"tcp_start":[0.48736,-0.01536,0.16931],"tcp_to_object_dist_end":0.15521,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53831,0.00356,0.01602],"object_pos_start":[0.53003,-0.0135,0.00483],"object_to_goal_dist_end":0.30008,"object_to_goal_dist_start":0.32063,"object_z_max":0.01605,"peak_contact_force":9748.83333,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9880.0,"raw_peak_contact_force":121.00268,"subtask_id":"release_1","tcp_end":[0.43819,0.01579,0.09063],"tcp_start":[0.38474,-0.05164,0.0439],"tcp_to_object_dist_end":0.12546,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53831,0.00356,0.01602],"object_pos_start":[0.53831,0.00356,0.01602],"object_to_goal_dist_end":0.30008,"object_to_goal_dist_start":0.30008,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1015.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.43252,0.01529,0.11564],"tcp_start":[0.43819,0.01579,0.09063],"tcp_to_object_dist_end":0.14578,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":38.0,"average_failure_rate":0.19192,"average_mean_iterations":42.23737,"average_solve_count":198.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12884,"approach_1.speed":0.06709,"descend_1.grasp_z_offset":0.00886,"descend_1.speed":0.05345,"lift_1.lift_height":0.1914,"lift_1.speed":0.16385,"place_descend.speed":0.07031,"transport_arc.arc_height":0.1531,"transport_arc.speed":0.10108},"optimized_scores":{"best_composite_score":0.01009,"best_fitness_score":0.61009,"best_task_score":0.26164},"replay_outcomes":[{"contacts":{"omitted_contact_groups":11,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":40.0,"contact_point_centroid":[0.52376,0.10612,-0.00351],"force_p95":808.97295,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1020.41503,"mean_force":169.3252,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.47509,0.05167,-0.00705]},{"body_a":"world","body_b":"link6","contact_count":717.0,"contact_point_centroid":[0.66916,0.0497,-0.00023],"force_p95":261.87723,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":669.50006,"mean_force":222.2134,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.43264,0.09235,0.06616]},{"body_a":"world","body_b":"link6","contact_count":95.0,"contact_point_centroid":[0.70463,0.05808,-9e-05],"force_p95":523.20329,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":638.01032,"mean_force":184.97371,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.46666,0.13982,0.08179]},{"body_a":"world","body_b":"link7","contact_count":179.0,"contact_point_centroid":[0.58089,0.05206,-0.00027],"force_p95":314.55395,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":538.44698,"mean_force":222.52939,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.45536,0.05857,0.01904]},{"body_a":"world","body_b":"link6","contact_count":78.0,"contact_point_centroid":[0.73222,0.05891,-0.00012],"force_p95":158.10849,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":274.84607,"mean_force":71.31618,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49564,0.14687,0.08833]},{"body_a":"world","body_b":"right_finger","contact_count":827.0,"contact_point_centroid":[0.4782,0.06427,-0.00603],"force_p95":9.27852,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":42.93055,"mean_force":3.3255,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.4748,0.05192,-0.00541]},{"body_a":"world","body_b":"left_finger","contact_count":799.0,"contact_point_centroid":[0.47659,0.03901,-0.00598],"force_p95":9.16116,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":38.74912,"mean_force":3.09883,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.47499,0.05185,-0.00592]},{"body_a":"grasp_target","body_b":"hand","contact_count":924.0,"contact_point_centroid":[0.53196,0.05679,0.03616],"force_p95":1.4365,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.59223,"mean_force":0.80263,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.43894,0.08467,0.055]},{"body_a":"world","body_b":"grasp_target","contact_count":3071.0,"contact_point_centroid":[0.53354,0.04877,-0.00647],"force_p95":0.71712,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.70593,"mean_force":0.41181,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.43945,0.08053,0.05168]},{"body_a":"grasp_target","body_b":"link7","contact_count":835.0,"contact_point_centroid":[0.5392,0.04616,0.03391],"force_p95":0.59265,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.15715,"mean_force":0.38847,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.43507,0.08807,0.06055]},{"body_a":"world","body_b":"grasp_target","contact_count":123.0,"contact_point_centroid":[0.50926,0.03767,-0.00117],"force_p95":0.58954,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.83933,"mean_force":0.09421,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49804,0.03841,0.02611]},{"body_a":"grasp_target","body_b":"hand","contact_count":108.0,"contact_point_centroid":[0.54333,0.09164,0.04136],"force_p95":0.35994,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.76872,"mean_force":0.16479,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.45851,0.13795,0.08124]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":548.0,"contact_point_centroid":[0.53631,0.06085,0.17264],"force_p95":0.42525,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.67194,"mean_force":0.22452,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53401,0.04517,0.1779]},{"body_a":"world","body_b":"grasp_target","contact_count":915.0,"contact_point_centroid":[0.53072,0.05293,-0.0034],"force_p95":0.35417,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61713,"mean_force":0.20921,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.47847,0.14235,0.08277]},{"body_a":"grasp_target","body_b":"link7","contact_count":27.0,"contact_point_centroid":[0.54023,0.08519,0.04149],"force_p95":0.46444,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.53919,"mean_force":0.16856,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.45117,0.13636,0.08057]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":334.0,"contact_point_centroid":[0.53758,0.0295,0.16315],"force_p95":0.31131,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45273,"mean_force":0.17618,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53659,0.04601,0.1694]}],"total_contact_groups":27},"final_pose_error":0.14072,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.53106,0.04224,0.02602],"final_tcp_position":[0.49462,0.147,0.08661],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1020.41503,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":460.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1836.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50766,0.03575,0.16635],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14047,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50756,0.03921,0.0329],"tcp_start":[0.50766,0.03575,0.16635],"tcp_to_object_dist_end":0.00849,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51238,0.03847,0.02564],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21329,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14738,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10839.0,"raw_peak_contact_force":0.23825,"subtask_id":"grasp_1","tcp_end":[0.49948,0.03854,0.02417],"tcp_start":[0.50756,0.03921,0.0329],"tcp_to_object_dist_end":0.01298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":692.0,"n_steps_budget":750.0,"object_pos_end":[0.5125,0.03842,0.18015],"object_pos_start":[0.51238,0.03847,0.02564],"object_to_goal_dist_end":0.18016,"object_to_goal_dist_start":0.21329,"object_z_max":0.18002,"peak_contact_force":0.18468,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19421.0,"raw_peak_contact_force":0.83933,"tcp_end":[0.49624,0.03827,0.2],"tcp_start":[0.49948,0.03854,0.02417],"tcp_to_object_dist_end":0.02565,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5236,0.05907,0.02508],"object_pos_start":[0.5125,0.03842,0.18015],"object_to_goal_dist_end":0.19511,"object_to_goal_dist_start":0.18016,"object_z_max":0.18033,"peak_contact_force":258.98175,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11317.0,"raw_peak_contact_force":1020.41503,"subtask_id":"transport_arc","tcp_end":[0.44914,0.13658,0.0798],"tcp_start":[0.49624,0.03827,0.2],"tcp_to_object_dist_end":0.1206,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":364.0,"n_steps_budget":1000.0,"object_pos_end":[0.53105,0.04176,0.02604],"object_pos_start":[0.5236,0.05907,0.02508],"object_to_goal_dist_end":0.20143,"object_to_goal_dist_start":0.19511,"object_z_max":0.02816,"peak_contact_force":505.40758,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2712.0,"raw_peak_contact_force":638.01032,"subtask_id":"release_1","tcp_end":[0.49462,0.147,0.08661],"tcp_start":[0.44914,0.13658,0.0798],"tcp_to_object_dist_end":0.12677,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53106,0.04224,0.02602],"object_pos_start":[0.53105,0.04176,0.02604],"object_to_goal_dist_end":0.20112,"object_to_goal_dist_start":0.20143,"object_z_max":0.02604,"peak_contact_force":0.12267,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1103.0,"raw_peak_contact_force":274.84607,"tcp_end":[0.49323,0.14628,0.11499],"tcp_start":[0.49462,0.147,0.08661],"tcp_to_object_dist_end":0.14202,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":37.0,"average_failure_rate":0.16895,"average_mean_iterations":37.27854,"average_solve_count":219.0,"average_success_count":182.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15078,"approach_1.speed":0.09936,"descend_1.grasp_z_offset":0.01295,"descend_1.speed":0.06002,"lift_1.lift_height":0.19095,"lift_1.speed":0.14818,"place_descend.speed":0.04573,"transport_arc.arc_height":0.21734,"transport_arc.speed":0.17169},"optimized_scores":{"best_composite_score":-0.05504,"best_fitness_score":0.54496,"best_task_score":0.13511},"replay_outcomes":[{"contacts":{"omitted_contact_groups":11,"reported_contact_groups":[{"body_a":"world","body_b":"hand","contact_count":22.0,"contact_point_centroid":[0.45602,0.14555,-0.00259],"force_p95":807.68745,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":870.19568,"mean_force":116.51173,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.40611,0.05947,0.00317]},{"body_a":"world","body_b":"link7","contact_count":56.0,"contact_point_centroid":[0.52926,0.05794,-0.00161],"force_p95":692.6918,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":786.29483,"mean_force":261.14782,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.39805,0.06082,0.02418]},{"body_a":"world","body_b":"link6","contact_count":812.0,"contact_point_centroid":[0.61838,0.06632,-0.00024],"force_p95":254.69964,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":419.29934,"mean_force":221.54167,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.38247,0.0838,0.07053]},{"body_a":"world","body_b":"link6","contact_count":387.0,"contact_point_centroid":[0.65092,0.14663,-2e-05],"force_p95":253.60892,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":372.77771,"mean_force":124.37989,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.44751,0.16614,0.1902]},{"body_a":"link5","body_b":"hand","contact_count":260.0,"contact_point_centroid":[0.52161,0.09419,0.17442],"force_p95":308.49307,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":359.05147,"mean_force":251.69905,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.491,0.18496,0.19329]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.5168,0.10173,0.16091],"force_p95":191.08877,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":195.00927,"mean_force":149.08108,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50221,0.19269,0.20093]},{"body_a":"world","body_b":"link6","contact_count":62.0,"contact_point_centroid":[0.70657,0.1604,-0.00019],"force_p95":83.39784,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":107.66928,"mean_force":49.17311,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50214,0.19159,0.19467]},{"body_a":"world","body_b":"right_finger","contact_count":248.0,"contact_point_centroid":[0.41063,0.06326,-0.00276],"force_p95":29.07949,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":39.55857,"mean_force":3.36071,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.40749,0.05955,0.00203]},{"body_a":"world","body_b":"left_finger","contact_count":237.0,"contact_point_centroid":[0.4102,0.05484,-0.0027],"force_p95":26.34238,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":35.32344,"mean_force":3.16724,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.40749,0.05955,0.00188]},{"body_a":"grasp_target","body_b":"hand","contact_count":744.0,"contact_point_centroid":[0.48192,0.06016,0.03005],"force_p95":1.1325,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.76603,"mean_force":0.59393,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.38373,0.07544,0.05596]},{"body_a":"world","body_b":"grasp_target","contact_count":3110.0,"contact_point_centroid":[0.45889,0.05866,-0.00434],"force_p95":0.93263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.86172,"mean_force":0.30282,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.38578,0.08411,0.07015]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20.0,"contact_point_centroid":[0.44747,0.06517,0.01613],"force_p95":1.46965,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.20757,"mean_force":0.80158,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.43901,0.061,0.02138]},{"body_a":"grasp_target","body_b":"link7","contact_count":718.0,"contact_point_centroid":[0.48857,0.055,0.0267],"force_p95":0.47197,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.54425,"mean_force":0.33734,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.38217,0.07736,0.06009]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9.0,"contact_point_centroid":[0.44965,0.05759,0.01744],"force_p95":0.83832,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.9458,"mean_force":0.59717,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.43793,0.06097,0.0204]},{"body_a":"world","body_b":"grasp_target","contact_count":132.0,"contact_point_centroid":[0.48034,0.04621,-0.00119],"force_p95":0.41524,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65882,"mean_force":0.07582,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46897,0.04711,0.03477]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10044.0,"contact_point_centroid":[0.46986,0.02808,0.10328],"force_p95":0.12257,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3368,"mean_force":0.0731,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46677,0.0469,0.10161]}],"total_contact_groups":27},"final_pose_error":0.09156,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.45637,0.06033,0.01602],"final_tcp_position":[0.49979,0.19234,0.19281],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":9748.74436,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":370.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1476.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48131,0.0431,0.18867],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":894.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3576.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47805,0.04803,0.04059],"tcp_start":[0.48131,0.0431,0.18867],"tcp_to_object_dist_end":0.01531,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48262,0.04751,0.02554],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.2911,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15388,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12328.0,"raw_peak_contact_force":0.23752,"subtask_id":"grasp_1","tcp_end":[0.47037,0.04726,0.03273],"tcp_start":[0.47805,0.04803,0.04059],"tcp_to_object_dist_end":0.01421,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":752.0,"n_steps_budget":810.0,"object_pos_end":[0.48144,0.05154,0.16809],"object_pos_start":[0.48262,0.04751,0.02554],"object_to_goal_dist_end":0.21312,"object_to_goal_dist_start":0.2911,"object_z_max":0.17813,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20806.0,"raw_peak_contact_force":0.65882,"tcp_end":[0.46722,0.04695,0.20917],"tcp_start":[0.47037,0.04726,0.03273],"tcp_to_object_dist_end":0.04371,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45635,0.06036,0.01603],"object_pos_start":[0.48144,0.05154,0.16809],"object_to_goal_dist_end":0.30023,"object_to_goal_dist_start":0.21312,"object_z_max":0.16809,"peak_contact_force":9748.74436,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9536.0,"raw_peak_contact_force":870.19568,"subtask_id":"transport_arc","tcp_end":[0.39377,0.14173,0.18514],"tcp_start":[0.46722,0.04695,0.20917],"tcp_to_object_dist_end":0.19783,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":862.0,"n_steps_budget":1000.0,"object_pos_end":[0.45637,0.06033,0.01602],"object_pos_start":[0.45635,0.06036,0.01603],"object_to_goal_dist_end":0.30025,"object_to_goal_dist_start":0.30023,"object_z_max":0.01603,"peak_contact_force":228.12049,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7766.0,"raw_peak_contact_force":372.77771,"subtask_id":"release_1","tcp_end":[0.49979,0.19234,0.19281],"tcp_start":[0.39377,0.14173,0.18514],"tcp_to_object_dist_end":0.22487,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45637,0.06033,0.01602],"object_pos_start":[0.45637,0.06033,0.01602],"object_to_goal_dist_end":0.30025,"object_to_goal_dist_start":0.30025,"object_z_max":0.01602,"peak_contact_force":195.00927,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1292.0,"raw_peak_contact_force":195.00927,"tcp_end":[0.50349,0.19593,0.22098],"tcp_start":[0.49979,0.19234,0.19281],"tcp_to_object_dist_end":0.25023,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```