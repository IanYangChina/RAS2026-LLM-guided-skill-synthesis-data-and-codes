## Search State

- **Seed**: 6
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0726 | 0.24 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1345 | 0.25 | ✅ accepted |
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | admittance_control | position_control | position_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | time_limit | 3 | 0.3184 | 0.17 | ✅ accepted |

**Proposal policy**: task_score is 0.24 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.073) — your mutation base

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
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: transport_arc
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.073
- **task_score** (E): 0.237
- **fitness_score**: 0.593  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1417 |
| descend_1 | 1.00 | 1.00 | 0.1192 |
| grasp_1 | 1.00 | 1.00 | 0.0115 |
| lift_1 | 0.00 | 1.00 | 0.0991 |
| transport_arc | 0.00 | 1.00 | 0.1221 |
| release_1 | 1.00 | 1.00 | 0.0239 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.022, 0.163) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 6.448 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.022, 0.163)→(0.495, 0.024, 0.044) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 27.129 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.495, 0.024, 0.044)→(0.487, 0.024, 0.036) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.272 | 1.00 / 43.000 | 0.144 | 0.206 |
| lift_1 | lift | 0.00 / step_budget | (0.487, 0.024, 0.036)→(0.483, 0.023, 0.135) | (0.500, 0.024, 0.026)→(0.491, 0.023, 0.117) | 0.272→0.228 | 1.00 / 38.333 | 0.079 | 0.542 |
| transport_arc | approach | 0.00 / step_budget | (0.483, 0.023, 0.135)→(0.533, 0.095, 0.210) | (0.491, 0.023, 0.117)→(0.536, 0.091, 0.140) | 0.228→0.150 | 1.00 / 12.000 | 0.158 | 0.735 |
| release_1 | release | 1.00 / step_budget | (0.533, 0.095, 0.210)→(0.528, 0.094, 0.234) | (0.536, 0.091, 0.140)→(0.540, 0.093, 0.016) | 0.150→0.227 | 1.00 / 4.000 | 0.105 | 1.287 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.366
- phase_score: 0.389
- phase_breakdown.descend_1_score: 0.806
- phase_breakdown.transport_arc_score: 0.229
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.130
- phase_breakdown.release_1_score: 0.171
- grasp_place_fitness: 0.660

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.660
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.366
- **Median Q (composite search score)**: 0.053
- **K-run variance**: 0.0024
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.407


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09596,"average_solve_count":198.0,"average_success_count":198.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17592,"approach_1.speed":0.05544,"descend_1.grasp_z_offset":0.01387,"descend_1.speed":0.0326,"lift_1.lift_height":0.18687,"lift_1.speed":0.05914,"transport_arc.arc_height":0.24822,"transport_arc.speed":0.12503},"optimized_scores":{"best_composite_score":0.02424,"best_fitness_score":0.54424,"best_task_score":0.15213},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":211.0,"contact_point_centroid":[0.52634,0.04065,-0.00785],"force_p95":1.19794,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.99098,"mean_force":0.37678,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51031,0.04714,0.25198]},{"body_a":"world","body_b":"grasp_target","contact_count":175.0,"contact_point_centroid":[0.49977,-0.015,-0.00117],"force_p95":0.27781,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45416,"mean_force":0.0819,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48924,-0.01526,0.04334]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19070.0,"contact_point_centroid":[0.48739,0.0039,0.09305],"force_p95":0.07722,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3087,"mean_force":0.05295,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48677,-0.01522,0.09077]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19558.0,"contact_point_centroid":[0.48757,-0.03431,0.09226],"force_p95":0.07614,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28506,"mean_force":0.05186,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48678,-0.01522,0.08995]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13912.0,"contact_point_centroid":[0.49838,0.02582,0.18709],"force_p95":0.10678,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27446,"mean_force":0.06895,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49444,0.00692,0.18604]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15561.0,"contact_point_centroid":[0.49793,-0.01219,0.18637],"force_p95":0.09671,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24389,"mean_force":0.06167,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49428,0.00659,0.18537]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":455.0,"contact_point_centroid":[0.51923,0.06541,0.22914],"force_p95":0.13042,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20804,"mean_force":0.09477,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51349,0.04755,0.23367]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":366.0,"contact_point_centroid":[0.5194,0.02949,0.22933],"force_p95":0.19584,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20305,"mean_force":0.12012,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51364,0.04757,0.23392]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50382,-0.01556,-0.00204],"force_p95":0.13448,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16444,"mean_force":0.12592,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4921,-0.0153,0.04303]},{"body_a":"world","body_b":"grasp_target","contact_count":1140.0,"contact_point_centroid":[0.50382,-0.01567,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49915,-0.00626,0.25812]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49789,-0.01432,0.12738]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4113.0,"contact_point_centroid":[0.49137,0.00392,0.04455],"force_p95":0.07661,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1196,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49094,-0.01529,0.04179]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4887.0,"contact_point_centroid":[0.49145,-0.03436,0.04364],"force_p95":0.06888,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08863,"mean_force":0.04469,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49094,-0.01529,0.04179]}],"total_contact_groups":13},"final_pose_error":0.15796,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.52757,0.04086,0.01408],"final_tcp_position":[0.51471,0.04749,0.23592],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":286.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1140.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50005,-0.01322,0.21481],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18885,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.4988,-0.01539,0.05031],"tcp_start":[0.50005,-0.01322,0.21481],"tcp_to_object_dist_end":0.0248,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50372,-0.01522,0.02585],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31208,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13228,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10800.0,"raw_peak_contact_force":0.16444,"subtask_id":"grasp_1","tcp_end":[0.49091,-0.01528,0.04176],"tcp_start":[0.4988,-0.01539,0.05031],"tcp_to_object_dist_end":0.02042,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49264,-0.01525,0.11582],"object_pos_start":[0.50372,-0.01522,0.02585],"object_to_goal_dist_end":0.25976,"object_to_goal_dist_start":0.31208,"object_z_max":0.11572,"peak_contact_force":0.06863,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38803.0,"raw_peak_contact_force":0.45416,"tcp_end":[0.48686,-0.01521,0.13856],"tcp_start":[0.49091,-0.01528,0.04176],"tcp_to_object_dist_end":0.02346,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52163,0.04737,0.20606],"object_pos_start":[0.49264,-0.01525,0.11582],"object_to_goal_dist_end":0.16016,"object_to_goal_dist_start":0.25976,"object_z_max":0.20601,"peak_contact_force":0.12765,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29473.0,"raw_peak_contact_force":0.27446,"subtask_id":"transport_arc","tcp_end":[0.51471,0.04749,0.23592],"tcp_start":[0.48686,-0.01521,0.13856],"tcp_to_object_dist_end":0.03065,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52757,0.04086,0.01408],"object_pos_start":[0.52163,0.04737,0.20606],"object_to_goal_dist_end":0.28246,"object_to_goal_dist_start":0.16016,"object_z_max":0.20606,"peak_contact_force":0.06731,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1032.0,"raw_peak_contact_force":1.99098,"subtask_id":"release_1","tcp_end":[0.51025,0.04714,0.26008],"tcp_start":[0.51471,0.04749,0.23592],"tcp_to_object_dist_end":0.24669,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34171,"average_solve_count":199.0,"average_success_count":199.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09373,"approach_1.speed":0.03176,"descend_1.grasp_z_offset":0.01791,"descend_1.speed":0.07152,"lift_1.lift_height":0.2397,"lift_1.speed":0.06496,"transport_arc.arc_height":0.22249,"transport_arc.speed":0.14106},"optimized_scores":{"best_composite_score":0.14042,"best_fitness_score":0.66042,"best_task_score":0.36605},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":725.0,"contact_point_centroid":[0.57661,0.11331,-0.00324],"force_p95":0.62273,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.65329,"mean_force":0.18447,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.56987,0.11685,0.17375]},{"body_a":"world","body_b":"grasp_target","contact_count":168.0,"contact_point_centroid":[0.5088,0.03798,-0.00117],"force_p95":0.39844,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61093,"mean_force":0.09483,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49792,0.03843,0.03357]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17466.0,"contact_point_centroid":[0.49687,0.05725,0.08321],"force_p95":0.08617,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32768,"mean_force":0.05845,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49532,0.03823,0.08159]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17378.0,"contact_point_centroid":[0.49686,0.01923,0.08475],"force_p95":0.08597,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32239,"mean_force":0.05831,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4953,0.03823,0.0829]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7572.0,"contact_point_centroid":[0.52191,0.04546,0.15774],"force_p95":0.15177,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26365,"mean_force":0.08947,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.51772,0.06393,0.15862]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8142.0,"contact_point_centroid":[0.52444,0.08429,0.15886],"force_p95":0.13572,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22193,"mean_force":0.08349,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.51967,0.06594,0.15973]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51254,0.03947,-0.0021],"force_p95":0.15215,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22179,"mean_force":0.13055,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50078,0.03868,0.03305]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4078.0,"contact_point_centroid":[0.50006,0.01938,0.03456],"force_p95":0.0797,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1428,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49959,0.03858,0.03175]},{"body_a":"world","body_b":"grasp_target","contact_count":2368.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50256,0.01781,0.2156]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57681,0.11331,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1227,"mean_force":0.12262,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57383,0.12425,0.17356]},{"body_a":"world","body_b":"grasp_target","contact_count":2924.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50622,0.03802,0.07485]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4969.0,"contact_point_centroid":[0.50007,0.05772,0.03357],"force_p95":0.07221,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08436,"mean_force":0.04471,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49959,0.03858,0.03176]},{"body_a":"left_finger","body_b":"right_finger","contact_count":488.0,"contact_point_centroid":[0.57313,0.11982,0.17533],"force_p95":0.01388,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01632,"mean_force":0.01121,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.57282,0.11981,0.17326]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.57674,0.12496,0.17158],"force_p95":0.01108,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01282,"mean_force":0.0101,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57652,0.12494,0.16914]}],"total_contact_groups":14},"final_pose_error":0.07367,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.57681,0.11331,0.01602],"final_tcp_position":[0.57795,0.12513,0.17184],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.65329,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":593.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2368.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50758,0.03637,0.13173],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10588,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":731.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2924.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50752,0.03924,0.04044],"tcp_start":[0.50758,0.03637,0.13173],"tcp_to_object_dist_end":0.01527,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51241,0.0386,0.02566],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21318,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14581,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10847.0,"raw_peak_contact_force":0.22179,"subtask_id":"grasp_1","tcp_end":[0.49956,0.03858,0.03172],"tcp_start":[0.50752,0.03924,0.04044],"tcp_to_object_dist_end":0.01421,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5066,0.03821,0.12284],"object_pos_start":[0.51241,0.0386,0.02566],"object_to_goal_dist_end":0.18211,"object_to_goal_dist_start":0.21318,"object_z_max":0.12273,"peak_contact_force":0.10127,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35012.0,"raw_peak_contact_force":0.61093,"tcp_end":[0.49545,0.03825,0.13902],"tcp_start":[0.49956,0.03858,0.03172],"tcp_to_object_dist_end":0.01965,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57681,0.11331,0.01602],"object_pos_start":[0.5066,0.03821,0.12284],"object_to_goal_dist_end":0.15075,"object_to_goal_dist_start":0.18211,"object_z_max":0.1477,"peak_contact_force":0.12271,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16927.0,"raw_peak_contact_force":1.65329,"subtask_id":"transport_arc","tcp_end":[0.57795,0.12513,0.17184],"tcp_start":[0.49545,0.03825,0.13902],"tcp_to_object_dist_end":0.15628,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57681,0.11331,0.01602],"object_pos_start":[0.57681,0.11331,0.01602],"object_to_goal_dist_end":0.15075,"object_to_goal_dist_start":0.15075,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.1227,"subtask_id":"release_1","tcp_end":[0.57224,0.12384,0.19361],"tcp_start":[0.57795,0.12513,0.17184],"tcp_to_object_dist_end":0.17796,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1117,"average_solve_count":188.0,"average_success_count":188.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10473,"approach_1.speed":0.04002,"descend_1.grasp_z_offset":0.01415,"descend_1.speed":0.06005,"lift_1.lift_height":0.28535,"lift_1.speed":0.04571,"transport_arc.arc_height":0.24706,"transport_arc.speed":0.13234},"optimized_scores":{"best_composite_score":0.0531,"best_fitness_score":0.5731,"best_task_score":0.19323},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":384.0,"contact_point_centroid":[0.51614,0.12569,-0.00509],"force_p95":0.98847,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.74868,"mean_force":0.24444,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.501,0.11186,0.23328]},{"body_a":"world","body_b":"grasp_target","contact_count":172.0,"contact_point_centroid":[0.47753,0.04632,-0.00124],"force_p95":0.45325,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56043,"mean_force":0.10777,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46873,0.04708,0.03556]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":66.0,"contact_point_centroid":[0.51164,0.09528,0.21663],"force_p95":0.21427,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33283,"mean_force":0.16472,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50523,0.11294,0.22244]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20938.0,"contact_point_centroid":[0.46599,0.06603,0.08203],"force_p95":0.07097,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30589,"mean_force":0.04902,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46623,0.04684,0.08037]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13615.0,"contact_point_centroid":[0.48094,0.08858,0.17471],"force_p95":0.11573,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27661,"mean_force":0.06987,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.47778,0.06979,0.17387]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20962.0,"contact_point_centroid":[0.466,0.02767,0.08355],"force_p95":0.07141,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26386,"mean_force":0.04822,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46623,0.04684,0.08148]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13766.0,"contact_point_centroid":[0.4792,0.04917,0.17167],"force_p95":0.12853,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24092,"mean_force":0.06884,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.4766,0.06794,0.17098]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48274,0.04852,-0.00213],"force_p95":0.15959,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23117,"mean_force":0.13258,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47146,0.04736,0.03495]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":169.0,"contact_point_centroid":[0.5102,0.12899,0.21704],"force_p95":0.17071,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22924,"mean_force":0.07742,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50494,0.11289,0.22192]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5034.0,"contact_point_centroid":[0.47013,0.028,0.0367],"force_p95":0.06927,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15207,"mean_force":0.04298,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47033,0.04724,0.03381]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48929,0.02162,0.22164]},{"body_a":"world","body_b":"grasp_target","contact_count":2612.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47754,0.04609,0.08938]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5500.0,"contact_point_centroid":[0.46995,0.06656,0.03609],"force_p95":0.06945,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07828,"mean_force":0.04104,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47034,0.04724,0.03381]}],"total_contact_groups":13},"final_pose_error":0.13921,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.51617,0.12563,0.0164],"final_tcp_position":[0.50544,0.11275,0.22288],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":19.09747,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":19.09747,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48037,0.04435,0.14332],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1174,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":653.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2612.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47798,0.048,0.04164],"tcp_start":[0.48037,0.04435,0.14332],"tcp_to_object_dist_end":0.01633,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48262,0.04751,0.02554],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.2911,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15391,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12334.0,"raw_peak_contact_force":0.23117,"subtask_id":"grasp_1","tcp_end":[0.47031,0.04724,0.03378],"tcp_start":[0.47798,0.048,0.04164],"tcp_to_object_dist_end":0.01482,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47357,0.04684,0.11144],"object_pos_start":[0.48262,0.04751,0.02554],"object_to_goal_dist_end":0.24296,"object_to_goal_dist_start":0.2911,"object_z_max":0.11135,"peak_contact_force":0.06842,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":42072.0,"raw_peak_contact_force":0.56043,"tcp_end":[0.46629,0.04686,0.12668],"tcp_start":[0.47031,0.04724,0.03378],"tcp_to_object_dist_end":0.01689,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":12.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51088,0.11274,0.19667],"object_pos_start":[0.47357,0.04684,0.11144],"object_to_goal_dist_end":0.14023,"object_to_goal_dist_start":0.24296,"object_z_max":0.19663,"peak_contact_force":0.22238,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27381.0,"raw_peak_contact_force":0.27661,"subtask_id":"transport_arc","tcp_end":[0.50544,0.11275,0.22288],"tcp_start":[0.46629,0.04686,0.12668],"tcp_to_object_dist_end":0.02677,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51617,0.12563,0.0164],"object_pos_start":[0.51088,0.11274,0.19667],"object_to_goal_dist_end":0.24658,"object_to_goal_dist_start":0.14023,"object_z_max":0.19667,"peak_contact_force":0.1245,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":619.0,"raw_peak_contact_force":1.74868,"subtask_id":"release_1","tcp_end":[0.50089,0.11184,0.24715],"tcp_start":[0.50544,0.11275,0.22288],"tcp_to_object_dist_end":0.23166,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```