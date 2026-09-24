## Search State

- **Seed**: 8
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → contact → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.2594 | 0.22 | ❌ rejected |
| 10 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4248 | 0.24 | ❌ rejected |
| 9 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3303 | 0.15 | ❌ rejected |
| 8 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4211 | 0.24 | ❌ rejected |
| 7 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4221 | 0.24 | ❌ rejected |

**Proposal policy**: task_score is 0.22 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.259) — your mutation base

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

- **Composite score**: 0.259
- **task_score** (E): 0.220
- **fitness_score**: 0.567  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.143
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1025 |
| descend_1 | 1.00 | 1.00 | 0.1567 |
| contact_1 | 1.00 | 1.00 | 0.0097 |
| lift_1 | 1.00 | 1.00 | 0.1142 |
| transport_1 | 0.00 | 0.67 | 0.0773 |
| descend_place | 0.33 | 1.00 | 0.1055 |
| release_1 | 1.00 | 1.00 | 0.0221 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.211) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.516, -0.001, 0.211)→(0.517, -0.001, 0.054) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| contact_1 | contact | 1.00 / force_exceeded | (0.517, -0.001, 0.054)→(0.511, -0.001, 0.047) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 44.667 | 0.142 | 0.189 |
| lift_1 | lift | 1.00 / step_budget | (0.511, -0.001, 0.047)→(0.507, -0.001, 0.161) | (0.522, -0.001, 0.026)→(0.518, -0.001, 0.134) | 0.289→0.239 | 1.00 / 22.667 | 0.113 | 0.435 |
| transport_1 | approach | 0.00 / step_budget | (0.507, -0.001, 0.161)→(0.531, 0.055, 0.208) | (0.518, -0.001, 0.134)→(0.536, 0.061, 0.136) | 0.239→0.188 | 0.67 / 11.667 | 0.084 | 0.196 |
| descend_place | descend | 0.33 / step_budget | (0.531, 0.055, 0.208)→(0.578, 0.149, 0.198) | (0.536, 0.061, 0.136)→(0.560, 0.091, 0.016) | 0.188→0.228 | 1.00 / 8.333 | 91002.357 | 1.683 |
| release_1 | release | 1.00 / step_budget | (0.578, 0.149, 0.198)→(0.572, 0.147, 0.220) | (0.560, 0.091, 0.016)→(0.560, 0.091, 0.016) | 0.228→0.228 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.265
- phase_score: 0.297
- phase_breakdown.approach_1_score: 0.009
- phase_breakdown.descend_1_score: 0.874
- phase_breakdown.transport_arc_score: 0.038
- phase_breakdown.release_1_score: 0.255
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.589

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.589
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.265
- **Median Q (composite search score)**: 0.251
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.358


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.61875,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17374,"contact_1.contact_force":17.50131,"descend_place.place_speed":0.08772,"lift_1.lift_height":0.13041,"release_1.release_duration":0.77853,"transport_1.transport_speed":0.0128},"optimized_scores":{"best_composite_score":0.24556,"best_fitness_score":0.5527,"best_task_score":0.19345},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3912.0,"contact_point_centroid":[0.50842,0.13224,-0.00226],"force_p95":0.12719,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79598,"mean_force":0.13596,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.53253,0.15585,0.22077]},{"body_a":"world","body_b":"grasp_target","contact_count":139.0,"contact_point_centroid":[0.48017,0.04635,-0.00121],"force_p95":0.26194,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40457,"mean_force":0.05617,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47149,0.04711,0.04978]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13476.0,"contact_point_centroid":[0.47043,0.06585,0.10307],"force_p95":0.0943,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29797,"mean_force":0.05797,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46908,0.04689,0.10235]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12963.0,"contact_point_centroid":[0.46972,0.02789,0.10281],"force_p95":0.10798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29604,"mean_force":0.06034,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46905,0.04689,0.10265]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7891.0,"contact_point_centroid":[0.4869,0.05474,0.18987],"force_p95":0.13609,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25074,"mean_force":0.10492,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48245,0.07305,0.19299]},{"body_a":"world","body_b":"grasp_target","contact_count":1644.0,"contact_point_centroid":[0.48273,0.0486,-0.00213],"force_p95":0.15647,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21276,"mean_force":0.13238,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47357,0.04733,0.04852]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9239.0,"contact_point_centroid":[0.48641,0.08962,0.18912],"force_p95":0.12799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18386,"mean_force":0.08996,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48154,0.0716,0.19131]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4091.0,"contact_point_centroid":[0.47222,0.02806,0.04897],"force_p95":0.07992,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14694,"mean_force":0.05206,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47297,0.04727,0.04788]},{"body_a":"world","body_b":"grasp_target","contact_count":1228.0,"contact_point_centroid":[0.4827,0.04873,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49043,0.02021,0.25571]},{"body_a":"world","body_b":"grasp_target","contact_count":1972.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47892,0.04482,0.13224]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50837,0.13231,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55707,0.19802,0.22328]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4988.0,"contact_point_centroid":[0.47307,0.06638,0.049],"force_p95":0.07313,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07432,"mean_force":0.04413,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47297,0.04727,0.04788]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3965.0,"contact_point_centroid":[0.53479,0.15868,0.22305],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01642,"mean_force":0.01046,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.53427,0.15866,0.22072]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.55974,0.19896,0.22162],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.01002,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55925,0.19893,0.21899]}],"total_contact_groups":14},"final_pose_error":0.03761,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.50837,0.13231,0.01602],"final_tcp_position":[0.56041,0.19926,0.22165],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.79598,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":308.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1228.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48186,0.04211,0.21108],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18518,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":493.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1972.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47838,0.04776,0.05474],"tcp_start":[0.48186,0.04211,0.21108],"tcp_to_object_dist_end":0.02906,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":11.0,"n_steps_budget":600.0,"object_pos_end":[0.48266,0.04764,0.02557],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29099,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15296,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10723.0,"raw_peak_contact_force":0.21276,"subtask_id":"grasp_1","tcp_end":[0.47294,0.04727,0.04785],"tcp_start":[0.47838,0.04776,0.05474],"tcp_to_object_dist_end":0.02431,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.47897,0.04761,0.13778],"object_pos_start":[0.48266,0.04764,0.02557],"object_to_goal_dist_end":0.22811,"object_to_goal_dist_start":0.29099,"object_z_max":0.13768,"peak_contact_force":0.13382,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26578.0,"raw_peak_contact_force":0.40457,"tcp_end":[0.46929,0.04692,0.16679],"tcp_start":[0.47294,0.04727,0.04785],"tcp_to_object_dist_end":0.03059,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50345,0.1184,0.08186],"object_pos_start":[0.47897,0.04761,0.13778],"object_to_goal_dist_end":0.20109,"object_to_goal_dist_start":0.22811,"object_z_max":0.18152,"peak_contact_force":0.0,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17130.0,"raw_peak_contact_force":0.25074,"subtask_id":"transport_arc","tcp_end":[0.49964,0.10061,0.22476],"tcp_start":[0.46929,0.04692,0.16679],"tcp_to_object_dist_end":0.14405,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50837,0.13231,0.01602],"object_pos_start":[0.50345,0.1184,0.08186],"object_to_goal_dist_end":0.24641,"object_to_goal_dist_start":0.20109,"object_z_max":0.08186,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7877.0,"raw_peak_contact_force":1.79598,"tcp_end":[0.56041,0.19926,0.22165],"tcp_start":[0.49964,0.10061,0.22476],"tcp_to_object_dist_end":0.22242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50837,0.13231,0.01602],"object_pos_start":[0.50837,0.13231,0.01602],"object_to_goal_dist_end":0.24641,"object_to_goal_dist_start":0.24641,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.55584,0.19748,0.24326],"tcp_start":[0.56041,0.19926,0.22165],"tcp_to_object_dist_end":0.24112,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4125,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11712,"contact_1.contact_force":17.22967,"descend_place.place_speed":0.05358,"lift_1.lift_height":0.12077,"release_1.release_duration":0.13938,"transport_1.transport_speed":0.02409},"optimized_scores":{"best_composite_score":0.25066,"best_fitness_score":0.5578,"best_task_score":0.20261},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2117.0,"contact_point_centroid":[0.57192,0.08884,-0.00247],"force_p95":0.1763,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.64601,"mean_force":0.14808,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56373,0.11252,0.19494]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.53455,-0.02063,-0.00115],"force_p95":0.31622,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4469,"mean_force":0.06831,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52415,-0.02085,0.0481]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12905.0,"contact_point_centroid":[0.52309,-0.03975,0.09519],"force_p95":0.09355,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27235,"mean_force":0.05584,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52159,-0.02079,0.09407]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11472.0,"contact_point_centroid":[0.52317,-0.00175,0.09573],"force_p95":0.10167,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2721,"mean_force":0.06194,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52157,-0.02079,0.09467]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3177.0,"contact_point_centroid":[0.55126,0.08124,0.18953],"force_p95":0.12503,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22941,"mean_force":0.10553,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54549,0.06294,0.19408]},{"body_a":"world","body_b":"grasp_target","contact_count":1636.0,"contact_point_centroid":[0.53703,-0.02127,-0.00205],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17167,"mean_force":0.12657,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52641,-0.0209,0.04716]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11315.0,"contact_point_centroid":[0.53448,-0.00764,0.17385],"force_p95":0.11766,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17034,"mean_force":0.08084,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52943,0.01077,0.17466]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10565.0,"contact_point_centroid":[0.53421,0.02834,0.17306],"force_p95":0.13301,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16991,"mean_force":0.08642,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52908,0.00979,0.17388]},{"body_a":"world","body_b":"grasp_target","contact_count":1940.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51381,-0.00954,0.22657]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3618.0,"contact_point_centroid":[0.55089,0.04513,0.1897],"force_p95":0.12058,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13648,"mean_force":0.09191,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.54558,0.06322,0.19407]},{"body_a":"world","body_b":"grasp_target","contact_count":1224.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52955,-0.02017,0.10374]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57191,0.08905,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56782,0.13258,0.19746]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4845.0,"contact_point_centroid":[0.52532,-0.00164,0.04722],"force_p95":0.06799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09823,"mean_force":0.04504,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52579,-0.02089,0.04641]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5377.0,"contact_point_centroid":[0.52514,-0.0401,0.04751],"force_p95":0.06424,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08229,"mean_force":0.04096,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52579,-0.02089,0.04641]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2046.0,"contact_point_centroid":[0.56495,0.11469,0.19732],"force_p95":0.01112,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01612,"mean_force":0.01052,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56455,0.11469,0.19502]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.57071,0.13328,0.19519],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.00993,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57031,0.13327,0.19305]}],"total_contact_groups":16},"final_pose_error":0.10263,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.57191,0.08905,0.01602],"final_tcp_position":[0.57162,0.13343,0.19564],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273006.82719,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":486.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1940.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53012,-0.01943,0.15408],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12826,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":306.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1224.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53153,-0.02098,0.05416],"tcp_start":[0.53012,-0.01943,0.15408],"tcp_to_object_dist_end":0.02868,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":9.0,"n_steps_budget":600.0,"object_pos_end":[0.53695,-0.02099,0.02582],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31659,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13502,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":11858.0,"raw_peak_contact_force":0.17167,"subtask_id":"grasp_1","tcp_end":[0.52576,-0.02089,0.04638],"tcp_start":[0.53153,-0.02098,0.05416],"tcp_to_object_dist_end":0.02341,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":693.0,"n_steps_budget":780.0,"object_pos_end":[0.53292,-0.02097,0.12817],"object_pos_start":[0.53695,-0.02099,0.02582],"object_to_goal_dist_end":0.27228,"object_to_goal_dist_start":0.31659,"object_z_max":0.12805,"peak_contact_force":0.10273,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24523.0,"raw_peak_contact_force":0.4469,"tcp_end":[0.52179,-0.02079,0.15471],"tcp_start":[0.52576,-0.02089,0.04638],"tcp_to_object_dist_end":0.02878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54533,0.04054,0.16328],"object_pos_start":[0.53292,-0.02097,0.12817],"object_to_goal_dist_end":0.20302,"object_to_goal_dist_start":0.27228,"object_z_max":0.16326,"peak_contact_force":0.11557,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21880.0,"raw_peak_contact_force":0.17034,"subtask_id":"transport_arc","tcp_end":[0.54022,0.04092,0.19876],"tcp_start":[0.52179,-0.02079,0.15471],"tcp_to_object_dist_end":0.03584,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57191,0.08905,0.01602],"object_pos_start":[0.54533,0.04054,0.16328],"object_to_goal_dist_end":0.23947,"object_to_goal_dist_start":0.20302,"object_z_max":0.16328,"peak_contact_force":273006.82719,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10958.0,"raw_peak_contact_force":1.64601,"tcp_end":[0.57162,0.13343,0.19564],"tcp_start":[0.54022,0.04092,0.19876],"tcp_to_object_dist_end":0.18503,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57191,0.08905,0.01602],"object_pos_start":[0.57191,0.08905,0.01602],"object_to_goal_dist_end":0.23947,"object_to_goal_dist_start":0.23947,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.56638,0.13218,0.21752],"tcp_start":[0.57162,0.13343,0.19564],"tcp_to_object_dist_end":0.20614,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46154,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.24012,"contact_1.contact_force":14.03991,"descend_place.place_speed":0.0615,"lift_1.lift_height":0.12782,"release_1.release_duration":0.75696,"transport_1.transport_speed":0.04817},"optimized_scores":{"best_composite_score":0.28201,"best_fitness_score":0.58916,"best_task_score":0.26543},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2097.0,"contact_point_centroid":[0.59973,0.05295,-0.00245],"force_p95":0.17391,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.6074,"mean_force":0.1484,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59019,0.09435,0.18016]},{"body_a":"world","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.543,-0.0285,-0.00116],"force_p95":0.31601,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45236,"mean_force":0.07026,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53269,-0.02861,0.0473]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11910.0,"contact_point_centroid":[0.53175,-0.00947,0.09804],"force_p95":0.10183,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28448,"mean_force":0.06193,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5301,-0.02852,0.09646]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13483.0,"contact_point_centroid":[0.53172,-0.04748,0.09695],"force_p95":0.09457,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27654,"mean_force":0.05572,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53011,-0.02852,0.09552]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3135.0,"contact_point_centroid":[0.57024,0.06544,0.18491],"force_p95":0.1372,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22879,"mean_force":0.10843,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56438,0.04718,0.18906]},{"body_a":"world","body_b":"grasp_target","contact_count":1648.0,"contact_point_centroid":[0.54561,-0.02913,-0.00206],"force_p95":0.1384,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18108,"mean_force":0.1276,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53502,-0.02868,0.04643]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11718.0,"contact_point_centroid":[0.54663,-0.01938,0.17776],"force_p95":0.11256,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16588,"mean_force":0.07842,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54138,-0.00093,0.17826]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10943.0,"contact_point_centroid":[0.54607,0.01651,0.17696],"force_p95":0.13276,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16576,"mean_force":0.08352,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54078,-0.00208,0.17731]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3550.0,"contact_point_centroid":[0.56988,0.02907,0.18496],"force_p95":0.11936,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15117,"mean_force":0.09558,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.56437,0.04709,0.18916]},{"body_a":"world","body_b":"grasp_target","contact_count":1128.0,"contact_point_centroid":[0.5456,-0.02923,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51801,-0.01295,0.28222]},{"body_a":"world","body_b":"grasp_target","contact_count":2532.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53747,-0.02704,0.16006]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59984,0.05265,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59649,0.11236,0.17804]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4841.0,"contact_point_centroid":[0.53378,-0.00937,0.04785],"force_p95":0.06823,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09806,"mean_force":0.045,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53436,-0.02866,0.04559]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5633.0,"contact_point_centroid":[0.5339,-0.04787,0.04725],"force_p95":0.0623,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0768,"mean_force":0.03949,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53436,-0.02866,0.0456]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1996.0,"contact_point_centroid":[0.59175,0.09645,0.18213],"force_p95":0.01156,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01616,"mean_force":0.01064,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.59136,0.09645,0.17979]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.59961,0.11299,0.17635],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.01018,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59922,0.11299,0.17409]}],"total_contact_groups":16},"final_pose_error":0.06099,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.59984,0.05265,0.01602],"final_tcp_position":[0.60061,0.11315,0.17687],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.6074,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":283.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1128.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53677,-0.02535,0.26777],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.24194,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":633.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2532.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.54037,-0.02883,0.05425],"tcp_start":[0.53677,-0.02535,0.26777],"tcp_to_object_dist_end":0.02872,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":12.0,"n_steps_budget":600.0,"object_pos_end":[0.54553,-0.02873,0.02578],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26071,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13655,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":12122.0,"raw_peak_contact_force":0.18108,"subtask_id":"grasp_1","tcp_end":[0.53433,-0.02866,0.04556],"tcp_start":[0.54037,-0.02883,0.05425],"tcp_to_object_dist_end":0.02273,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.54183,-0.02867,0.13465],"object_pos_start":[0.54553,-0.02873,0.02578],"object_to_goal_dist_end":0.21806,"object_to_goal_dist_start":0.26071,"object_z_max":0.13453,"peak_contact_force":0.10303,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25540.0,"raw_peak_contact_force":0.45236,"tcp_end":[0.53039,-0.02852,0.16062],"tcp_start":[0.53433,-0.02866,0.04556],"tcp_to_object_dist_end":0.02839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55953,0.0238,0.16429],"object_pos_start":[0.54183,-0.02867,0.13465],"object_to_goal_dist_end":0.15954,"object_to_goal_dist_start":0.21806,"object_z_max":0.16426,"peak_contact_force":0.13554,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22661.0,"raw_peak_contact_force":0.16588,"subtask_id":"transport_arc","tcp_end":[0.55453,0.02382,0.19898],"tcp_start":[0.53039,-0.02852,0.16062],"tcp_to_object_dist_end":0.03505,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59984,0.05265,0.01602],"object_pos_start":[0.55953,0.0238,0.16429],"object_to_goal_dist_end":0.19896,"object_to_goal_dist_start":0.15954,"object_z_max":0.16429,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10778.0,"raw_peak_contact_force":1.6074,"tcp_end":[0.60061,0.11315,0.17687],"tcp_start":[0.55453,0.02382,0.19898],"tcp_to_object_dist_end":0.17185,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59984,0.05265,0.01602],"object_pos_start":[0.59984,0.05265,0.01602],"object_to_goal_dist_end":0.19896,"object_to_goal_dist_start":0.19896,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.5949,0.11199,0.19782],"tcp_start":[0.60061,0.11315,0.17687],"tcp_to_object_dist_end":0.1913,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```