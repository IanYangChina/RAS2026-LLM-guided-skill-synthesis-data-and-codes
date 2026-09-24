## Search State

- **Seed**: 8
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4221 | 0.24 | ❌ rejected |
| 6 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4211 | 0.24 | ❌ rejected |
| 5 | approach → descend → contact → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.2318 | 0.17 | ❌ rejected |
| 4 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4199 | 0.23 | ❌ rejected |
| 3 | approach → descend → contact → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | 0.2086 | 0.21 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`
- Frozen object start: [0.48269722766055606, 0.048727684333792556, 0.03]
- Frozen task target: [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]
- Goal object position: (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5818710838485517, 0.2288548935820029, 0.2304844767544324)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.48269722766055606, 0.048727684333792556, 0.03)
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
  frozen_object_start: [0.4827, 0.0487, 0.03]
  frozen_task_target: [0.5819, 0.2289, 0.2305]
  frozen_object_starts: {'grasp_target': [0.48269722766055606, 0.048727684333792556, 0.03]}
  frozen_targets: {'place_target': [0.5818710838485517, 0.2288548935820029, 0.2304844767544324]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c

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

## Current Skill (Q=0.422) — your mutation base

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
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.08
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.08
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
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.02
    orientation:
      mode: keep_current
  subtask_id: descend_1
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
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
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
- id: transport_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.1
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
- id: release_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  end_effector_action: open
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.08]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_1** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.422
- **task_score** (E): 0.239
- **fitness_score**: 0.575  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.320

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1141 |
| descend_1 | 1.00 | 1.00 | 0.1410 |
| contact_1 | 1.00 | 1.00 | 0.0096 |
| lift_1 | 1.00 | 1.00 | 0.1080 |
| transport_1 | 0.00 | 1.00 | 0.0953 |
| release_1 | 0.33 | 1.00 | 0.1058 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.517, -0.001, 0.195) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.517, -0.001, 0.195)→(0.517, -0.001, 0.055) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| contact_1 | contact | 1.00 / force_exceeded | (0.517, -0.001, 0.055)→(0.511, -0.001, 0.047) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 43.667 | 0.142 | 0.187 |
| lift_1 | lift | 1.00 / step_budget | (0.511, -0.001, 0.047)→(0.507, -0.001, 0.155) | (0.522, -0.001, 0.026)→(0.518, -0.001, 0.128) | 0.289→0.241 | 1.00 / 23.333 | 0.113 | 0.430 |
| transport_1 | approach | 0.00 / step_budget | (0.507, -0.001, 0.155)→(0.540, 0.074, 0.203) | (0.518, -0.001, 0.128)→(0.545, 0.083, 0.105) | 0.241→0.192 | 1.00 / 13.000 | 0.368 | 0.695 |
| release_1 | descend | 0.33 / step_budget | (0.540, 0.074, 0.203)→(0.584, 0.169, 0.189) | (0.545, 0.083, 0.105)→(0.567, 0.112, 0.016) | 0.192→0.217 | 1.00 / 4.000 | 0.123 | 1.306 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.291
- phase_score: 0.324
- phase_breakdown.approach_1_score: 0.081
- phase_breakdown.descend_1_score: 0.869
- phase_breakdown.transport_arc_score: 0.055
- phase_breakdown.release_1_score: 0.355
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.602

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.602
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.291
- **Median Q (composite search score)**: 0.413
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.378


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2cbd02033d1f1347f2ac2d0b012406a96501e6b48f5b172bd88b34d6c745630c`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5745d7c2d025a63f908a4bf0f58182445bb06541d436718f39304ac5569d60c0`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83221,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19242,"contact_1.contact_force":5.74322,"lift_1.lift_height":0.12773,"transport_1.transport_speed":0.07055},"optimized_scores":{"best_composite_score":0.40452,"best_fitness_score":0.55786,"best_task_score":0.20412},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":36.0,"contact_point_centroid":[0.51694,0.13631,-0.00673],"force_p95":1.71726,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.74394,"mean_force":1.08473,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50975,0.11679,0.22274]},{"body_a":"world","body_b":"grasp_target","contact_count":4600.0,"contact_point_centroid":[0.51651,0.148,-0.00219],"force_p95":0.12358,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86489,"mean_force":0.12572,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.54436,0.17466,0.21945]},{"body_a":"world","body_b":"grasp_target","contact_count":135.0,"contact_point_centroid":[0.48011,0.04631,-0.00122],"force_p95":0.2731,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40167,"mean_force":0.05619,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4716,0.0471,0.05007]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13064.0,"contact_point_centroid":[0.47045,0.06583,0.10232],"force_p95":0.09438,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29766,"mean_force":0.05762,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46918,0.04688,0.10172]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12479.0,"contact_point_centroid":[0.46973,0.02787,0.10176],"force_p95":0.10944,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29606,"mean_force":0.06022,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46915,0.04688,0.10174]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7659.0,"contact_point_centroid":[0.4914,0.0618,0.18682],"force_p95":0.13535,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25143,"mean_force":0.1045,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48691,0.08012,0.19]},{"body_a":"world","body_b":"grasp_target","contact_count":1640.0,"contact_point_centroid":[0.48273,0.0486,-0.00213],"force_p95":0.15675,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21271,"mean_force":0.13242,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47364,0.04731,0.04882]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8923.0,"contact_point_centroid":[0.49087,0.0966,0.18623],"force_p95":0.12759,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18136,"mean_force":0.09037,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48595,0.07856,0.18861]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4092.0,"contact_point_centroid":[0.4723,0.02805,0.04917],"force_p95":0.0798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14665,"mean_force":0.05206,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47306,0.04726,0.04819]},{"body_a":"world","body_b":"grasp_target","contact_count":1052.0,"contact_point_centroid":[0.4827,0.04873,-0.00188],"force_p95":0.1365,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12309,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49076,0.01969,0.2645]},{"body_a":"world","body_b":"grasp_target","contact_count":2180.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47921,0.04438,0.14099]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4989.0,"contact_point_centroid":[0.47315,0.06637,0.04922],"force_p95":0.07312,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07428,"mean_force":0.0441,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47306,0.04726,0.0482]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4107.0,"contact_point_centroid":[0.5431,0.17176,0.22213],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01661,"mean_force":0.01043,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.5426,0.17173,0.21986]}],"total_contact_groups":13},"final_pose_error":0.02369,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.51648,0.14797,0.01602],"final_tcp_position":[0.56837,0.21155,0.22158],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.74394,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":264.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1052.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48233,0.04123,0.22875],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":545.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2180.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47843,0.04774,0.05488],"tcp_start":[0.48233,0.04123,0.22875],"tcp_to_object_dist_end":0.02919,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":10.0,"n_steps_budget":600.0,"object_pos_end":[0.48266,0.04764,0.02556],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29099,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15329,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10721.0,"raw_peak_contact_force":0.21271,"subtask_id":"grasp_1","tcp_end":[0.47303,0.04725,0.04817],"tcp_start":[0.47843,0.04774,0.05488],"tcp_to_object_dist_end":0.02457,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.47888,0.04763,0.13502],"object_pos_start":[0.48266,0.04764,0.02556],"object_to_goal_dist_end":0.22926,"object_to_goal_dist_start":0.29099,"object_z_max":0.13491,"peak_contact_force":0.13302,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25678.0,"raw_peak_contact_force":0.40167,"tcp_end":[0.46936,0.0469,0.16433],"tcp_start":[0.47303,0.04725,0.04817],"tcp_to_object_dist_end":0.03083,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51298,0.14408,0.00038],"object_pos_start":[0.47888,0.04763,0.13502],"object_to_goal_dist_end":0.25472,"object_to_goal_dist_start":0.22926,"object_z_max":0.17799,"peak_contact_force":0.86489,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16618.0,"raw_peak_contact_force":1.74394,"subtask_id":"transport_arc","tcp_end":[0.50993,0.11708,0.223],"tcp_start":[0.46936,0.0469,0.16433],"tcp_to_object_dist_end":0.22428,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51648,0.14797,0.01602],"object_pos_start":[0.51298,0.14408,0.00038],"object_to_goal_dist_end":0.23836,"object_to_goal_dist_start":0.25472,"object_z_max":0.01671,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8707.0,"raw_peak_contact_force":0.86489,"subtask_id":"release_1","tcp_end":[0.56522,0.2103,0.21409],"tcp_start":[0.50993,0.11708,0.223],"tcp_to_object_dist_end":0.21329,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2b35d39beba75b46a5edd8e67b975c00ef2c88fb75a3753bdd32db5918adf9e2`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82979,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16635,"contact_1.contact_force":6.24412,"lift_1.lift_height":0.12536,"transport_1.transport_speed":0.0884},"optimized_scores":{"best_composite_score":0.41296,"best_fitness_score":0.56629,"best_task_score":0.22039},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3126.0,"contact_point_centroid":[0.58068,0.10953,-0.00233],"force_p95":0.12813,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.63439,"mean_force":0.13919,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.57697,0.14877,0.1974]},{"body_a":"world","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.53473,-0.02057,-0.00115],"force_p95":0.30776,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44507,"mean_force":0.06686,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52438,-0.02087,0.04863]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11878.0,"contact_point_centroid":[0.52341,-0.00178,0.09791],"force_p95":0.10158,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29503,"mean_force":0.06228,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5218,-0.02081,0.09706]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13247.0,"contact_point_centroid":[0.52322,-0.03976,0.09792],"force_p95":0.09393,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29205,"mean_force":0.0566,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52181,-0.02081,0.09708]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2257.0,"contact_point_centroid":[0.55998,0.10394,0.19455],"force_p95":0.13741,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23601,"mean_force":0.10927,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.55417,0.08568,0.19945]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10211.0,"contact_point_centroid":[0.53874,0.03999,0.17786],"force_p95":0.13365,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17271,"mean_force":0.08917,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53357,0.02147,0.17909]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11066.0,"contact_point_centroid":[0.53914,0.00454,0.17867],"force_p95":0.11788,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17138,"mean_force":0.0824,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53407,0.0229,0.1799]},{"body_a":"world","body_b":"grasp_target","contact_count":1632.0,"contact_point_centroid":[0.53703,-0.02131,-0.00205],"force_p95":0.13612,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16542,"mean_force":0.12661,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52663,-0.02091,0.04767]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2591.0,"contact_point_centroid":[0.55967,0.06785,0.19486],"force_p95":0.12241,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15029,"mean_force":0.09405,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.55424,0.08588,0.19943]},{"body_a":"world","body_b":"grasp_target","contact_count":1396.0,"contact_point_centroid":[0.53702,-0.02132,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51353,-0.00918,0.25062]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4834.0,"contact_point_centroid":[0.52551,-0.0017,0.04736],"force_p95":0.06836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12529,"mean_force":0.04512,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52601,-0.0209,0.04694]},{"body_a":"world","body_b":"grasp_target","contact_count":1788.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52932,-0.01987,0.12763]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5099.0,"contact_point_centroid":[0.52579,-0.0401,0.04807],"force_p95":0.06614,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08771,"mean_force":0.04299,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52602,-0.0209,0.04694]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2453.0,"contact_point_centroid":[0.57686,0.14627,0.20068],"force_p95":0.01126,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01609,"mean_force":0.0106,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.57645,0.14626,0.19844]}],"total_contact_groups":14},"final_pose_error":0.06175,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.5807,0.10962,0.01602],"final_tcp_position":[0.58608,0.17166,0.1985],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.63439,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":350.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1396.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52947,-0.01883,0.20209],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17625,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":447.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1788.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53174,-0.02099,0.0545],"tcp_start":[0.52947,-0.01883,0.20209],"tcp_to_object_dist_end":0.02897,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":8.0,"n_steps_budget":600.0,"object_pos_end":[0.53695,-0.02103,0.02582],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31662,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13567,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":11565.0,"raw_peak_contact_force":0.16542,"subtask_id":"grasp_1","tcp_end":[0.52599,-0.0209,0.0469],"tcp_start":[0.53174,-0.02099,0.0545],"tcp_to_object_dist_end":0.02376,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.53273,-0.02099,0.13253],"object_pos_start":[0.53695,-0.02103,0.02582],"object_to_goal_dist_end":0.27111,"object_to_goal_dist_start":0.31662,"object_z_max":0.13242,"peak_contact_force":0.1025,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25272.0,"raw_peak_contact_force":0.44507,"tcp_end":[0.52206,-0.02081,0.15981],"tcp_start":[0.52599,-0.0209,0.0469],"tcp_to_object_dist_end":0.02929,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55478,0.06539,0.16834],"object_pos_start":[0.53273,-0.02099,0.13253],"object_to_goal_dist_end":0.17599,"object_to_goal_dist_start":0.27111,"object_z_max":0.16831,"peak_contact_force":0.11466,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21277.0,"raw_peak_contact_force":0.17271,"subtask_id":"transport_arc","tcp_end":[0.54934,0.06568,0.20467],"tcp_start":[0.52206,-0.02081,0.15981],"tcp_to_object_dist_end":0.03674,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5807,0.10962,0.01602],"object_pos_start":[0.55478,0.06539,0.16834],"object_to_goal_dist_end":0.22685,"object_to_goal_dist_start":0.17599,"object_z_max":0.16834,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10427.0,"raw_peak_contact_force":1.63439,"subtask_id":"release_1","tcp_end":[0.58257,0.17058,0.19087],"tcp_start":[0.54934,0.06568,0.20467],"tcp_to_object_dist_end":0.18518,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `530652a2467d9ac78fab654e7ed7fc5283ca1649270bc8f158e04c16074f9f95`; realized-scene SHA-256: `9bdc6de22965641ffcaccb8421100561fe91fb98e16735236cc25272572d8879`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5456,-0.02923,0.03]},{"name":"goal","value":[0.63284,0.16493,0.17692]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5456,-0.02923,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63284,0.16493,0.17692]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81618,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11952,"contact_1.contact_force":1.82867,"lift_1.lift_height":0.10741,"transport_1.transport_speed":0.07267},"optimized_scores":{"best_composite_score":0.44878,"best_fitness_score":0.60212,"best_task_score":0.29146},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1827.0,"contact_point_centroid":[0.60309,0.07888,-0.0025],"force_p95":0.22435,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.41899,"mean_force":0.14342,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.60237,0.11833,0.16844]},{"body_a":"world","body_b":"grasp_target","contact_count":149.0,"contact_point_centroid":[0.54334,-0.02839,-0.00116],"force_p95":0.29144,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44303,"mean_force":0.06829,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53232,-0.02854,0.04728]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10335.0,"contact_point_centroid":[0.53118,-0.00937,0.09014],"force_p95":0.09898,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32141,"mean_force":0.06009,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52972,-0.02845,0.08842]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11758.0,"contact_point_centroid":[0.53113,-0.04744,0.08935],"force_p95":0.09095,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28096,"mean_force":0.05383,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52973,-0.02845,0.0878]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5274.0,"contact_point_centroid":[0.58263,0.09057,0.16884],"force_p95":0.13277,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24533,"mean_force":0.10438,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.57742,0.0723,0.17297]},{"body_a":"world","body_b":"grasp_target","contact_count":1648.0,"contact_point_centroid":[0.54561,-0.02909,-0.00207],"force_p95":0.13939,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18351,"mean_force":0.12786,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53466,-0.02862,0.0464]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5766.0,"contact_point_centroid":[0.58271,0.05455,0.16883],"force_p95":0.11992,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18152,"mean_force":0.09531,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.57764,0.07267,0.17298]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11591.0,"contact_point_centroid":[0.55005,0.0259,0.15897],"force_p95":0.12052,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16926,"mean_force":0.07961,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5451,0.00729,0.15941]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12923.0,"contact_point_centroid":[0.54913,-0.01192,0.15837],"force_p95":0.11771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16543,"mean_force":0.0719,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54474,0.00664,0.15895]},{"body_a":"world","body_b":"grasp_target","contact_count":2016.0,"contact_point_centroid":[0.5456,-0.02923,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5178,-0.01316,0.22707]},{"body_a":"world","body_b":"grasp_target","contact_count":1228.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53777,-0.0277,0.10441]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4357.0,"contact_point_centroid":[0.53409,-0.00932,0.04878],"force_p95":0.072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09863,"mean_force":0.04959,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53399,-0.0286,0.04557]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5640.0,"contact_point_centroid":[0.53359,-0.04774,0.04752],"force_p95":0.0623,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07833,"mean_force":0.03945,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.534,-0.0286,0.04557]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1001.0,"contact_point_centroid":[0.60303,0.11752,0.17248],"force_p95":0.01281,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01648,"mean_force":0.01073,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.60271,0.11751,0.17031]}],"total_contact_groups":14},"final_pose_error":0.04716,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.60305,0.07878,0.01602],"final_tcp_position":[0.60745,0.12581,0.16991],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.41899,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":505.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2016.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53813,-0.02675,0.15553],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12975,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":307.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1228.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53998,-0.02876,0.05422],"tcp_start":[0.53813,-0.02675,0.15553],"tcp_to_object_dist_end":0.02875,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":12.0,"n_steps_budget":600.0,"object_pos_end":[0.54553,-0.02861,0.02577],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26062,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13658,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":11645.0,"raw_peak_contact_force":0.18351,"subtask_id":"grasp_1","tcp_end":[0.53397,-0.0286,0.04554],"tcp_start":[0.53998,-0.02876,0.05422],"tcp_to_object_dist_end":0.0229,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":603.0,"n_steps_budget":690.0,"object_pos_end":[0.54196,-0.02861,0.11535],"object_pos_start":[0.54553,-0.02861,0.02577],"object_to_goal_dist_end":0.22251,"object_to_goal_dist_start":0.26062,"object_z_max":0.11524,"peak_contact_force":0.10334,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22242.0,"raw_peak_contact_force":0.44303,"tcp_end":[0.52984,-0.02845,0.14029],"tcp_start":[0.53397,-0.0286,0.04554],"tcp_to_object_dist_end":0.02772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56689,0.03826,0.1474],"object_pos_start":[0.54196,-0.02861,0.11535],"object_to_goal_dist_end":0.14583,"object_to_goal_dist_start":0.22251,"object_z_max":0.14738,"peak_contact_force":0.12323,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24514.0,"raw_peak_contact_force":0.16926,"subtask_id":"transport_arc","tcp_end":[0.56182,0.03856,0.1809],"tcp_start":[0.52984,-0.02845,0.14029],"tcp_to_object_dist_end":0.03388,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60305,0.07878,0.01602],"object_pos_start":[0.56689,0.03826,0.1474],"object_to_goal_dist_end":0.18493,"object_to_goal_dist_start":0.14583,"object_z_max":0.1474,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":13868.0,"raw_peak_contact_force":1.41899,"subtask_id":"release_1","tcp_end":[0.60353,0.12494,0.16206],"tcp_start":[0.56182,0.03856,0.1809],"tcp_to_object_dist_end":0.15316,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```