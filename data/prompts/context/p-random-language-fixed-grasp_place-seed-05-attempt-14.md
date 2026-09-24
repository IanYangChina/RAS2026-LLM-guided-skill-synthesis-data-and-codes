## Search State

- **Seed**: 5
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.2650 | 0.40 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3148 | 0.41 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.3060 | 0.41 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.2228 | 0.42 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | 0.2227 | 0.41 | ❌ rejected |

**Proposal policy**: task_score is 0.40 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`
- Frozen object start: [0.530500292374538, 0.030794078973649372, 0.03]
- Frozen task target: [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]
- Goal object position: (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6015325561042142, 0.17858013800881417, 0.10808960535724847)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.530500292374538, 0.030794078973649372, 0.03)
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
  frozen_object_start: [0.5305, 0.0308, 0.03]
  frozen_task_target: [0.6015, 0.1786, 0.1081]
  frozen_object_starts: {'grasp_target': [0.530500292374538, 0.030794078973649372, 0.03]}
  frozen_targets: {'place_target': [0.6015325561042142, 0.17858013800881417, 0.10808960535724847]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d

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

## Current Skill (Q=0.265) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
phases:
- id: approach
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
    - 0.0
    tolerance: 0.02
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_1
- id: descend
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    descend_force_threshold:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: descend_1
- id: grasp
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
  guards:
  - id: grasp_check
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: grasp_1
- id: lift
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
    tolerance: 0.02
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
- id: transport
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
    - 0.05
    tolerance: 0.02
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: release
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
  subtask_id: release_1
- id: retract
  type: retract
  generator: linear_cartesian
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
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.02
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.265
- **task_score** (E): 0.403
- **fitness_score**: 0.670  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.125
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2541 |
| descend | 1.00 | 1.00 | 0.0010 |
| grasp | 0.00 | 1.00 | 0.0000 |
| lift | 1.00 | 1.00 | 0.1172 |
| transport | 1.00 | 1.00 | 0.1897 |
| place_descend | 1.00 | 1.00 | 0.0330 |
| release | 1.00 | 1.00 | 0.0204 |
| retract | 1.00 | 1.00 | 0.0463 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.016, 0.049) | (0.516, 0.018, 0.030)→(0.516, 0.018, 0.026) | 0.234→0.236 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend | descend | 1.00 / force_exceeded | (0.510, 0.016, 0.049)→(0.510, 0.017, 0.048) | (0.516, 0.018, 0.026)→(0.516, 0.018, 0.026) | 0.236→0.236 | 1.00 / 4.000 | 234.014 | 0.123 |
| grasp | grasp | 0.00 / guard_failure | (0.505, 0.016, 0.042)→(0.505, 0.016, 0.042) | (0.516, 0.018, 0.026)→(0.516, 0.017, 0.025) | 0.236→0.237 | 1.00 / 42.667 | 0.175 | 0.253 |
| lift | lift | 1.00 / step_budget | (0.505, 0.016, 0.042)→(0.501, 0.016, 0.159) | (0.516, 0.017, 0.025)→(0.516, 0.017, 0.139) | 0.237→0.196 | 1.00 / 24.000 | 0.109 | 0.491 |
| transport | approach | 1.00 / step_budget | (0.501, 0.016, 0.159)→(0.594, 0.165, 0.216) | (0.516, 0.017, 0.139)→(0.591, 0.151, 0.104) | 0.196→0.099 | 1.00 / 16.667 | 91004.952 | 1.077 |
| place_descend | descend | 1.00 / step_budget | (0.594, 0.165, 0.216)→(0.598, 0.172, 0.184) | (0.591, 0.151, 0.104)→(0.596, 0.156, 0.079) | 0.099→0.092 | 1.00 / 15.000 | 3249.760 | 0.325 |
| release | release | 1.00 / step_budget | (0.598, 0.172, 0.184)→(0.592, 0.170, 0.203) | (0.596, 0.156, 0.079)→(0.584, 0.157, 0.023) | 0.092→0.149 | 1.00 / 3.333 | 0.197 | 0.892 |
| retract | retract | 1.00 / step_budget | (0.592, 0.170, 0.203)→(0.600, 0.177, 0.248) | (0.584, 0.157, 0.023)→(0.580, 0.160, 0.023) | 0.149→0.150 | 1.00 / 4.000 | 0.123 | 0.200 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.564
- phase_score: 0.548
- phase_breakdown.approach_1_score: 0.672
- phase_breakdown.descend_1_score: 0.838
- phase_breakdown.transport_arc_score: 0.326
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.674
- grasp_place_fitness: 0.750

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.750
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.564
- **Median Q (composite search score)**: 0.285
- **K-run variance**: 0.0056
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.316


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `181fdad61feb8a6d3dd6561c82dc2730a5598964bf30fa08b43615687239c379`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `eed1fc17ff57094d5189888f0dc8540ea7c165c4c73333e7487a550c7ded377e`; realized-scene SHA-256: `ca83b0c5488ee900ee32f323a4fc38ffcc2f5381fd3d2b180044b561c962382d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93985,"average_solve_count":133.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.14207,"descend.descend_force_threshold":5.92763,"lift.lift_height":0.13522,"place_descend.place_speed":0.15906,"retract.retract_speed":0.20858,"transport.arc_height":0.0309,"transport.transport_speed":0.21257},"optimized_scores":{"best_composite_score":0.34538,"best_fitness_score":0.75038,"best_task_score":0.56381},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":299.0,"contact_point_centroid":[0.57738,0.17449,-0.00378],"force_p95":0.7778,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.10774,"mean_force":0.22568,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.5865,0.16901,0.13299]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":645.0,"contact_point_centroid":[0.59492,0.18898,0.11661],"force_p95":0.18038,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.54052,"mean_force":0.10122,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59062,0.1704,0.1191]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":675.0,"contact_point_centroid":[0.59522,0.15216,0.11737],"force_p95":0.16692,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.50465,"mean_force":0.08622,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59072,0.17044,0.11923]},{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.52825,0.02676,-0.00156],"force_p95":0.46917,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48484,"mean_force":0.0993,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51637,0.02746,0.04241]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":781.0,"contact_point_centroid":[0.59576,0.18527,0.14189],"force_p95":0.1678,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42032,"mean_force":0.10362,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.59118,0.16671,0.14347]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":768.0,"contact_point_centroid":[0.59558,0.14829,0.14255],"force_p95":0.15822,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41679,"mean_force":0.10102,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.59112,0.16659,0.14405]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5006.0,"contact_point_centroid":[0.55609,0.07611,0.17402],"force_p95":0.12142,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37169,"mean_force":0.0802,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55089,0.09487,0.17289]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5413.0,"contact_point_centroid":[0.51661,0.0083,0.09567],"force_p95":0.11208,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35978,"mean_force":0.07363,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51395,0.02731,0.09306]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5343.0,"contact_point_centroid":[0.55494,0.11164,0.17419],"force_p95":0.10762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35138,"mean_force":0.07576,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54979,0.09301,0.17304]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6441.0,"contact_point_centroid":[0.51611,0.04613,0.0926],"force_p95":0.10625,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32178,"mean_force":0.0651,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51398,0.02732,0.09079]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53065,0.03029,-0.0023],"force_p95":0.19571,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26127,"mean_force":0.14418,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51818,0.02759,0.04131]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4352.0,"contact_point_centroid":[0.51912,0.00833,0.04401],"force_p95":0.09236,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16734,"mean_force":0.05811,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51775,0.02756,0.0408]},{"body_a":"world","body_b":"grasp_target","contact_count":792.0,"contact_point_centroid":[0.57628,0.17481,-0.00196],"force_p95":0.1453,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16057,"mean_force":0.12259,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.59019,0.17228,0.16631]},{"body_a":"world","body_b":"grasp_target","contact_count":1876.0,"contact_point_centroid":[0.5305,0.03079,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51087,0.01363,0.1747]},{"body_a":"world","body_b":"grasp_target","contact_count":16.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.52344,0.02782,0.04775]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6214.0,"contact_point_centroid":[0.51807,0.04673,0.04321],"force_p95":0.07893,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08609,"mean_force":0.04424,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51775,0.02756,0.04081]}],"total_contact_groups":16},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.57626,0.17482,0.02602],"final_tcp_position":[0.59548,0.17584,0.18944],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":470.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1876.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52372,0.02778,0.04844],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02362,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16.0,"raw_peak_contact_force":0.12262,"subtask_id":"descend_1","tcp_end":[0.52286,0.02786,0.04673],"tcp_start":[0.52372,0.02778,0.04844],"tcp_to_object_dist_end":0.02227,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53053,0.02823,0.02514],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18581,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.17893,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12370.0,"raw_peak_contact_force":0.26127,"subtask_id":"grasp_1","tcp_end":[0.51773,0.02756,0.04078],"tcp_start":[0.51773,0.02756,0.04078],"tcp_to_object_dist_end":0.02022,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":380.0,"n_steps_budget":870.0,"object_pos_end":[0.52977,0.02759,0.13649],"object_pos_start":[0.53054,0.02817,0.0252],"object_to_goal_dist_end":0.16958,"object_to_goal_dist_start":0.18583,"object_z_max":0.13623,"peak_contact_force":0.10999,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11939.0,"raw_peak_contact_force":0.48484,"tcp_end":[0.51396,0.02732,0.1565],"tcp_start":[0.51773,0.02756,0.04078],"tcp_to_object_dist_end":0.0255,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":403.0,"n_steps_budget":1000.0,"object_pos_end":[0.59489,0.16282,0.13049],"object_pos_start":[0.52977,0.02759,0.13649],"object_to_goal_dist_end":0.02818,"object_to_goal_dist_start":0.16958,"object_z_max":0.15461,"peak_contact_force":0.12076,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10349.0,"raw_peak_contact_force":0.37169,"subtask_id":"transport_arc","tcp_end":[0.58988,0.16267,0.16063],"tcp_start":[0.51396,0.02732,0.1565],"tcp_to_object_dist_end":0.03055,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":75.0,"n_steps_budget":1000.0,"object_pos_end":[0.60048,0.17152,0.09324],"object_pos_start":[0.59489,0.16282,0.13049],"object_to_goal_dist_end":0.01648,"object_to_goal_dist_start":0.02818,"object_z_max":0.13049,"peak_contact_force":0.13518,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1549.0,"raw_peak_contact_force":0.42032,"subtask_id":"release_1","tcp_end":[0.59353,0.17101,0.12441],"tcp_start":[0.58988,0.16267,0.16063],"tcp_to_object_dist_end":0.03194,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57687,0.17455,0.0265],"object_pos_start":[0.60048,0.17152,0.09324],"object_to_goal_dist_end":0.08533,"object_to_goal_dist_start":0.01648,"object_z_max":0.09324,"peak_contact_force":0.15018,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1619.0,"raw_peak_contact_force":1.10774,"tcp_end":[0.58639,0.16898,0.14412],"tcp_start":[0.59353,0.17101,0.12441],"tcp_to_object_dist_end":0.11814,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":198.0,"n_steps_budget":600.0,"object_pos_end":[0.57626,0.17482,0.02602],"object_pos_start":[0.57687,0.17455,0.0265],"object_to_goal_dist_end":0.08596,"object_to_goal_dist_start":0.08533,"object_z_max":0.02651,"peak_contact_force":0.12296,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":792.0,"raw_peak_contact_force":0.16057,"tcp_end":[0.59548,0.17584,0.18944],"tcp_start":[0.58639,0.16898,0.14412],"tcp_to_object_dist_end":0.16455,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5dcdc1a4e2a8d4c3bb30f9ac92fb306bea0b16a8f449f4d02b0333754e50f910`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0082,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.18961,"descend.descend_force_threshold":7.92514,"lift.lift_height":0.14524,"place_descend.place_speed":0.0536,"retract.retract_speed":0.25142,"transport.arc_height":0.02144,"transport.transport_speed":0.28543},"optimized_scores":{"best_composite_score":0.16488,"best_fitness_score":0.56988,"best_task_score":0.20142},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":723.0,"contact_point_centroid":[0.56411,0.12939,-0.00376],"force_p95":0.7926,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.42486,"mean_force":0.19366,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56331,0.14172,0.27666]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.50143,-0.01419,-0.00142],"force_p95":0.44279,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47338,"mean_force":0.10145,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49308,-0.01419,0.04442]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4097.0,"contact_point_centroid":[0.5163,0.05,0.21117],"force_p95":0.11467,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33825,"mean_force":0.07886,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51035,0.03152,0.20988]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7788.0,"contact_point_centroid":[0.49156,-0.0332,0.10417],"force_p95":0.09044,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30299,"mean_force":0.05594,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49072,-0.01414,0.10245]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7253.0,"contact_point_centroid":[0.49148,0.00499,0.10387],"force_p95":0.09617,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29681,"mean_force":0.05879,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49074,-0.01414,0.10161]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3484.0,"contact_point_centroid":[0.51435,0.00885,0.2082],"force_p95":0.13608,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27807,"mean_force":0.08785,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.5085,0.02753,0.20659]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.50386,-0.01551,-0.00214],"force_p95":0.15593,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21664,"mean_force":0.13298,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49472,-0.01421,0.04331]},{"body_a":"world","body_b":"grasp_target","contact_count":1748.0,"contact_point_centroid":[0.50382,-0.01567,-0.00192],"force_p95":0.13393,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49902,-0.00696,0.17514]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5806.0,"contact_point_centroid":[0.49452,0.00498,0.04483],"force_p95":0.07232,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13065,"mean_force":0.04497,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49437,-0.0142,0.04293]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49948,-0.01421,0.04898]},{"body_a":"world","body_b":"grasp_target","contact_count":200.0,"contact_point_centroid":[0.56404,0.12932,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.1226,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57949,0.17624,0.2777]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56404,0.12932,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57784,0.17853,0.26503]},{"body_a":"world","body_b":"grasp_target","contact_count":736.0,"contact_point_centroid":[0.56404,0.12932,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.57968,0.18152,0.30627]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5996.0,"contact_point_centroid":[0.49454,-0.03343,0.04483],"force_p95":0.07284,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07481,"mean_force":0.04482,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.49437,-0.0142,0.04294]},{"body_a":"left_finger","body_b":"right_finger","contact_count":607.0,"contact_point_centroid":[0.56702,0.14838,0.28147],"force_p95":0.01325,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01654,"mean_force":0.01089,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56653,0.14837,0.27923]},{"body_a":"left_finger","body_b":"right_finger","contact_count":218.0,"contact_point_centroid":[0.57998,0.1793,0.26268],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.01018,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.57956,0.17928,0.26062]}],"total_contact_groups":17},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.56404,0.12932,0.01602],"final_tcp_position":[0.58327,0.18501,0.32881],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":273014.59515,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":438.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1748.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49948,-0.01421,0.04898],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02341,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":286.80785,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49933,-0.01424,0.0485],"tcp_start":[0.49948,-0.01421,0.04898],"tcp_to_object_dist_end":0.02297,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50378,-0.01464,0.02557],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31189,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.15028,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13606.0,"raw_peak_contact_force":0.21664,"subtask_id":"grasp_1","tcp_end":[0.49435,-0.0142,0.04291],"tcp_start":[0.49435,-0.0142,0.04291],"tcp_to_object_dist_end":0.01974,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":398.0,"n_steps_budget":930.0,"object_pos_end":[0.50588,-0.01416,0.14835],"object_pos_start":[0.50379,-0.01461,0.0256],"object_to_goal_dist_end":0.23909,"object_to_goal_dist_start":0.31186,"object_z_max":0.14808,"peak_contact_force":0.10692,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15121.0,"raw_peak_contact_force":0.47338,"tcp_end":[0.49081,-0.01413,0.16864],"tcp_start":[0.49435,-0.0142,0.04291],"tcp_to_object_dist_end":0.02528,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":604.0,"n_steps_budget":1000.0,"object_pos_end":[0.56404,0.12932,0.01602],"object_pos_start":[0.50588,-0.01416,0.14835],"object_to_goal_dist_end":0.24036,"object_to_goal_dist_start":0.23909,"object_z_max":0.2158,"peak_contact_force":273014.59515,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8911.0,"raw_peak_contact_force":2.42486,"subtask_id":"transport_arc","tcp_end":[0.57845,0.17339,0.28687],"tcp_start":[0.49081,-0.01413,0.16864],"tcp_to_object_dist_end":0.27479,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":1000.0,"object_pos_end":[0.56404,0.12932,0.01602],"object_pos_start":[0.56404,0.12932,0.01602],"object_to_goal_dist_end":0.24036,"object_to_goal_dist_start":0.24036,"object_z_max":0.01602,"peak_contact_force":9749.01812,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":418.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.58104,0.17949,0.26502],"tcp_start":[0.57845,0.17339,0.28687],"tcp_to_object_dist_end":0.25457,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56404,0.12932,0.01602],"object_pos_start":[0.56404,0.12932,0.01602],"object_to_goal_dist_end":0.24036,"object_to_goal_dist_start":0.24036,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57687,0.1781,0.28493],"tcp_start":[0.58104,0.17949,0.26502],"tcp_to_object_dist_end":0.2736,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":184.0,"n_steps_budget":600.0,"object_pos_end":[0.56404,0.12932,0.01602],"object_pos_start":[0.56404,0.12932,0.01602],"object_to_goal_dist_end":0.24036,"object_to_goal_dist_start":0.24036,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":736.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.58327,0.18501,0.32881],"tcp_start":[0.57687,0.1781,0.28493],"tcp_to_object_dist_end":0.3183,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `53da4dc33bcb1151bde99c46f4ec5d44dda63d23acc62ec623c12d4d0fb32574`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50658,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.2159,"descend.descend_force_threshold":6.49478,"lift.lift_height":0.12933,"place_descend.place_speed":0.02082,"retract.retract_speed":0.22079,"transport.arc_height":0.05668,"transport.transport_speed":0.21483},"optimized_scores":{"best_composite_score":0.2847,"best_fitness_score":0.6897,"best_task_score":0.44248},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":201.0,"contact_point_centroid":[0.60679,0.16976,-0.00616],"force_p95":1.08622,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.44647,"mean_force":0.34148,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.6121,0.16419,0.16961]},{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.50983,0.03515,-0.00166],"force_p95":0.47287,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51494,"mean_force":0.1027,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.50082,0.03547,0.04402]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":616.0,"contact_point_centroid":[0.61928,0.18414,0.15161],"force_p95":0.15609,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.49998,"mean_force":0.09283,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61591,0.16545,0.15574]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":591.0,"contact_point_centroid":[0.62042,0.14731,0.15235],"force_p95":0.12593,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4622,"mean_force":0.08668,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.61604,0.16549,0.15597]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6252.0,"contact_point_centroid":[0.54934,0.06701,0.20281],"force_p95":0.13099,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43523,"mean_force":0.08304,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54387,0.08563,0.20234]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":737.0,"contact_point_centroid":[0.61805,0.18047,0.17891],"force_p95":0.13884,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43245,"mean_force":0.11056,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61478,0.16209,0.18261]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":820.0,"contact_point_centroid":[0.61881,0.14389,0.17974],"force_p95":0.12193,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.419,"mean_force":0.09926,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61469,0.162,0.18325]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6075.0,"contact_point_centroid":[0.55175,0.10682,0.20451],"force_p95":0.1202,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4026,"mean_force":0.08329,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.54629,0.08821,0.20387]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6424.0,"contact_point_centroid":[0.49938,0.05447,0.09633],"force_p95":0.09871,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3223,"mean_force":0.06099,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.49855,0.0353,0.0941]},{"body_a":"world","body_b":"grasp_target","contact_count":779.0,"contact_point_centroid":[0.60068,0.17404,-0.00206],"force_p95":0.20946,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3163,"mean_force":0.1304,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.61663,0.16724,0.20376]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6848.0,"contact_point_centroid":[0.49898,0.01629,0.09808],"force_p95":0.08876,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28953,"mean_force":0.05603,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4985,0.0353,0.09597]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.51268,0.03921,-0.00237],"force_p95":0.25074,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28009,"mean_force":0.16092,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50257,0.03564,0.04266]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5266.0,"contact_point_centroid":[0.50149,0.01636,0.04454],"force_p95":0.08743,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19934,"mean_force":0.05097,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5022,0.03559,0.04226]},{"body_a":"world","body_b":"grasp_target","contact_count":1748.0,"contact_point_centroid":[0.51251,0.03972,-0.00192],"force_p95":0.13393,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.5029,0.0176,0.17474]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50735,0.03588,0.04847]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6184.0,"contact_point_centroid":[0.5023,0.05499,0.04405],"force_p95":0.08376,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09914,"mean_force":0.04785,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.50221,0.0356,0.04227]}],"total_contact_groups":16},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.59944,0.17455,0.02602],"final_tcp_position":[0.62198,0.17018,0.22599],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":334.09255,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":438.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1748.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50735,0.03588,0.04847],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02335,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":334.09255,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.5072,0.03593,0.04799],"tcp_start":[0.50735,0.03588,0.04847],"tcp_to_object_dist_end":0.02292,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51254,0.03672,0.0249],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21472,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.19491,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13254.0,"raw_peak_contact_force":0.28009,"subtask_id":"grasp_1","tcp_end":[0.50218,0.03559,0.04224],"tcp_start":[0.50218,0.03559,0.04224],"tcp_to_object_dist_end":0.02023,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":352.0,"n_steps_budget":810.0,"object_pos_end":[0.51356,0.03614,0.13204],"object_pos_start":[0.51256,0.03669,0.02496],"object_to_goal_dist_end":0.17823,"object_to_goal_dist_start":0.21469,"object_z_max":0.13177,"peak_contact_force":0.10972,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13357.0,"raw_peak_contact_force":0.51494,"tcp_end":[0.49849,0.0353,0.15211],"tcp_start":[0.50218,0.03559,0.04224],"tcp_to_object_dist_end":0.02511,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":511.0,"n_steps_budget":1000.0,"object_pos_end":[0.61554,0.15948,0.16657],"object_pos_start":[0.51356,0.03614,0.13204],"object_to_goal_dist_end":0.02792,"object_to_goal_dist_start":0.17823,"object_z_max":0.19433,"peak_contact_force":0.13945,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12327.0,"raw_peak_contact_force":0.43523,"subtask_id":"transport_arc","tcp_end":[0.61334,0.15931,0.19926],"tcp_start":[0.49849,0.0353,0.15211],"tcp_to_object_dist_end":0.03276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":85.0,"n_steps_budget":1000.0,"object_pos_end":[0.62385,0.16685,0.12787],"object_pos_start":[0.61554,0.15948,0.16657],"object_to_goal_dist_end":0.01845,"object_to_goal_dist_start":0.02792,"object_z_max":0.16657,"peak_contact_force":0.12613,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1557.0,"raw_peak_contact_force":0.43245,"subtask_id":"release_1","tcp_end":[0.61853,0.16601,0.16145],"tcp_start":[0.61334,0.15931,0.19926],"tcp_to_object_dist_end":0.03401,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61054,0.1671,0.02641],"object_pos_start":[0.62385,0.16685,0.12787],"object_to_goal_dist_end":0.11995,"object_to_goal_dist_start":0.01845,"object_z_max":0.12787,"peak_contact_force":0.31779,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1408.0,"raw_peak_contact_force":1.44647,"tcp_end":[0.61203,0.16417,0.18003],"tcp_start":[0.61853,0.16601,0.16145],"tcp_to_object_dist_end":0.15365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":207.0,"n_steps_budget":600.0,"object_pos_end":[0.59944,0.17455,0.02602],"object_pos_start":[0.61054,0.1671,0.02641],"object_to_goal_dist_end":0.1223,"object_to_goal_dist_start":0.11995,"object_z_max":0.0271,"peak_contact_force":0.12345,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":779.0,"raw_peak_contact_force":0.3163,"tcp_end":[0.62198,0.17018,0.22599],"tcp_start":[0.61203,0.16417,0.18003],"tcp_to_object_dist_end":0.20128,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```