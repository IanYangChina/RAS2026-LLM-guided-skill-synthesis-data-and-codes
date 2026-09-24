## Search State

- **Seed**: 6
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0750 | 0.30 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0057 | 0.26 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | -0.0328 | 0.18 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.0095 | 0.37 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0159 | 0.28 | ✅ accepted |

**Proposal policy**: task_score is 0.30 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.075) — your mutation base

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

- **Composite score**: 0.075
- **task_score** (E): 0.305
- **fitness_score**: 0.625  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.550

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1629 |
| descend_1 | 1.00 | 1.00 | 0.0966 |
| grasp_1 | 1.00 | 1.00 | 0.0114 |
| lift_1 | 1.00 | 1.00 | 0.2429 |
| transport_approach | 1.00 | 0.67 | 0.2067 |
| place_descend | 1.00 | 1.00 | 0.1097 |
| release_1 | 1.00 | 1.00 | 0.0204 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.020, 0.142) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 5.978 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.020, 0.142)→(0.495, 0.024, 0.045) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 5.004 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.024, 0.045)→(0.487, 0.023, 0.037) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.026) | 0.271→0.272 | 1.00 / 45.000 | 0.147 | 0.208 |
| lift_1 | lift | 1.00 / step_budget | (0.487, 0.023, 0.037)→(0.484, 0.023, 0.280) | (0.500, 0.023, 0.026)→(0.493, 0.023, 0.262) | 0.272→0.216 | 1.00 / 41.333 | 0.073 | 0.507 |
| transport_approach | approach | 1.00 / step_budget | (0.484, 0.023, 0.280)→(0.590, 0.184, 0.345) | (0.493, 0.023, 0.262)→(0.584, 0.175, 0.198) | 0.216→0.147 | 0.67 / 17.667 | 0.063 | 0.996 |
| place_descend | descend | 1.00 / step_budget | (0.590, 0.184, 0.345)→(0.595, 0.193, 0.236) | (0.584, 0.175, 0.198)→(0.588, 0.185, 0.063) | 0.147→0.149 | 1.00 / 19.000 | 91002.096 | 0.728 |
| release_1 | release | 1.00 / step_budget | (0.595, 0.193, 0.236)→(0.590, 0.192, 0.256) | (0.588, 0.185, 0.063)→(0.584, 0.185, 0.023) | 0.149→0.187 | 1.00 / 3.333 | 0.143 | 0.559 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.453
- phase_score: 0.325
- phase_breakdown.descend_1_score: 0.787
- phase_breakdown.transport_arc_score: 0.060
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.115
- phase_breakdown.release_1_score: 0.381
- grasp_place_fitness: 0.704

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.704
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.453
- **Median Q (composite search score)**: 0.046
- **K-run variance**: 0.0032
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.360


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.7726,"average_solve_count":365.0,"average_success_count":365.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06536,"approach_1.speed":0.05427,"descend_1.grasp_z_offset":0.02452,"descend_1.speed":0.04953,"lift_1.lift_height":0.26096,"lift_1.speed":0.05757,"place_descend.speed":0.0191,"transport_approach.speed":0.10995},"optimized_scores":{"best_composite_score":0.02523,"best_fitness_score":0.57523,"best_task_score":0.20679},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":742.0,"contact_point_centroid":[0.5701,0.14605,-0.00398],"force_p95":0.98735,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.55131,"mean_force":0.21724,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.56772,0.14999,0.36947]},{"body_a":"world","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.50091,-0.01527,-0.00138],"force_p95":0.42855,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.49932,"mean_force":0.13655,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49008,-0.01543,0.03985]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15411.0,"contact_point_centroid":[0.48828,0.00373,0.15902],"force_p95":0.07937,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29192,"mean_force":0.05574,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48781,-0.01538,0.15658]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15993.0,"contact_point_centroid":[0.48827,-0.03447,0.15798],"force_p95":0.07821,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28627,"mean_force":0.05415,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4878,-0.01538,0.15582]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5161.0,"contact_point_centroid":[0.51515,0.05295,0.30481],"force_p95":0.12193,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27521,"mean_force":0.0746,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.51087,0.03433,0.30406]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4722.0,"contact_point_centroid":[0.51197,0.00999,0.30226],"force_p95":0.1463,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25679,"mean_force":0.07951,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.50824,0.02876,0.30109]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01562,-0.00203],"force_p95":0.1308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15605,"mean_force":0.12508,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49233,-0.01546,0.03994]},{"body_a":"world","body_b":"grasp_target","contact_count":1476.0,"contact_point_centroid":[0.50382,-0.01567,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49919,-0.00661,0.20896]},{"body_a":"world","body_b":"grasp_target","contact_count":1300.0,"contact_point_centroid":[0.56916,0.14616,-0.00199],"force_p95":0.12267,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1228,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.58148,0.17947,0.33168]},{"body_a":"world","body_b":"grasp_target","contact_count":2552.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49799,-0.01486,0.0706]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56916,0.14616,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5808,0.18367,0.27762]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5091.0,"contact_point_centroid":[0.49102,0.00381,0.04176],"force_p95":0.06553,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09268,"mean_force":0.0429,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49117,-0.01544,0.03869]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5365.0,"contact_point_centroid":[0.49089,-0.03468,0.04127],"force_p95":0.06378,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08102,"mean_force":0.04115,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49117,-0.01544,0.03869]},{"body_a":"left_finger","body_b":"right_finger","contact_count":724.0,"contact_point_centroid":[0.56928,0.15238,0.37313],"force_p95":0.0131,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01644,"mean_force":0.0109,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.56891,0.15237,0.37085]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1390.0,"contact_point_centroid":[0.58196,0.1795,0.33391],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01268,"mean_force":0.01043,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.58148,0.17948,0.33165]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.58304,0.18439,0.27594],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.01007,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58243,0.18437,0.27352]}],"total_contact_groups":16},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.56916,0.14616,0.01602],"final_tcp_position":[0.58363,0.18473,0.27712],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":2.55131,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":370.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1476.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49983,-0.0137,0.1148],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08889,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":638.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2552.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49893,-0.01555,0.04706],"tcp_start":[0.49983,-0.0137,0.1148],"tcp_to_object_dist_end":0.0216,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50371,-0.01546,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31222,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13003,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12256.0,"raw_peak_contact_force":0.15605,"subtask_id":"grasp_1","tcp_end":[0.49114,-0.01544,0.03866],"tcp_start":[0.49893,-0.01555,0.04706],"tcp_to_object_dist_end":0.01793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":826.0,"n_steps_budget":1000.0,"object_pos_end":[0.49636,-0.01533,0.26074],"object_pos_start":[0.50371,-0.01546,0.02588],"object_to_goal_dist_end":0.22243,"object_to_goal_dist_start":0.31222,"object_z_max":0.26048,"peak_contact_force":0.07942,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":31485.0,"raw_peak_contact_force":0.49932,"tcp_end":[0.48862,-0.0154,0.27999],"tcp_start":[0.49114,-0.01544,0.03866],"tcp_to_object_dist_end":0.02074,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":703.0,"n_steps_budget":1000.0,"object_pos_end":[0.56917,0.14614,0.01602],"object_pos_start":[0.49636,-0.01533,0.26074],"object_to_goal_dist_end":0.23641,"object_to_goal_dist_start":0.22243,"object_z_max":0.30997,"peak_contact_force":0.12281,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11349.0,"raw_peak_contact_force":2.55131,"subtask_id":"transport_arc","tcp_end":[0.58035,0.17509,0.38409],"tcp_start":[0.48862,-0.0154,0.27999],"tcp_to_object_dist_end":0.36937,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":325.0,"n_steps_budget":1000.0,"object_pos_end":[0.56916,0.14616,0.01602],"object_pos_start":[0.56917,0.14614,0.01602],"object_to_goal_dist_end":0.23641,"object_to_goal_dist_start":0.23641,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2690.0,"raw_peak_contact_force":0.1228,"tcp_end":[0.58363,0.18473,0.27712],"tcp_start":[0.58035,0.17509,0.38409],"tcp_to_object_dist_end":0.26433,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56916,0.14616,0.01602],"object_pos_start":[0.56916,0.14616,0.01602],"object_to_goal_dist_end":0.23641,"object_to_goal_dist_start":0.23641,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57992,0.18326,0.29739],"tcp_start":[0.58363,0.18473,0.27712],"tcp_to_object_dist_end":0.28402,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.06306,"average_solve_count":333.0,"average_success_count":333.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08968,"approach_1.speed":0.05301,"descend_1.grasp_z_offset":0.00726,"descend_1.speed":0.04992,"lift_1.lift_height":0.25414,"lift_1.speed":0.03007,"place_descend.speed":0.0369,"transport_approach.speed":0.12123},"optimized_scores":{"best_composite_score":0.15387,"best_fitness_score":0.70387,"best_task_score":0.4532},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":201.0,"contact_point_centroid":[0.6054,0.16842,-0.00671],"force_p95":1.2032,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.42993,"mean_force":0.35624,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61618,0.16791,0.18073]},{"body_a":"world","body_b":"grasp_target","contact_count":91.0,"contact_point_centroid":[0.50829,0.03761,-0.00154],"force_p95":0.53773,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5608,"mean_force":0.20625,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49801,0.03795,0.03189]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16415.0,"contact_point_centroid":[0.49573,0.05688,0.1465],"force_p95":0.07718,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29288,"mean_force":0.0522,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49565,0.03776,0.14459]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15937.0,"contact_point_centroid":[0.49588,0.01863,0.14986],"force_p95":0.07689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2818,"mean_force":0.05288,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49566,0.03776,0.14752]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51257,0.03941,-0.00215],"force_p95":0.16652,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24374,"mean_force":0.13421,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50033,0.03815,0.03202]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1288.0,"contact_point_centroid":[0.6202,0.18844,0.16908],"force_p95":0.06962,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19857,"mean_force":0.0426,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62013,0.16922,0.16826]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7303.0,"contact_point_centroid":[0.61724,0.18397,0.23178],"force_p95":0.06796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19269,"mean_force":0.04495,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61744,0.1648,0.22997]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1216.0,"contact_point_centroid":[0.61979,0.15003,0.16942],"force_p95":0.0714,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19173,"mean_force":0.04386,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62013,0.16922,0.16826]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6444.0,"contact_point_centroid":[0.61709,0.14565,0.23077],"force_p95":0.07206,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15934,"mean_force":0.05001,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61749,0.16486,0.22933]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4057.0,"contact_point_centroid":[0.49978,0.01885,0.03352],"force_p95":0.08177,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15185,"mean_force":0.05193,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49913,0.03806,0.03073]},{"body_a":"world","body_b":"grasp_target","contact_count":1336.0,"contact_point_centroid":[0.51251,0.03972,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50286,0.01644,0.22041]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50595,0.03705,0.07235]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8836.0,"contact_point_centroid":[0.55765,0.08285,0.27615],"force_p95":0.07876,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11598,"mean_force":0.05457,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.55759,0.10207,0.27367]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10305.0,"contact_point_centroid":[0.55736,0.12065,0.27516],"force_p95":0.07083,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11432,"mean_force":0.04757,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.55714,0.10164,0.27351]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5025.0,"contact_point_centroid":[0.49975,0.05724,0.03254],"force_p95":0.07447,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08338,"mean_force":0.04464,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49914,0.03806,0.03074]}],"total_contact_groups":15},"final_pose_error":0.00977,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61042,0.16714,0.02768],"final_tcp_position":[0.62213,0.16976,0.17266],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.42993,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":335.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1336.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50738,0.0342,0.13786],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11209,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50707,0.03871,0.03939],"tcp_start":[0.50738,0.0342,0.13786],"tcp_to_object_dist_end":0.01447,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51242,0.03816,0.0255],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21354,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15736,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10882.0,"raw_peak_contact_force":0.24374,"subtask_id":"grasp_1","tcp_end":[0.49911,0.03805,0.0307],"tcp_start":[0.50707,0.03871,0.03939],"tcp_to_object_dist_end":0.0143,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":820.0,"n_steps_budget":1000.0,"object_pos_end":[0.50616,0.03786,0.25344],"object_pos_start":[0.51242,0.03816,0.0255],"object_to_goal_dist_end":0.21125,"object_to_goal_dist_start":0.21354,"object_z_max":0.25317,"peak_contact_force":0.07021,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32443.0,"raw_peak_contact_force":0.5608,"tcp_end":[0.49643,0.03782,0.26515],"tcp_start":[0.49911,0.03805,0.0307],"tcp_to_object_dist_end":0.01523,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":484.0,"n_steps_budget":1000.0,"object_pos_end":[0.61432,0.1607,0.26112],"object_pos_start":[0.50616,0.03786,0.25344],"object_to_goal_dist_end":0.11745,"object_to_goal_dist_start":0.21125,"object_z_max":0.26112,"peak_contact_force":0.06653,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":19141.0,"raw_peak_contact_force":0.11598,"subtask_id":"transport_arc","tcp_end":[0.61496,0.16089,0.28478],"tcp_start":[0.49643,0.03782,0.26515],"tcp_to_object_dist_end":0.02367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":322.0,"n_steps_budget":1000.0,"object_pos_end":[0.62261,0.16979,0.14756],"object_pos_start":[0.61432,0.1607,0.26112],"object_to_goal_dist_end":0.0062,"object_to_goal_dist_start":0.11745,"object_z_max":0.26112,"peak_contact_force":0.07327,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":13747.0,"raw_peak_contact_force":0.19269,"tcp_end":[0.62213,0.16976,0.17266],"tcp_start":[0.61496,0.16089,0.28478],"tcp_to_object_dist_end":0.02511,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61042,0.16714,0.02768],"object_pos_start":[0.62261,0.16979,0.14756],"object_to_goal_dist_end":0.11871,"object_to_goal_dist_start":0.0062,"object_z_max":0.14756,"peak_contact_force":0.18378,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2705.0,"raw_peak_contact_force":1.42993,"subtask_id":"release_1","tcp_end":[0.61612,0.16789,0.19166],"tcp_start":[0.62213,0.16976,0.17266],"tcp_to_object_dist_end":0.16408,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05587,"average_solve_count":358.0,"average_success_count":358.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12481,"approach_1.speed":0.0436,"descend_1.grasp_z_offset":0.02182,"descend_1.speed":0.03015,"lift_1.lift_height":0.27241,"lift_1.speed":0.0227,"place_descend.speed":0.05318,"transport_approach.speed":0.14441},"optimized_scores":{"best_composite_score":0.04592,"best_fitness_score":0.59592,"best_task_score":0.2549},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":844.0,"contact_point_centroid":[0.57197,0.24041,-0.00382],"force_p95":0.86948,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.8684,"mean_force":0.19554,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.5762,0.22225,0.29629]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.47919,0.04668,-0.00152],"force_p95":0.44722,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46202,"mean_force":0.16866,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46955,0.04699,0.04294]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10302.0,"contact_point_centroid":[0.51158,0.13759,0.32374],"force_p95":0.0994,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32046,"mean_force":0.05552,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.51181,0.11863,0.32347]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17532.0,"contact_point_centroid":[0.46752,0.06594,0.17196],"force_p95":0.07575,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28999,"mean_force":0.05134,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4674,0.04678,0.17007]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9205.0,"contact_point_centroid":[0.51285,0.1015,0.32503],"force_p95":0.10368,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27488,"mean_force":0.06193,"phase_index":4.0,"phase_name":"transport_approach","phase_type":"approach","tcp_position_centroid":[0.51306,0.1206,0.32439]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17185.0,"contact_point_centroid":[0.4673,0.02762,0.1707],"force_p95":0.07566,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25706,"mean_force":0.05165,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46739,0.04678,0.16851]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48274,0.04857,-0.00213],"force_p95":0.15988,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22497,"mean_force":0.13265,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47169,0.04722,0.0429]},{"body_a":"world","body_b":"grasp_target","contact_count":1080.0,"contact_point_centroid":[0.4827,0.04873,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49092,0.01926,0.2382]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5045.0,"contact_point_centroid":[0.4703,0.02786,0.04441],"force_p95":0.0697,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12726,"mean_force":0.04298,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47057,0.04711,0.04175]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57198,0.24043,-0.00199],"force_p95":0.12293,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1249,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57525,0.22455,0.25935]},{"body_a":"world","body_b":"grasp_target","contact_count":3132.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4786,0.04422,0.10769]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5510.0,"contact_point_centroid":[0.47013,0.06642,0.04383],"force_p95":0.06952,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07203,"mean_force":0.04088,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47058,0.04711,0.04176]},{"body_a":"left_finger","body_b":"right_finger","contact_count":778.0,"contact_point_centroid":[0.577,0.22274,0.29384],"force_p95":0.01297,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01619,"mean_force":0.01086,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57644,0.22271,0.29149]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.57734,0.22548,0.25768],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.00991,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57699,0.22544,0.25539]}],"total_contact_groups":14},"final_pose_error":0.00973,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57198,0.24043,0.02602],"final_tcp_position":[0.57824,0.22593,0.25903],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273006.09088,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":271.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":17.68876,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1080.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48239,0.04062,0.17288],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14708,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":783.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":14.7669,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3132.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47815,0.04785,0.04962],"tcp_start":[0.48239,0.04062,0.17288],"tcp_to_object_dist_end":0.02405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48265,0.04755,0.02553],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29107,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15469,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12355.0,"raw_peak_contact_force":0.22497,"subtask_id":"grasp_1","tcp_end":[0.47055,0.04711,0.04172],"tcp_start":[0.47815,0.04785,0.04962],"tcp_to_object_dist_end":0.02022,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":851.0,"n_steps_budget":1000.0,"object_pos_end":[0.475,0.04677,0.27314],"object_pos_start":[0.48265,0.04755,0.02553],"object_to_goal_dist_end":0.21539,"object_to_goal_dist_start":0.29107,"object_z_max":0.27286,"peak_contact_force":0.07064,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34803.0,"raw_peak_contact_force":0.46202,"tcp_end":[0.46821,0.04686,0.29455],"tcp_start":[0.47055,0.04711,0.04172],"tcp_to_object_dist_end":0.02246,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":586.0,"n_steps_budget":1000.0,"object_pos_end":[0.56839,0.21697,0.31592],"object_pos_start":[0.475,0.04677,0.27314],"object_to_goal_dist_end":0.08731,"object_to_goal_dist_start":0.21539,"object_z_max":0.32747,"peak_contact_force":0.0,"phase_name":"transport_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":19507.0,"raw_peak_contact_force":0.32046,"subtask_id":"transport_arc","tcp_end":[0.57353,0.21647,0.36757],"tcp_start":[0.46821,0.04686,0.29455],"tcp_to_object_dist_end":0.0519,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":310.0,"n_steps_budget":1000.0,"object_pos_end":[0.57202,0.24049,0.02602],"object_pos_start":[0.56839,0.21697,0.31592],"object_to_goal_dist_end":0.20503,"object_to_goal_dist_start":0.08731,"object_z_max":0.31592,"peak_contact_force":273006.09088,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1622.0,"raw_peak_contact_force":1.8684,"tcp_end":[0.57824,0.22593,0.25903],"tcp_start":[0.57353,0.21647,0.36757],"tcp_to_object_dist_end":0.23354,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57198,0.24043,0.02602],"object_pos_start":[0.57202,0.24049,0.02602],"object_to_goal_dist_end":0.20503,"object_to_goal_dist_start":0.20503,"object_z_max":0.02602,"peak_contact_force":0.12264,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.1249,"subtask_id":"release_1","tcp_end":[0.57431,0.22403,0.27906],"tcp_start":[0.57824,0.22593,0.25903],"tcp_to_object_dist_end":0.25358,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```