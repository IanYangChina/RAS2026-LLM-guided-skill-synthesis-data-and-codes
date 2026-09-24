## Search State

- **Seed**: 6
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0159 | 0.28 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0726 | 0.24 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1345 | 0.25 | ✅ accepted |
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | admittance_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | time_limit | 3 | 0.3184 | 0.17 | ✅ accepted |

**Proposal policy**: task_score is 0.28 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.016) — your mutation base

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
      - 0.2
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
      default: 0.15
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.06
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
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0

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
- **release_1** (`release`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.016
- **task_score** (E): 0.280
- **fitness_score**: 0.616  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.600

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1057 |
| descend_1 | 1.00 | 1.00 | 0.1583 |
| grasp_1 | 1.00 | 1.00 | 0.0115 |
| lift_1 | 0.33 | 1.00 | 0.0948 |
| transport_arc | 0.67 | 1.00 | 0.2535 |
| place_descend | 1.00 | 1.00 | 0.0964 |
| release_1 | 1.00 | 1.00 | 0.0207 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.022, 0.201) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.022, 0.201)→(0.495, 0.024, 0.042) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.024, 0.042)→(0.487, 0.023, 0.034) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 43.000 | 0.144 | 0.204 |
| lift_1 | lift | 0.33 / step_budget | (0.487, 0.023, 0.034)→(0.483, 0.023, 0.129) | (0.500, 0.024, 0.026)→(0.490, 0.023, 0.113) | 0.272→0.230 | 1.00 / 41.667 | 524.410 | 0.548 |
| transport_arc | approach | 0.67 / step_budget | (0.483, 0.023, 0.129)→(0.582, 0.170, 0.306) | (0.490, 0.023, 0.113)→(0.567, 0.131, 0.185) | 0.230→0.143 | 1.00 / 14.000 | 0.110 | 0.856 |
| place_descend | descend | 1.00 / step_budget | (0.582, 0.170, 0.306)→(0.593, 0.192, 0.214) | (0.567, 0.131, 0.185)→(0.578, 0.139, 0.053) | 0.143→0.172 | 1.00 / 16.667 | 16.489 | 0.856 |
| release_1 | release | 1.00 / step_budget | (0.593, 0.192, 0.214)→(0.588, 0.190, 0.234) | (0.578, 0.139, 0.053)→(0.573, 0.139, 0.020) | 0.172→0.205 | 1.00 / 3.333 | 0.134 | 0.482 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.456
- phase_score: 0.388
- phase_breakdown.descend_1_score: 0.880
- phase_breakdown.transport_arc_score: 0.117
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.038
- phase_breakdown.release_1_score: 0.556
- grasp_place_fitness: 0.701

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.701
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.456
- **Median Q (composite search score)**: -0.019
- **K-run variance**: 0.0037
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.415


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0708,"average_solve_count":339.0,"average_success_count":339.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18065,"approach_1.speed":0.04801,"descend_1.grasp_z_offset":0.01437,"descend_1.speed":0.07063,"lift_1.lift_height":0.15357,"lift_1.speed":0.05936,"place_descend.speed":0.02194,"transport_arc.arc_height":0.2996,"transport_arc.speed":0.05358},"optimized_scores":{"best_composite_score":-0.01868,"best_fitness_score":0.58132,"best_task_score":0.20882},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1034.0,"contact_point_centroid":[0.59677,0.15228,-0.00352],"force_p95":0.71092,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.94701,"mean_force":0.18321,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57325,0.16484,0.28268]},{"body_a":"world","body_b":"grasp_target","contact_count":172.0,"contact_point_centroid":[0.49959,-0.01535,-0.00115],"force_p95":0.38266,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56527,"mean_force":0.09615,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48927,-0.0154,0.0344]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19132.0,"contact_point_centroid":[0.4871,0.00378,0.08451],"force_p95":0.07708,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3193,"mean_force":0.05276,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48674,-0.01535,0.0824]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19898.0,"contact_point_centroid":[0.48705,-0.03444,0.08414],"force_p95":0.07591,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29745,"mean_force":0.05106,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48674,-0.01535,0.08224]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11911.0,"contact_point_centroid":[0.5024,0.03379,0.23387],"force_p95":0.15015,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26865,"mean_force":0.07871,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49917,0.01498,0.23311]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":31.0,"contact_point_centroid":[0.56677,0.12431,0.33742],"force_p95":0.1538,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2268,"mean_force":0.02914,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.56131,0.13852,0.34306]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13469.0,"contact_point_centroid":[0.50399,-0.00063,0.23782],"force_p95":0.11876,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19581,"mean_force":0.07055,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50065,0.01796,0.23775]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50381,-0.01555,-0.00203],"force_p95":0.13168,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15442,"mean_force":0.12526,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49213,-0.01543,0.0341]},{"body_a":"world","body_b":"grasp_target","contact_count":1084.0,"contact_point_centroid":[0.50382,-0.01567,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12308,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49924,-0.00619,0.2605]},{"body_a":"world","body_b":"grasp_target","contact_count":3912.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49806,-0.01434,0.12476]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59696,0.15241,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57784,0.1794,0.25276]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4113.0,"contact_point_centroid":[0.49138,0.00379,0.03563],"force_p95":0.07607,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11812,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49096,-0.01542,0.03286]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4884.0,"contact_point_centroid":[0.49146,-0.03449,0.03471],"force_p95":0.06825,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08951,"mean_force":0.04469,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49096,-0.01542,0.03286]},{"body_a":"left_finger","body_b":"right_finger","contact_count":986.0,"contact_point_centroid":[0.57436,0.16632,0.28206],"force_p95":0.01268,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01649,"mean_force":0.0108,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57397,0.1663,0.27975]},{"body_a":"left_finger","body_b":"right_finger","contact_count":227.0,"contact_point_centroid":[0.58011,0.18022,0.25084],"force_p95":0.01088,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0126,"mean_force":0.00988,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57973,0.1802,0.24866]}],"total_contact_groups":15},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.59696,0.15241,0.01602],"final_tcp_position":[0.58101,0.18037,0.25198],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1573.09317,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":272.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1084.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50014,-0.01311,0.21948],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19352,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":978.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3912.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49891,-0.01552,0.04134],"tcp_start":[0.50014,-0.01311,0.21948],"tcp_to_object_dist_end":0.01609,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5037,-0.01529,0.02588],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31211,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.1297,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10797.0,"raw_peak_contact_force":0.15442,"subtask_id":"grasp_1","tcp_end":[0.49093,-0.01542,0.03283],"tcp_start":[0.49891,-0.01552,0.04134],"tcp_to_object_dist_end":0.01453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49458,-0.01525,0.11583],"object_pos_start":[0.5037,-0.01529,0.02588],"object_to_goal_dist_end":0.25906,"object_to_goal_dist_start":0.31211,"object_z_max":0.11573,"peak_contact_force":1573.09317,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39202.0,"raw_peak_contact_force":0.56527,"tcp_end":[0.48682,-0.01534,0.13071],"tcp_start":[0.49093,-0.01542,0.03283],"tcp_to_object_dist_end":0.01678,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56852,0.13581,0.31367],"object_pos_start":[0.49458,-0.01525,0.11583],"object_to_goal_dist_end":0.08545,"object_to_goal_dist_start":0.25906,"object_z_max":0.31763,"peak_contact_force":0.09848,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25380.0,"raw_peak_contact_force":0.26865,"subtask_id":"transport_arc","tcp_end":[0.56134,0.13814,0.34333],"tcp_start":[0.48682,-0.01534,0.13071],"tcp_to_object_dist_end":0.03061,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":370.0,"n_steps_budget":1000.0,"object_pos_end":[0.59696,0.15241,0.01602],"object_pos_start":[0.56852,0.13581,0.31367],"object_to_goal_dist_end":0.23494,"object_to_goal_dist_start":0.08545,"object_z_max":0.31367,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2051.0,"raw_peak_contact_force":1.94701,"subtask_id":"release_1","tcp_end":[0.58101,0.18037,0.25198],"tcp_start":[0.56134,0.13814,0.34333],"tcp_to_object_dist_end":0.23815,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59696,0.15241,0.01602],"object_pos_start":[0.59696,0.15241,0.01602],"object_to_goal_dist_end":0.23494,"object_to_goal_dist_start":0.23494,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57679,0.17895,0.27258],"tcp_start":[0.58101,0.18037,0.25198],"tcp_to_object_dist_end":0.25872,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10284,"average_solve_count":282.0,"average_success_count":282.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15596,"approach_1.speed":0.05873,"descend_1.grasp_z_offset":0.01952,"descend_1.speed":0.06422,"lift_1.lift_height":0.12285,"lift_1.speed":0.05727,"place_descend.speed":0.06784,"transport_arc.arc_height":0.13084,"transport_arc.speed":0.01038},"optimized_scores":{"best_composite_score":0.10098,"best_fitness_score":0.70098,"best_task_score":0.45628},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.61664,0.1676,-0.00839],"force_p95":1.14385,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.19978,"mean_force":0.47083,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61515,0.16746,0.16014]},{"body_a":"world","body_b":"grasp_target","contact_count":192.0,"contact_point_centroid":[0.50799,0.03773,-0.00123],"force_p95":0.32658,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51916,"mean_force":0.09209,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49777,0.03833,0.03884]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4486.0,"contact_point_centroid":[0.62062,0.18332,0.19852],"force_p95":0.10411,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.49876,"mean_force":0.06732,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61659,0.16446,0.19715]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4450.0,"contact_point_centroid":[0.62038,0.14538,0.201],"force_p95":0.10787,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45667,"mean_force":0.07001,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61637,0.16423,0.19948]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19431.0,"contact_point_centroid":[0.49575,0.05725,0.08583],"force_p95":0.07742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31226,"mean_force":0.05234,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49537,0.03815,0.08389]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19249.0,"contact_point_centroid":[0.4958,0.01904,0.08752],"force_p95":0.07801,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30499,"mean_force":0.05223,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49537,0.03815,0.08534]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":892.0,"contact_point_centroid":[0.62203,0.14974,0.1479],"force_p95":0.0873,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26066,"mean_force":0.05924,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61935,0.16883,0.14756]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1047.0,"contact_point_centroid":[0.62189,0.1878,0.14751],"force_p95":0.07888,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25437,"mean_force":0.05106,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61936,0.16884,0.14756]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51254,0.03951,-0.00211],"force_p95":0.15345,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2185,"mean_force":0.13088,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50079,0.03859,0.03846]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4081.0,"contact_point_centroid":[0.50007,0.01929,0.03997],"force_p95":0.07991,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1461,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49961,0.03849,0.03717]},{"body_a":"world","body_b":"grasp_target","contact_count":1556.0,"contact_point_centroid":[0.51251,0.03972,-0.00191],"force_p95":0.13468,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12294,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50273,0.0169,0.24661]},{"body_a":"world","body_b":"grasp_target","contact_count":3544.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50613,0.03711,0.11281]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14967.0,"contact_point_centroid":[0.52443,0.08733,0.22439],"force_p95":0.08775,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12102,"mean_force":0.05984,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52277,0.06826,0.22299]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16384.0,"contact_point_centroid":[0.525,0.04995,0.2266],"force_p95":0.08087,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12012,"mean_force":0.05498,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52335,0.06887,0.22556]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4975.0,"contact_point_centroid":[0.50009,0.05762,0.03899],"force_p95":0.07259,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08101,"mean_force":0.04459,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49962,0.03849,0.03717]}],"total_contact_groups":15},"final_pose_error":0.00974,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61093,0.16765,0.02861],"final_tcp_position":[0.62151,0.1694,0.15199],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":49.2218,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":390.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1556.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50768,0.03501,0.19313],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16725,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":886.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3544.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50757,0.03914,0.04595],"tcp_start":[0.50768,0.03501,0.19313],"tcp_to_object_dist_end":0.02055,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51244,0.03861,0.02563],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21317,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14744,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10856.0,"raw_peak_contact_force":0.2185,"subtask_id":"grasp_1","tcp_end":[0.49958,0.03849,0.03713],"tcp_start":[0.50757,0.03914,0.04595],"tcp_to_object_dist_end":0.01725,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5021,0.03816,0.11277],"object_pos_start":[0.51244,0.03861,0.02563],"object_to_goal_dist_end":0.18664,"object_to_goal_dist_start":0.21317,"object_z_max":0.11268,"peak_contact_force":0.06815,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38872.0,"raw_peak_contact_force":0.51916,"tcp_end":[0.49546,0.03816,0.13168],"tcp_start":[0.49958,0.03849,0.03713],"tcp_to_object_dist_end":0.02004,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":906.0,"n_steps_budget":1000.0,"object_pos_end":[0.62093,0.15972,0.22667],"object_pos_start":[0.5021,0.03816,0.11277],"object_to_goal_dist_end":0.08291,"object_to_goal_dist_start":0.18664,"object_z_max":0.25257,"peak_contact_force":0.10755,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31351.0,"raw_peak_contact_force":0.12102,"subtask_id":"transport_arc","tcp_end":[0.61337,0.15967,0.25062],"tcp_start":[0.49546,0.03816,0.13168],"tcp_to_object_dist_end":0.02511,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":279.0,"n_steps_budget":1000.0,"object_pos_end":[0.62491,0.16899,0.12633],"object_pos_start":[0.62093,0.15972,0.22667],"object_to_goal_dist_end":0.01921,"object_to_goal_dist_start":0.08291,"object_z_max":0.22667,"peak_contact_force":49.2218,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8936.0,"raw_peak_contact_force":0.49876,"subtask_id":"release_1","tcp_end":[0.62151,0.1694,0.15199],"tcp_start":[0.61337,0.15967,0.25062],"tcp_to_object_dist_end":0.02588,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61093,0.16765,0.02861],"object_pos_start":[0.62491,0.16899,0.12633],"object_to_goal_dist_end":0.1177,"object_to_goal_dist_start":0.01921,"object_z_max":0.12633,"peak_contact_force":0.15752,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2087.0,"raw_peak_contact_force":1.19978,"tcp_end":[0.61507,0.16744,0.17107],"tcp_start":[0.62151,0.1694,0.15199],"tcp_to_object_dist_end":0.14252,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09483,"average_solve_count":348.0,"average_success_count":348.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15125,"approach_1.speed":0.03843,"descend_1.grasp_z_offset":0.01217,"descend_1.speed":0.02328,"lift_1.lift_height":0.23577,"lift_1.speed":0.01061,"place_descend.speed":0.08027,"transport_arc.arc_height":0.29219,"transport_arc.speed":0.07461},"optimized_scores":{"best_composite_score":-0.03468,"best_fitness_score":0.56532,"best_task_score":0.17464},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1513.0,"contact_point_centroid":[0.51206,0.09588,-0.00286],"force_p95":0.37984,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17826,"mean_force":0.16146,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53563,0.15825,0.31531]},{"body_a":"world","body_b":"grasp_target","contact_count":173.0,"contact_point_centroid":[0.47732,0.04643,-0.00124],"force_p95":0.48333,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55815,"mean_force":0.1155,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46874,0.0471,0.03357]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21035.0,"contact_point_centroid":[0.46598,0.06605,0.0794],"force_p95":0.07077,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29108,"mean_force":0.0488,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46626,0.04687,0.07776]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21062.0,"contact_point_centroid":[0.46599,0.02769,0.08089],"force_p95":0.07064,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25337,"mean_force":0.04798,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46625,0.04687,0.07882]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6797.0,"contact_point_centroid":[0.47166,0.07372,0.18839],"force_p95":0.12941,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24825,"mean_force":0.07525,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46866,0.05475,0.18754]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7646.0,"contact_point_centroid":[0.47191,0.03636,0.18899],"force_p95":0.1229,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24029,"mean_force":0.06787,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46882,0.05503,0.18842]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48274,0.04851,-0.00213],"force_p95":0.15997,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2386,"mean_force":0.13271,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4715,0.04738,0.03307]},{"body_a":"world","body_b":"grasp_target","contact_count":1604.0,"contact_point_centroid":[0.4827,0.04873,-0.00191],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4899,0.02069,0.24488]},{"body_a":"world","body_b":"grasp_target","contact_count":3960.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47799,0.04549,0.1101]},{"body_a":"world","body_b":"grasp_target","contact_count":964.0,"contact_point_centroid":[0.51199,0.09606,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57346,0.21871,0.28153]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51199,0.09606,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57404,0.22355,0.2387]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5031.0,"contact_point_centroid":[0.47016,0.02802,0.03478],"force_p95":0.0693,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11812,"mean_force":0.04298,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47037,0.04727,0.03193]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5498.0,"contact_point_centroid":[0.46998,0.06658,0.03418],"force_p95":0.06943,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08041,"mean_force":0.04108,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47038,0.04727,0.03193]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1466.0,"contact_point_centroid":[0.53912,0.16287,0.31968],"force_p95":0.0118,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01609,"mean_force":0.0106,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53861,0.16285,0.31738]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1033.0,"contact_point_centroid":[0.57391,0.21872,0.28396],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01041,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57346,0.2187,0.28165]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.57662,0.22454,0.23699],"force_p95":0.01089,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01092,"mean_force":0.0099,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57596,0.2245,0.23467]}],"total_contact_groups":16},"final_pose_error":0.00983,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.51199,0.09606,0.01602],"final_tcp_position":[0.57734,0.22499,0.23831],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":2.17826,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":402.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1604.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.4812,0.04303,0.18921],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16329,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":990.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3960.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47804,0.04803,0.03976],"tcp_start":[0.4812,0.04303,0.18921],"tcp_to_object_dist_end":0.01453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48262,0.04749,0.02554],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29111,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15414,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12329.0,"raw_peak_contact_force":0.2386,"subtask_id":"grasp_1","tcp_end":[0.47035,0.04726,0.0319],"tcp_start":[0.47804,0.04803,0.03976],"tcp_to_object_dist_end":0.01382,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47418,0.04688,0.1102],"object_pos_start":[0.48262,0.04749,0.02554],"object_to_goal_dist_end":0.24328,"object_to_goal_dist_start":0.29111,"object_z_max":0.11012,"peak_contact_force":0.06833,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":42270.0,"raw_peak_contact_force":0.55815,"tcp_end":[0.46633,0.04688,0.12356],"tcp_start":[0.47035,0.04726,0.0319],"tcp_to_object_dist_end":0.0155,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51199,0.09606,0.01602],"object_pos_start":[0.47418,0.04688,0.1102],"object_to_goal_dist_end":0.26175,"object_to_goal_dist_start":0.24328,"object_z_max":0.24568,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17422.0,"raw_peak_contact_force":2.17826,"subtask_id":"transport_arc","tcp_end":[0.57101,0.2133,0.32448],"tcp_start":[0.46633,0.04688,0.12356],"tcp_to_object_dist_end":0.33523,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":241.0,"n_steps_budget":1000.0,"object_pos_end":[0.51199,0.09606,0.01602],"object_pos_start":[0.51199,0.09606,0.01602],"object_to_goal_dist_end":0.26175,"object_to_goal_dist_start":0.26175,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1997.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57734,0.22499,0.23831],"tcp_start":[0.57101,0.2133,0.32448],"tcp_to_object_dist_end":0.26516,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51199,0.09606,0.01602],"object_pos_start":[0.51199,0.09606,0.01602],"object_to_goal_dist_end":0.26175,"object_to_goal_dist_start":0.26175,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57296,0.22299,0.25843],"tcp_start":[0.57734,0.22499,0.23831],"tcp_to_object_dist_end":0.28035,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```