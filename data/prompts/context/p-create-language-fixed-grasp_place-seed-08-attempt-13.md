## Search State

- **Seed**: 8
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → contact → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.1549 | 0.19 | ❌ rejected |
| 12 | approach → descend → contact → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3310 | 0.26 | ✅ accepted |
| 11 | approach → descend → contact → lift → approach → descend → release | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | force_threshold_switch | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.2594 | 0.22 | ❌ rejected |
| 10 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4248 | 0.24 | ❌ rejected |
| 9 | approach → descend → contact → lift → approach → descend | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3303 | 0.15 | ❌ rejected |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.155) — your mutation base

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
    - 0.05
    orientation:
      mode: keep_current
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
  subtask_id: transport_arc
- id: descend_to_goal
  type: descend
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
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: release_1
- id: release_grasp
  type: release
  control: position_control
  termination: pose_tolerance
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current

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
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.05]
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **release_grasp** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.155
- **task_score** (E): 0.191
- **fitness_score**: 0.560  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1121 |
| descend_1 | 1.00 | 1.00 | 0.1432 |
| contact_1 | 1.00 | 1.00 | 0.0086 |
| grasp_verify | 1.00 | 1.00 | 0.0118 |
| lift_1 | 0.67 | 1.00 | 0.1429 |
| transport_1 | 0.00 | 1.00 | 0.1568 |
| descend_to_goal | 1.00 | 1.00 | 0.1015 |
| release_1 | 1.00 | 1.00 | 0.0209 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, -0.000, 0.198) | (0.522, -0.001, 0.030)→(0.522, -0.001, 0.026) | 0.287→0.289 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.516, -0.000, 0.198)→(0.517, -0.001, 0.055) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 4.000 | 0.123 | 0.123 |
| contact_1 | contact | 1.00 / force_exceeded | (0.517, -0.001, 0.055)→(0.511, -0.001, 0.048) | (0.522, -0.001, 0.026)→(0.522, -0.001, 0.026) | 0.289→0.289 | 1.00 / 42.000 | 0.142 | 0.186 |
| grasp_verify | grasp | 1.00 / step_budget | (0.511, -0.001, 0.048)→(0.503, -0.001, 0.039) | (0.522, -0.001, 0.026)→(0.518, -0.001, 0.021) | 0.289→0.293 | 1.00 / 47.333 | 0.370 | 0.403 |
| lift_1 | lift | 0.67 / step_budget | (0.503, -0.001, 0.039)→(0.500, -0.001, 0.182) | (0.518, -0.001, 0.021)→(0.511, -0.000, 0.154) | 0.293→0.238 | 1.00 / 22.667 | 0.114 | 0.610 |
| transport_1 | approach | 0.00 / step_budget | (0.500, -0.001, 0.182)→(0.563, 0.122, 0.250) | (0.511, -0.000, 0.154)→(0.533, 0.063, 0.016) | 0.238→0.250 | 1.00 / 8.333 | 3249.727 | 1.761 |
| descend_to_goal | descend | 1.00 / step_budget | (0.563, 0.122, 0.250)→(0.597, 0.190, 0.190) | (0.533, 0.063, 0.016)→(0.533, 0.063, 0.016) | 0.250→0.250 | 1.00 / 8.000 | 3249.645 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.597, 0.190, 0.190)→(0.592, 0.188, 0.210) | (0.533, 0.063, 0.016)→(0.533, 0.063, 0.016) | 0.250→0.250 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.231
- phase_score: 0.428
- phase_breakdown.approach_1_score: 0.059
- phase_breakdown.descend_1_score: 0.869
- phase_breakdown.transport_arc_score: 0.143
- phase_breakdown.release_1_score: 0.734
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.580

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.580
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.231
- **Median Q (composite search score)**: 0.150
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.368


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72611,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13167,"contact_1.contact_force":8.99572,"descend_to_goal.descend_speed":0.05922,"descend_to_goal.release_z_offset":-0.01485,"lift_1.lift_height":0.1976,"transport_1.arc_height":0.0606,"transport_1.transport_speed":0.19385},"optimized_scores":{"best_composite_score":0.13988,"best_fitness_score":0.54488,"best_task_score":0.16204},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3218.0,"contact_point_centroid":[0.48391,0.09127,-0.00234],"force_p95":0.1261,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79589,"mean_force":0.13711,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.50061,0.10825,0.27958]},{"body_a":"world","body_b":"grasp_target","contact_count":210.0,"contact_point_centroid":[0.47394,0.04614,-0.00246],"force_p95":0.43084,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57184,"mean_force":0.1086,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46353,0.04633,0.04529]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48293,0.04753,-0.00414],"force_p95":0.3764,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37925,"mean_force":0.261,"phase_index":3.0,"phase_name":"grasp_verify","phase_type":"grasp","tcp_position_centroid":[0.46673,0.04665,0.04221]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15499.0,"contact_point_centroid":[0.46322,0.02721,0.11035],"force_p95":0.12891,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31109,"mean_force":0.06694,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46176,0.04617,0.11026]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16827.0,"contact_point_centroid":[0.46402,0.06499,0.11121],"force_p95":0.1034,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30447,"mean_force":0.06144,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4618,0.04617,0.11046]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1024.0,"contact_point_centroid":[0.46895,0.06696,0.20936],"force_p95":0.17595,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30254,"mean_force":0.09338,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.46244,0.04902,0.21101]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":779.0,"contact_point_centroid":[0.46853,0.03046,0.20736],"force_p95":0.17836,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2399,"mean_force":0.10903,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.46233,0.04876,0.21035]},{"body_a":"world","body_b":"grasp_target","contact_count":1632.0,"contact_point_centroid":[0.48273,0.04861,-0.00213],"force_p95":0.15678,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21247,"mean_force":0.13247,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47355,0.04731,0.04924]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4092.0,"contact_point_centroid":[0.47221,0.02805,0.04945],"force_p95":0.0796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14648,"mean_force":0.05208,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47299,0.04726,0.04864]},{"body_a":"world","body_b":"grasp_target","contact_count":1680.0,"contact_point_centroid":[0.4827,0.04873,-0.00192],"force_p95":0.13414,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4898,0.02118,0.23514]},{"body_a":"world","body_b":"grasp_target","contact_count":1460.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47839,0.04558,0.11211]},{"body_a":"world","body_b":"grasp_target","contact_count":1788.0,"contact_point_centroid":[0.48392,0.09126,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.5565,0.19435,0.25485]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.48392,0.09126,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57128,0.22041,0.21627]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9573.0,"contact_point_centroid":[0.46708,0.06565,0.04374],"force_p95":0.07597,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12017,"mean_force":0.0491,"phase_index":3.0,"phase_name":"grasp_verify","phase_type":"grasp","tcp_position_centroid":[0.46667,0.04664,0.04215]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7702.0,"contact_point_centroid":[0.46604,0.02748,0.0435],"force_p95":0.08298,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11296,"mean_force":0.05687,"phase_index":3.0,"phase_name":"grasp_verify","phase_type":"grasp","tcp_position_centroid":[0.46672,0.04665,0.04221]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4988.0,"contact_point_centroid":[0.47307,0.06637,0.04953],"force_p95":0.07303,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07418,"mean_force":0.04409,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47299,0.04726,0.04864]}],"total_contact_groups":19},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.48392,0.09126,0.01602],"final_tcp_position":[0.5748,0.22179,0.21547],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":9748.93537,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":421.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1680.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48094,0.04367,0.17003],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14411,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":365.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1460.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47827,0.04774,0.05492],"tcp_start":[0.48094,0.04367,0.17003],"tcp_to_object_dist_end":0.02925,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":8.0,"n_steps_budget":600.0,"object_pos_end":[0.48266,0.04765,0.02556],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29098,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15343,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10712.0,"raw_peak_contact_force":0.21247,"subtask_id":"grasp_1","tcp_end":[0.47296,0.04725,0.04861],"tcp_start":[0.47827,0.04774,0.05492],"tcp_to_object_dist_end":0.02501,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47892,0.0466,0.0218],"object_pos_start":[0.48266,0.04765,0.02556],"object_to_goal_dist_end":0.29558,"object_to_goal_dist_start":0.29098,"object_z_max":0.02556,"peak_contact_force":0.34831,"phase_name":"grasp_verify","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":19075.0,"raw_peak_contact_force":0.37925,"tcp_end":[0.46559,0.04654,0.04105],"tcp_start":[0.47296,0.04725,0.04861],"tcp_to_object_dist_end":0.02342,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47067,0.04769,0.17183],"object_pos_start":[0.47892,0.0466,0.0218],"object_to_goal_dist_end":0.22052,"object_to_goal_dist_start":0.29558,"object_z_max":0.17164,"peak_contact_force":0.13069,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32536.0,"raw_peak_contact_force":0.57184,"tcp_end":[0.46211,0.0462,0.20357],"tcp_start":[0.46559,0.04654,0.04105],"tcp_to_object_dist_end":0.03291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48392,0.09126,0.01602],"object_pos_start":[0.47067,0.04769,0.17183],"object_to_goal_dist_end":0.27298,"object_to_goal_dist_start":0.22052,"object_z_max":0.18545,"peak_contact_force":9748.93537,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8260.0,"raw_peak_contact_force":1.79589,"subtask_id":"transport_arc","tcp_end":[0.53982,0.16727,0.29972],"tcp_start":[0.46211,0.0462,0.20357],"tcp_to_object_dist_end":0.29897,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":447.0,"n_steps_budget":1000.0,"object_pos_end":[0.48392,0.09126,0.01602],"object_pos_start":[0.48392,0.09126,0.01602],"object_to_goal_dist_end":0.27298,"object_to_goal_dist_start":0.27298,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3711.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5748,0.22179,0.21547],"tcp_start":[0.53982,0.16727,0.29972],"tcp_to_object_dist_end":0.2551,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48392,0.09126,0.01602],"object_pos_start":[0.48392,0.09126,0.01602],"object_to_goal_dist_end":0.27298,"object_to_goal_dist_start":0.27298,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57005,0.2198,0.23602],"tcp_start":[0.5748,0.22179,0.21547],"tcp_to_object_dist_end":0.26897,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68153,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.21919,"contact_1.contact_force":7.98705,"descend_to_goal.descend_speed":0.04737,"descend_to_goal.release_z_offset":-0.00947,"lift_1.lift_height":0.11838,"transport_1.arc_height":0.02131,"transport_1.transport_speed":0.17961},"optimized_scores":{"best_composite_score":0.15008,"best_fitness_score":0.55508,"best_task_score":0.17913},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1307.0,"contact_point_centroid":[0.55676,0.06329,-0.00276],"force_p95":0.37175,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.70998,"mean_force":0.15899,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.54997,0.08072,0.20613]},{"body_a":"world","body_b":"grasp_target","contact_count":240.0,"contact_point_centroid":[0.52795,-0.0206,-0.00272],"force_p95":0.29155,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62839,"mean_force":0.12577,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51555,-0.02068,0.04225]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53718,-0.02089,-0.0045],"force_p95":0.40389,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40727,"mean_force":0.28555,"phase_index":3.0,"phase_name":"grasp_verify","phase_type":"grasp","tcp_position_centroid":[0.51924,-0.02075,0.03909]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13119.0,"contact_point_centroid":[0.51505,-0.03969,0.08687],"force_p95":0.09299,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2967,"mean_force":0.05418,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51377,-0.02064,0.08486]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12123.0,"contact_point_centroid":[0.51502,-0.00152,0.0877],"force_p95":0.09966,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28492,"mean_force":0.05778,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51375,-0.02064,0.08541]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6976.0,"contact_point_centroid":[0.53043,0.03461,0.16671],"force_p95":0.10958,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26797,"mean_force":0.07934,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52465,0.01603,0.16695]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6899.0,"contact_point_centroid":[0.52966,-0.00449,0.16556],"force_p95":0.12236,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23717,"mean_force":0.08007,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52393,0.01411,0.16564]},{"body_a":"world","body_b":"grasp_target","contact_count":1632.0,"contact_point_centroid":[0.53703,-0.02126,-0.00205],"force_p95":0.13586,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.166,"mean_force":0.12668,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52669,-0.0209,0.0477]},{"body_a":"world","body_b":"grasp_target","contact_count":932.0,"contact_point_centroid":[0.53702,-0.02132,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12315,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51303,-0.00872,0.27497]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4312.0,"contact_point_centroid":[0.52661,-0.00168,0.04809],"force_p95":0.07496,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13024,"mean_force":0.04996,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52607,-0.02089,0.04697]},{"body_a":"world","body_b":"grasp_target","contact_count":2364.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52875,-0.01935,0.15196]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.55683,0.0633,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.5755,0.15053,0.20155]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55683,0.0633,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5872,0.18701,0.19608]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10382.0,"contact_point_centroid":[0.51887,-0.0399,0.04075],"force_p95":0.0715,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11825,"mean_force":0.04694,"phase_index":3.0,"phase_name":"grasp_verify","phase_type":"grasp","tcp_position_centroid":[0.5192,-0.02075,0.03904]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9262.0,"contact_point_centroid":[0.51872,-0.00152,0.04094],"force_p95":0.07551,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11567,"mean_force":0.05118,"phase_index":3.0,"phase_name":"grasp_verify","phase_type":"grasp","tcp_position_centroid":[0.5192,-0.02075,0.03905]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4888.0,"contact_point_centroid":[0.52623,-0.03999,0.04838],"force_p95":0.06844,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08785,"mean_force":0.04447,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52608,-0.02089,0.04697]}],"total_contact_groups":19},"final_pose_error":0.04411,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.55683,0.0633,0.01602],"final_tcp_position":[0.59097,0.18821,0.19518],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":9748.68841,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":234.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":932.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52803,-0.01779,0.25145],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22564,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":591.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2364.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.5318,-0.02098,0.05453],"tcp_start":[0.52803,-0.01779,0.25145],"tcp_to_object_dist_end":0.02899,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":8.0,"n_steps_budget":600.0,"object_pos_end":[0.53695,-0.021,0.02582],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3166,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13502,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10832.0,"raw_peak_contact_force":0.166,"subtask_id":"grasp_1","tcp_end":[0.52605,-0.02088,0.04693],"tcp_start":[0.5318,-0.02098,0.05453],"tcp_to_object_dist_end":0.02376,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":49.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53285,-0.02067,0.02108],"object_pos_start":[0.53695,-0.021,0.02582],"object_to_goal_dist_end":0.32005,"object_to_goal_dist_start":0.3166,"object_z_max":0.02582,"peak_contact_force":0.37466,"phase_name":"grasp_verify","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":21444.0,"raw_peak_contact_force":0.40727,"tcp_end":[0.51798,-0.02073,0.03765],"tcp_start":[0.52605,-0.02088,0.04693],"tcp_to_object_dist_end":0.02227,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.52753,-0.02064,0.11917],"object_pos_start":[0.53285,-0.02067,0.02108],"object_to_goal_dist_end":0.27629,"object_to_goal_dist_start":0.32005,"object_z_max":0.11906,"peak_contact_force":0.10453,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25482.0,"raw_peak_contact_force":0.62839,"tcp_end":[0.51394,-0.02063,0.14362],"tcp_start":[0.51798,-0.02073,0.03765],"tcp_to_object_dist_end":0.02797,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55683,0.0633,0.01602],"object_pos_start":[0.52753,-0.02064,0.11917],"object_to_goal_dist_end":0.25795,"object_to_goal_dist_start":0.27629,"object_z_max":0.15801,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16328.0,"raw_peak_contact_force":1.70998,"subtask_id":"transport_arc","tcp_end":[0.55822,0.10151,0.21598],"tcp_start":[0.51394,-0.02063,0.14362],"tcp_to_object_dist_end":0.20359,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55683,0.0633,0.01602],"object_pos_start":[0.55683,0.0633,0.01602],"object_to_goal_dist_end":0.25795,"object_to_goal_dist_start":0.25795,"object_z_max":0.01602,"peak_contact_force":9748.68841,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8250.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59097,0.18821,0.19518],"tcp_start":[0.55822,0.10151,0.21598],"tcp_to_object_dist_end":0.22106,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55683,0.0633,0.01602],"object_pos_start":[0.55683,0.0633,0.01602],"object_to_goal_dist_end":0.25795,"object_to_goal_dist_start":0.25795,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.58579,0.18646,0.21573],"tcp_start":[0.59097,0.18821,0.19518],"tcp_to_object_dist_end":0.23642,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.84106,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13597,"contact_1.contact_force":15.61905,"descend_to_goal.descend_speed":0.06171,"descend_to_goal.release_z_offset":-0.0153,"lift_1.lift_height":0.22069,"transport_1.arc_height":0.02878,"transport_1.transport_speed":0.17584},"optimized_scores":{"best_composite_score":0.17486,"best_fitness_score":0.57986,"best_task_score":0.23058},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2777.0,"contact_point_centroid":[0.55703,0.03528,-0.00237],"force_p95":0.13137,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.77768,"mean_force":0.14058,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.56655,0.05352,0.23016]},{"body_a":"world","body_b":"grasp_target","contact_count":251.0,"contact_point_centroid":[0.53693,-0.02827,-0.00277],"force_p95":0.28801,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62997,"mean_force":0.13078,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52425,-0.02827,0.04302]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54603,-0.02872,-0.00462],"force_p95":0.41813,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42182,"mean_force":0.29234,"phase_index":3.0,"phase_name":"grasp_verify","phase_type":"grasp","tcp_position_centroid":[0.52804,-0.02839,0.03982]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17570.0,"contact_point_centroid":[0.52468,-0.04716,0.1071],"force_p95":0.09734,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29522,"mean_force":0.05956,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52259,-0.02821,0.10578]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16070.0,"contact_point_centroid":[0.52469,-0.0092,0.10902],"force_p95":0.10242,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28677,"mean_force":0.06394,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5226,-0.02821,0.10753]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2260.0,"contact_point_centroid":[0.53467,0.00386,0.20291],"force_p95":0.16129,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27522,"mean_force":0.09212,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.5283,-0.01448,0.20409]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2228.0,"contact_point_centroid":[0.53396,-0.03412,0.20231],"force_p95":0.15099,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25513,"mean_force":0.08511,"phase_index":5.0,"phase_name":"transport_1","phase_type":"approach","tcp_position_centroid":[0.52773,-0.01566,0.20348]},{"body_a":"world","body_b":"grasp_target","contact_count":1604.0,"contact_point_centroid":[0.54561,-0.02916,-0.00207],"force_p95":0.14013,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17956,"mean_force":0.12795,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53547,-0.02863,0.0486]},{"body_a":"world","body_b":"grasp_target","contact_count":1840.0,"contact_point_centroid":[0.5456,-0.02923,-0.00192],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51772,-0.01305,0.23507]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4109.0,"contact_point_centroid":[0.53591,-0.0094,0.04902],"force_p95":0.07777,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13507,"mean_force":0.05213,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53495,-0.02861,0.04797]},{"body_a":"world","body_b":"grasp_target","contact_count":1424.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53771,-0.02761,0.11239]},{"body_a":"world","body_b":"grasp_target","contact_count":1964.0,"contact_point_centroid":[0.55705,0.03532,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.60844,0.12947,0.19243]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55705,0.03532,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62123,0.15767,0.15836]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10331.0,"contact_point_centroid":[0.52773,-0.04752,0.04117],"force_p95":0.073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11886,"mean_force":0.04718,"phase_index":3.0,"phase_name":"grasp_verify","phase_type":"grasp","tcp_position_centroid":[0.52794,-0.02839,0.0397]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9009.0,"contact_point_centroid":[0.52755,-0.00917,0.04126],"force_p95":0.07606,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11714,"mean_force":0.05239,"phase_index":3.0,"phase_name":"grasp_verify","phase_type":"grasp","tcp_position_centroid":[0.52797,-0.02839,0.03973]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4901.0,"contact_point_centroid":[0.53507,-0.04768,0.04907],"force_p95":0.06906,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08621,"mean_force":0.04439,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53495,-0.02861,0.04797]}],"total_contact_groups":19},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.55705,0.03532,0.01602],"final_tcp_position":[0.6257,0.15876,0.15834],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.77768,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":461.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1840.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53796,-0.02656,0.17153],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14574,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":356.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1424.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.54004,-0.02877,0.05426],"tcp_start":[0.53796,-0.02656,0.17153],"tcp_to_object_dist_end":0.02879,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.54554,-0.02874,0.02577],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26072,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.13846,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10614.0,"raw_peak_contact_force":0.17956,"subtask_id":"grasp_1","tcp_end":[0.53493,-0.02861,0.04794],"tcp_start":[0.54004,-0.02877,0.05426],"tcp_to_object_dist_end":0.02458,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54159,-0.02837,0.02085],"object_pos_start":[0.54554,-0.02874,0.02577],"object_to_goal_dist_end":0.26467,"object_to_goal_dist_start":0.26072,"object_z_max":0.02577,"peak_contact_force":0.38586,"phase_name":"grasp_verify","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":21140.0,"raw_peak_contact_force":0.42182,"tcp_end":[0.52677,-0.02835,0.03833],"tcp_start":[0.53493,-0.02861,0.04794],"tcp_to_object_dist_end":0.02292,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53345,-0.02837,0.16975],"object_pos_start":[0.54159,-0.02837,0.02085],"object_to_goal_dist_end":0.21748,"object_to_goal_dist_start":0.26467,"object_z_max":0.16957,"peak_contact_force":0.10574,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33891.0,"raw_peak_contact_force":0.62997,"tcp_end":[0.52307,-0.02822,0.1985],"tcp_start":[0.52677,-0.02835,0.03833],"tcp_to_object_dist_end":0.03057,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55705,0.03532,0.01602],"object_pos_start":[0.53345,-0.02837,0.16975],"object_to_goal_dist_end":0.22007,"object_to_goal_dist_start":0.21748,"object_z_max":0.17901,"peak_contact_force":0.12263,"phase_name":"transport_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10060.0,"raw_peak_contact_force":1.77768,"subtask_id":"transport_arc","tcp_end":[0.59217,0.09826,0.23516],"tcp_start":[0.52307,-0.02822,0.1985],"tcp_to_object_dist_end":0.23069,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":491.0,"n_steps_budget":1000.0,"object_pos_end":[0.55705,0.03532,0.01602],"object_pos_start":[0.55705,0.03532,0.01602],"object_to_goal_dist_end":0.22007,"object_to_goal_dist_start":0.22007,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4046.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6257,0.15876,0.15834],"tcp_start":[0.59217,0.09826,0.23516],"tcp_to_object_dist_end":0.20051,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55705,0.03532,0.01602],"object_pos_start":[0.55705,0.03532,0.01602],"object_to_goal_dist_end":0.22007,"object_to_goal_dist_start":0.22007,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61954,0.15714,0.17772],"tcp_start":[0.6257,0.15876,0.15834],"tcp_to_object_dist_end":0.21188,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```