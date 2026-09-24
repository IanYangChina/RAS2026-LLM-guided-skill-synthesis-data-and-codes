## Search State

- **Seed**: 8
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3303 | 0.15 | ❌ rejected |
| 8 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4211 | 0.24 | ❌ rejected |
| 7 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4221 | 0.24 | ❌ rejected |
| 6 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4211 | 0.24 | ❌ rejected |
| 5 | approach → descend → contact → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.2318 | 0.17 | ❌ rejected |

**Proposal policy**: task_score is 0.15 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.330) — your mutation base

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

- **Composite score**: 0.330
- **task_score** (E): 0.155
- **fitness_score**: 0.534  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0672 |
| descend_1 | 1.00 | 1.00 | 0.2026 |
| contact_1 | 1.00 | 1.00 | 0.0096 |
| lift_1 | 0.33 | 1.00 | 0.1408 |
| transport_1 | 0.00 | 1.00 | 0.1224 |
| release_1 | 1.00 | 1.00 | 0.1710 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.001, 0.257) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.516, -0.001, 0.257)→(0.517, -0.001, 0.054) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| contact_1 | contact | 1.00 / force_exceeded | (0.517, -0.001, 0.054)→(0.511, -0.001, 0.047) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 43.000 | 0.141 | 0.186 |
| lift_1 | lift | 0.33 / step_budget | (0.511, -0.001, 0.047)→(0.507, -0.001, 0.188) | (0.522, -0.001, 0.026)→(0.517, -0.000, 0.159) | 0.289→0.233 | 1.00 / 22.667 | 82.809 | 0.421 |
| transport_1 | approach | 0.00 / step_budget | (0.507, -0.001, 0.188)→(0.535, 0.059, 0.290) | (0.517, -0.000, 0.159)→(0.527, 0.018, 0.016) | 0.233→0.282 | 1.00 / 8.667 | 91002.216 | 1.872 |
| release_1 | descend | 1.00 / step_budget | (0.535, 0.059, 0.290)→(0.594, 0.188, 0.197) | (0.527, 0.018, 0.016)→(0.527, 0.018, 0.016) | 0.282→0.282 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.185
- phase_score: 0.328
- phase_breakdown.approach_1_score: 0.038
- phase_breakdown.descend_1_score: 0.871
- phase_breakdown.transport_arc_score: 0.026
- phase_breakdown.release_1_score: 0.498
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.549

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.549
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.185
- **Median Q (composite search score)**: 0.334
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.419


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85799,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.27479,"contact_1.contact_force":9.45383,"lift_1.lift_height":0.32179,"transport_1.arc_height":0.29881,"transport_1.transport_speed":0.14971},"optimized_scores":{"best_composite_score":0.3338,"best_fitness_score":0.53714,"best_task_score":0.16272},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3220.0,"contact_point_centroid":[0.48739,0.09013,-0.00233],"force_p95":0.13156,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.90913,"mean_force":0.13893,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48798,0.08064,0.28346]},{"body_a":"world","body_b":"grasp_target","contact_count":135.0,"contact_point_centroid":[0.48008,0.04633,-0.00119],"force_p95":0.27334,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40227,"mean_force":0.05549,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47158,0.04723,0.04992]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15172.0,"contact_point_centroid":[0.47062,0.02808,0.11732],"force_p95":0.1276,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29754,"mean_force":0.06705,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46919,0.04701,0.11762]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16269.0,"contact_point_centroid":[0.47148,0.06578,0.11996],"force_p95":0.10243,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29697,"mean_force":0.06228,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46922,0.04701,0.11953]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":988.0,"contact_point_centroid":[0.47553,0.06657,0.21514],"force_p95":0.1881,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28506,"mean_force":0.09787,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.46906,0.04869,0.21706]},{"body_a":"world","body_b":"grasp_target","contact_count":1644.0,"contact_point_centroid":[0.48273,0.04861,-0.00212],"force_p95":0.15414,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2101,"mean_force":0.13166,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47363,0.04744,0.04866]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":674.0,"contact_point_centroid":[0.47537,0.03022,0.21323],"force_p95":0.17913,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18792,"mean_force":0.11949,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.46904,0.04857,0.21663]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4095.0,"contact_point_centroid":[0.47228,0.02817,0.04908],"force_p95":0.07958,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14489,"mean_force":0.05204,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47304,0.04738,0.04802]},{"body_a":"world","body_b":"grasp_target","contact_count":972.0,"contact_point_centroid":[0.4827,0.04873,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12313,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4904,0.02076,0.29803]},{"body_a":"world","body_b":"grasp_target","contact_count":3024.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47967,0.04434,0.17548]},{"body_a":"world","body_b":"grasp_target","contact_count":3540.0,"contact_point_centroid":[0.48737,0.0901,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.54812,0.17912,0.26195]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4972.0,"contact_point_centroid":[0.47314,0.06649,0.0491],"force_p95":0.07274,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07379,"mean_force":0.0442,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47304,0.04738,0.04802]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3239.0,"contact_point_centroid":[0.48919,0.08207,0.28805],"force_p95":0.01106,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01606,"mean_force":0.0106,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.48887,0.08205,0.28583]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3164.0,"contact_point_centroid":[0.54369,0.17075,0.27228],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01266,"mean_force":0.01036,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.54316,0.17073,0.27008]}],"total_contact_groups":14},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.48737,0.0901,0.01602],"final_tcp_position":[0.57541,0.22225,0.22674],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273006.40369,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":244.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":972.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48284,0.04096,0.29867],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":756.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3024.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47846,0.04788,0.0549],"tcp_start":[0.48284,0.04096,0.29867],"tcp_to_object_dist_end":0.0292,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":11.0,"n_steps_budget":600.0,"object_pos_end":[0.48265,0.04772,0.0256],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29092,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15092,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10711.0,"raw_peak_contact_force":0.2101,"subtask_id":"grasp_1","tcp_end":[0.47301,0.04738,0.04799],"tcp_start":[0.47846,0.04788,0.0549],"tcp_to_object_dist_end":0.02438,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47783,0.04858,0.1788],"object_pos_start":[0.48265,0.04772,0.0256],"object_to_goal_dist_end":0.21446,"object_to_goal_dist_start":0.29092,"object_z_max":0.17861,"peak_contact_force":0.12979,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":31576.0,"raw_peak_contact_force":0.40227,"tcp_end":[0.46958,0.04705,0.21074],"tcp_start":[0.47301,0.04738,0.04799],"tcp_to_object_dist_end":0.03303,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48737,0.0901,0.01602],"object_pos_start":[0.47783,0.04858,0.1788],"object_to_goal_dist_end":0.27236,"object_to_goal_dist_start":0.21446,"object_z_max":0.18981,"peak_contact_force":273006.40369,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8121.0,"raw_peak_contact_force":1.90913,"subtask_id":"transport_arc","tcp_end":[0.50972,0.11495,0.32225],"tcp_start":[0.46958,0.04705,0.21074],"tcp_to_object_dist_end":0.30804,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":735.0,"n_steps_budget":1000.0,"object_pos_end":[0.48737,0.0901,0.01602],"object_pos_start":[0.48737,0.0901,0.01602],"object_to_goal_dist_end":0.27236,"object_to_goal_dist_start":0.27236,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6704.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57234,0.22096,0.219],"tcp_start":[0.50972,0.11495,0.32225],"tcp_to_object_dist_end":0.25602,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.84884,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.25288,"contact_1.contact_force":18.24257,"lift_1.lift_height":0.38516,"transport_1.arc_height":0.29976,"transport_1.transport_speed":0.13236},"optimized_scores":{"best_composite_score":0.31146,"best_fitness_score":0.51479,"best_task_score":0.11689},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3103.0,"contact_point_centroid":[0.53815,-0.02091,-0.00237],"force_p95":0.12469,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.93559,"mean_force":0.13791,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5327,0.01579,0.27342]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.53457,-0.02058,-0.00114],"force_p95":0.30764,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41561,"mean_force":0.06484,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52455,-0.02089,0.0485]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1098.0,"contact_point_centroid":[0.52811,0.00053,0.21348],"force_p95":0.18876,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30998,"mean_force":0.10581,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52157,-0.01812,0.21414]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15189.0,"contact_point_centroid":[0.52455,-0.00187,0.11797],"force_p95":0.10198,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30267,"mean_force":0.06622,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52206,-0.02083,0.11713]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16822.0,"contact_point_centroid":[0.52425,-0.03971,0.11713],"force_p95":0.09625,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29431,"mean_force":0.06059,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52206,-0.02083,0.11635]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1549.0,"contact_point_centroid":[0.52778,-0.03572,0.2139],"force_p95":0.13041,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20244,"mean_force":0.07867,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52155,-0.01772,0.21508]},{"body_a":"world","body_b":"grasp_target","contact_count":1632.0,"contact_point_centroid":[0.53703,-0.02125,-0.00205],"force_p95":0.13532,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16468,"mean_force":0.12648,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52679,-0.02093,0.04751]},{"body_a":"world","body_b":"grasp_target","contact_count":904.0,"contact_point_centroid":[0.53702,-0.02132,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12317,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51387,-0.00917,0.28844]},{"body_a":"world","body_b":"grasp_target","contact_count":2684.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52905,-0.0194,0.16585]},{"body_a":"world","body_b":"grasp_target","contact_count":4600.0,"contact_point_centroid":[0.53814,-0.02091,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.57624,0.14233,0.24628]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4116.0,"contact_point_centroid":[0.52718,-0.00171,0.0483],"force_p95":0.07695,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12119,"mean_force":0.05203,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52618,-0.02092,0.04678]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4885.0,"contact_point_centroid":[0.52633,-0.03999,0.04824],"force_p95":0.06832,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08749,"mean_force":0.04447,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52618,-0.02092,0.04678]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3141.0,"contact_point_centroid":[0.5336,0.01734,0.27806],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01623,"mean_force":0.01044,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53327,0.01734,0.27575]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4303.0,"contact_point_centroid":[0.57364,0.13288,0.25488],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01036,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.57311,0.13287,0.25258]}],"total_contact_groups":14},"final_pose_error":0.02269,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.53814,-0.02091,0.01602],"final_tcp_position":[0.60011,0.20758,0.20941],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.93559,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":227.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":904.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52833,-0.01785,0.27959],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25375,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":671.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2684.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53188,-0.02101,0.05434],"tcp_start":[0.52833,-0.01785,0.27959],"tcp_to_object_dist_end":0.02878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":8.0,"n_steps_budget":600.0,"object_pos_end":[0.53695,-0.02094,0.02583],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31655,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13405,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10633.0,"raw_peak_contact_force":0.16468,"subtask_id":"grasp_1","tcp_end":[0.52615,-0.02092,0.04675],"tcp_start":[0.53188,-0.02101,0.05434],"tcp_to_object_dist_end":0.02354,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53224,-0.02086,0.17879],"object_pos_start":[0.53695,-0.02094,0.02583],"object_to_goal_dist_end":0.26215,"object_to_goal_dist_start":0.31655,"object_z_max":0.1786,"peak_contact_force":0.10415,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32155.0,"raw_peak_contact_force":0.41561,"tcp_end":[0.52255,-0.02083,0.20807],"tcp_start":[0.52615,-0.02092,0.04675],"tcp_to_object_dist_end":0.03084,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53814,-0.02091,0.01602],"object_pos_start":[0.53224,-0.02086,0.17879],"object_to_goal_dist_end":0.32198,"object_to_goal_dist_start":0.26215,"object_z_max":0.19028,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8891.0,"raw_peak_contact_force":1.93559,"subtask_id":"transport_arc","tcp_end":[0.54444,0.04786,0.30745],"tcp_start":[0.52255,-0.02083,0.20807],"tcp_to_object_dist_end":0.2995,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53814,-0.02091,0.01602],"object_pos_start":[0.53814,-0.02091,0.01602],"object_to_goal_dist_end":0.32198,"object_to_goal_dist_start":0.32198,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8903.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.59679,0.20634,0.2012],"tcp_start":[0.54444,0.04786,0.30745],"tcp_to_object_dist_end":0.29895,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82857,"average_solve_count":140.0,"average_success_count":140.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15768,"contact_1.contact_force":15.77996,"lift_1.lift_height":0.11073,"transport_1.arc_height":0.29666,"transport_1.transport_speed":0.1201},"optimized_scores":{"best_composite_score":0.34574,"best_fitness_score":0.54907,"best_task_score":0.18534},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1373.0,"contact_point_centroid":[0.55539,-0.01406,-0.00274],"force_p95":0.37944,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.77014,"mean_force":0.15587,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54398,0.004,0.22623]},{"body_a":"world","body_b":"grasp_target","contact_count":151.0,"contact_point_centroid":[0.54308,-0.02849,-0.00117],"force_p95":0.29134,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4461,"mean_force":0.06955,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53248,-0.02857,0.04729]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10826.0,"contact_point_centroid":[0.53131,-0.0094,0.09154],"force_p95":0.0994,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28541,"mean_force":0.06013,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52989,-0.02848,0.08985]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12247.0,"contact_point_centroid":[0.53131,-0.04746,0.09054],"force_p95":0.09202,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27862,"mean_force":0.05418,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5299,-0.02848,0.08903]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6205.0,"contact_point_centroid":[0.53614,-0.00269,0.1713],"force_p95":0.13751,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23091,"mean_force":0.08534,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53026,-0.02135,0.17082]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6969.0,"contact_point_centroid":[0.53634,-0.03918,0.17282],"force_p95":0.10565,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21595,"mean_force":0.07682,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.53059,-0.02073,0.17271]},{"body_a":"world","body_b":"grasp_target","contact_count":1648.0,"contact_point_centroid":[0.54561,-0.02913,-0.00207],"force_p95":0.13905,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18264,"mean_force":0.12779,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53483,-0.02864,0.04642]},{"body_a":"world","body_b":"grasp_target","contact_count":1612.0,"contact_point_centroid":[0.5456,-0.02923,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51754,-0.01285,0.24567]},{"body_a":"world","body_b":"grasp_target","contact_count":1668.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53758,-0.02743,0.12288]},{"body_a":"world","body_b":"grasp_target","contact_count":4600.0,"contact_point_centroid":[0.55543,-0.01408,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.58823,0.09031,0.20016]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4839.0,"contact_point_centroid":[0.53365,-0.00933,0.04803],"force_p95":0.06826,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09857,"mean_force":0.045,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53417,-0.02862,0.04559]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5637.0,"contact_point_centroid":[0.53374,-0.04783,0.0474],"force_p95":0.06245,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07779,"mean_force":0.03949,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53417,-0.02862,0.04559]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1248.0,"contact_point_centroid":[0.5452,0.00549,0.23085],"force_p95":0.01205,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01578,"mean_force":0.01055,"phase_index":4.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5448,0.0055,0.22853]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4280.0,"contact_point_centroid":[0.5848,0.08288,0.2066],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01042,"phase_index":5.0,"phase_name":"release_1","phase_type":"descend","tcp_position_centroid":[0.58447,0.08288,0.20428]}],"total_contact_groups":14},"final_pose_error":0.03143,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.55543,-0.01408,0.01602],"final_tcp_position":[0.61522,0.13899,0.17905],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":248.1931,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":404.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1612.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53758,-0.02619,0.19276],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16696,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":417.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1668.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.54016,-0.02878,0.05424],"tcp_start":[0.53758,-0.02619,0.19276],"tcp_to_object_dist_end":0.02875,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":12.0,"n_steps_budget":600.0,"object_pos_end":[0.54553,-0.0287,0.02577],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.2607,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13711,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":12124.0,"raw_peak_contact_force":0.18264,"subtask_id":"grasp_1","tcp_end":[0.53414,-0.02862,0.04556],"tcp_start":[0.54016,-0.02878,0.05424],"tcp_to_object_dist_end":0.02283,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.54195,-0.02863,0.11853],"object_pos_start":[0.54553,-0.0287,0.02577],"object_to_goal_dist_end":0.22166,"object_to_goal_dist_start":0.2607,"object_z_max":0.11842,"peak_contact_force":248.1931,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23224.0,"raw_peak_contact_force":0.4461,"tcp_end":[0.53004,-0.02848,0.14371],"tcp_start":[0.53414,-0.02862,0.04556],"tcp_to_object_dist_end":0.02785,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55543,-0.01408,0.01602],"object_pos_start":[0.54195,-0.02863,0.11853],"object_to_goal_dist_end":0.25283,"object_to_goal_dist_start":0.22166,"object_z_max":0.17062,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15795.0,"raw_peak_contact_force":1.77014,"subtask_id":"transport_arc","tcp_end":[0.54985,0.0147,0.24064],"tcp_start":[0.53004,-0.02848,0.14371],"tcp_to_object_dist_end":0.22653,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55543,-0.01408,0.01602],"object_pos_start":[0.55543,-0.01408,0.01602],"object_to_goal_dist_end":0.25283,"object_to_goal_dist_start":0.25283,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8880.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61141,0.13806,0.17093],"tcp_start":[0.54985,0.0147,0.24064],"tcp_to_object_dist_end":0.22423,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```