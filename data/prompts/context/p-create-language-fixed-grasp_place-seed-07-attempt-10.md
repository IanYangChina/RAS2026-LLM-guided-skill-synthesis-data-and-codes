## Search State

- **Seed**: 7
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | time_limit | time_limit | time_limit | time_limit | 9 | -0.0559 | 0.16 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.1112 | 0.26 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.1982 | 0.27 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2113 | 0.24 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2167 | 0.25 | ✅ accepted |

**Proposal policy**: task_score is 0.16 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`
- Frozen object start: [0.5125095466604667, 0.039721380096957554, 0.03]
- Frozen task target: [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]
- Goal object position: (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5125095466604667, 0.039721380096957554, 0.03)
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
  frozen_object_start: [0.5125, 0.0397, 0.03]
  frozen_task_target: [0.6276, 0.1725, 0.145]
  frozen_object_starts: {'grasp_target': [0.5125095466604667, 0.039721380096957554, 0.03]}
  frozen_targets: {'place_target': [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6

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

## Current Skill (Q=-0.056) — your mutation base

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
    - 0.0
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: descend_1
- id: grasp_1
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
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
  subtask_id: grasp_1
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
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
      - path: target.offset.z
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: transport_to_goal
  type: approach
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.08
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
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
- id: place_descend
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: release_1
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=repeat
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=repeat
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.08, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **place_descend** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.056
- **task_score** (E): 0.164
- **fitness_score**: 0.544  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.600

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0951 |
| descend_1 | 1.00 | 1.00 | 0.1558 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 1.00 | 1.00 | 0.1084 |
| transport_to_goal | 1.00 | 1.00 | 0.0062 |
| place_descend | 1.00 | 1.00 | 0.0973 |
| release_1 | 1.00 | 1.00 | 0.0204 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.016, 0.211) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.016, 0.211)→(0.506, 0.021, 0.056) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.021, 0.056)→(0.498, 0.021, 0.046) | (0.511, 0.022, 0.026)→(0.511, 0.021, 0.025) | 0.273→0.274 | 1.00 / 43.667 | 0.167 | 0.232 |
| lift_1 | lift | 1.00 / time_limit | (0.498, 0.021, 0.046)→(0.502, 0.021, 0.155) | (0.511, 0.021, 0.025)→(0.509, 0.020, 0.120) | 0.274→0.232 | 1.00 / 14.667 | 0.120 | 0.447 |
| transport_to_goal | approach | 1.00 / time_limit | (0.602, 0.204, 0.319)→(0.604, 0.208, 0.315) | (0.509, 0.020, 0.120)→(0.520, 0.020, 0.016) | 0.232→0.278 | 1.00 / 8.667 | 182002.948 | 1.523 |
| place_descend | descend | 1.00 / time_limit | (0.604, 0.208, 0.315)→(0.600, 0.207, 0.218) | (0.520, 0.020, 0.016)→(0.520, 0.020, 0.016) | 0.278→0.278 | 1.00 / 8.333 | 0.123 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.600, 0.207, 0.218)→(0.596, 0.205, 0.238) | (0.520, 0.020, 0.016)→(0.520, 0.020, 0.016) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.233
- phase_score: 0.347
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.025
- phase_breakdown.release_1_score: 0.407
- phase_breakdown.transport_arc_score: 0.090
- phase_breakdown.descend_1_score: 0.846
- grasp_place_fitness: 0.578

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.578
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.233
- **Median Q (composite search score)**: -0.066
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.468


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `0b279c554151a1bc107b4895d67067efa2444eadb5a644f2482f57ab9ff93d7f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `079d4532bc3cff86c1b89933c7940f2ee474dc4233e12f8d134c76ceb3cd8d4d`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71429,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15641,"descend_1.grasp_z_offset":0.01161,"lift_1.lift_height":0.15107,"lift_1.lift_time":1.22518,"place_descend.descend_time":0.86957,"place_descend.place_z_offset":0.0296,"transport_to_goal.arc_height":0.07599,"transport_to_goal.transport_speed":0.16134,"transport_to_goal.transport_time":2.29831},"optimized_scores":{"best_composite_score":-0.02229,"best_fitness_score":0.57771,"best_task_score":0.2332},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":10817.0,"contact_point_centroid":[0.51876,0.03391,-0.00208],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.5857,"mean_force":0.12686,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57679,0.12084,0.25683]},{"body_a":"world","body_b":"grasp_target","contact_count":340.0,"contact_point_centroid":[0.5105,0.03747,-0.00174],"force_p95":0.20369,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46866,"mean_force":0.09756,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49735,0.03698,0.04798]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17457.0,"contact_point_centroid":[0.50522,0.05601,0.11186],"force_p95":0.10469,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29137,"mean_force":0.06783,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5017,0.03725,0.11149]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1024.0,"contact_point_centroid":[0.50753,0.05527,0.15915],"force_p95":0.19227,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29091,"mean_force":0.1049,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50158,0.03704,0.16212]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16502.0,"contact_point_centroid":[0.50495,0.01842,0.11241],"force_p95":0.11145,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27326,"mean_force":0.07041,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50178,0.03725,0.11245]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1087.0,"contact_point_centroid":[0.50716,0.01915,0.15947],"force_p95":0.12587,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25475,"mean_force":0.09746,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50142,0.03703,0.1631]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51259,0.03958,-0.00221],"force_p95":0.17972,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23952,"mean_force":0.13758,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50067,0.03725,0.04831]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4128.0,"contact_point_centroid":[0.50009,0.018,0.04855],"force_p95":0.08024,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1437,"mean_force":0.05157,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49954,0.03716,0.04706]},{"body_a":"world","body_b":"grasp_target","contact_count":524.0,"contact_point_centroid":[0.51251,0.03972,-0.00176],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12356,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50337,0.01312,0.25912]},{"body_a":"world","body_b":"grasp_target","contact_count":1176.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5067,0.03292,0.13492]},{"body_a":"world","body_b":"grasp_target","contact_count":2856.0,"contact_point_centroid":[0.51876,0.03393,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.62134,0.17047,0.19169]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51876,0.03393,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61538,0.16866,0.16826]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4899.0,"contact_point_centroid":[0.50034,0.0564,0.04843],"force_p95":0.07887,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08169,"mean_force":0.04544,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49955,0.03716,0.04707]},{"body_a":"left_finger","body_b":"right_finger","contact_count":11344.0,"contact_point_centroid":[0.57886,0.12253,0.26057],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01607,"mean_force":0.01042,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5783,0.1225,0.25833]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3060.0,"contact_point_centroid":[0.62204,0.17052,0.19391],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0127,"mean_force":0.01041,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.62135,0.17047,0.19177]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.61868,0.16963,0.16723],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.01011,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61814,0.16956,0.16496]}],"total_contact_groups":16},"final_pose_error":0.00492,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.51876,0.03393,0.01602],"final_tcp_position":[0.62344,0.17119,0.17694],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.5857,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":132.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12261,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":524.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50727,0.0282,0.21358],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18798,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":294.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1176.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.50796,0.03779,0.05672],"tcp_start":[0.50727,0.0282,0.21358],"tcp_to_object_dist_end":0.0311,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51251,0.03803,0.02526],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2137,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.17397,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10827.0,"raw_peak_contact_force":0.23952,"subtask_id":"grasp_1","tcp_end":[0.49951,0.03716,0.04703],"tcp_start":[0.50796,0.03779,0.05672],"tcp_to_object_dist_end":0.02536,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":781.0,"n_steps_budget":810.0,"object_pos_end":[0.50964,0.03808,0.12504],"object_pos_start":[0.51251,0.03803,0.02526],"object_to_goal_dist_end":0.17995,"object_to_goal_dist_start":0.2137,"object_z_max":0.13478,"peak_contact_force":0.12412,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34299.0,"raw_peak_contact_force":0.46866,"tcp_end":[0.50405,0.03737,0.15825],"tcp_start":[0.49951,0.03716,0.04703],"tcp_to_object_dist_end":0.03369,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":2510.0,"n_steps_budget":1000.0,"object_pos_end":[0.51876,0.03393,0.01602],"object_pos_start":[0.50964,0.03808,0.12504],"object_to_goal_dist_end":0.21838,"object_to_goal_dist_start":0.17995,"object_z_max":0.13434,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24272.0,"raw_peak_contact_force":1.5857,"subtask_id":"transport_arc","tcp_end":[0.62433,0.17122,0.26528],"tcp_start":[0.62281,0.16953,0.26838],"tcp_to_object_dist_end":0.30352,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":314.0,"n_steps_budget":1000.0,"object_pos_end":[0.51876,0.03393,0.01602],"object_pos_start":[0.51876,0.03393,0.01602],"object_to_goal_dist_end":0.21838,"object_to_goal_dist_start":0.21838,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5916.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61952,0.16998,0.16802],"tcp_start":[0.62433,0.17122,0.26528],"tcp_to_object_dist_end":0.22752,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51876,0.03393,0.01602],"object_pos_start":[0.51876,0.03393,0.01602],"object_to_goal_dist_end":0.21838,"object_to_goal_dist_start":0.21838,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61378,0.16812,0.18758],"tcp_start":[0.61952,0.16998,0.16802],"tcp_to_object_dist_end":0.23763,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a74f7c08b88460953bfa7e35b953cddf9278fdc17d2d4db8a2ea121b328e8b73`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85629,"average_solve_count":167.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14402,"descend_1.grasp_z_offset":0.01054,"lift_1.lift_height":0.14551,"lift_1.lift_time":0.95718,"place_descend.descend_time":1.02386,"place_descend.place_z_offset":0.02786,"transport_to_goal.arc_height":0.19585,"transport_to_goal.transport_speed":0.13146,"transport_to_goal.transport_time":2.09202},"optimized_scores":{"best_composite_score":-0.06618,"best_fitness_score":0.53382,"best_task_score":0.14352},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":10506.0,"contact_point_centroid":[0.49295,0.05308,-0.00208],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.55259,"mean_force":0.12649,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51443,0.11988,0.30102]},{"body_a":"world","body_b":"grasp_target","contact_count":335.0,"contact_point_centroid":[0.48083,0.04601,-0.00171],"force_p95":0.20819,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46239,"mean_force":0.09639,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4693,0.04558,0.04825]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1801.0,"contact_point_centroid":[0.47592,0.06214,0.15777],"force_p95":0.14664,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33902,"mean_force":0.10272,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47057,0.04404,0.16074]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1677.0,"contact_point_centroid":[0.47594,0.02591,0.157],"force_p95":0.1542,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30855,"mean_force":0.10572,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47053,0.04403,0.16057]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17836.0,"contact_point_centroid":[0.47548,0.06457,0.10968],"force_p95":0.10335,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2816,"mean_force":0.06413,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47282,0.04588,0.1091]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48279,0.04858,-0.00224],"force_p95":0.18821,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24911,"mean_force":0.13975,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47247,0.04589,0.04819]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15804.0,"contact_point_centroid":[0.47469,0.02699,0.10643],"force_p95":0.13432,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24621,"mean_force":0.07239,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47273,0.04588,0.10671]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4604.0,"contact_point_centroid":[0.47061,0.02653,0.04758],"force_p95":0.07655,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13936,"mean_force":0.04693,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47139,0.04578,0.04708]},{"body_a":"world","body_b":"grasp_target","contact_count":600.0,"contact_point_centroid":[0.4827,0.04873,-0.00179],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12344,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49302,0.01693,0.25281]},{"body_a":"world","body_b":"grasp_target","contact_count":1104.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48156,0.04123,0.12843]},{"body_a":"world","body_b":"grasp_target","contact_count":2848.0,"contact_point_centroid":[0.49297,0.05308,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57793,0.22678,0.27782]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.49297,0.05308,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5738,0.22496,0.25484]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5590.0,"contact_point_centroid":[0.4707,0.0651,0.04792],"force_p95":0.07275,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07685,"mean_force":0.04048,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4714,0.04578,0.04709]},{"body_a":"left_finger","body_b":"right_finger","contact_count":10859.0,"contact_point_centroid":[0.51623,0.12216,0.30636],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01626,"mean_force":0.01054,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51575,0.12213,0.30411]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3056.0,"contact_point_centroid":[0.5786,0.22683,0.27997],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.01039,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57792,0.22677,0.27775]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.57617,0.22595,0.25324],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01097,"mean_force":0.01006,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57562,0.22588,0.25113]}],"total_contact_groups":16},"final_pose_error":0.00487,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.49297,0.05308,0.01602],"final_tcp_position":[0.57927,0.22754,0.26225],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":273004.35751,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":151.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":600.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48536,0.03617,0.20095],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1754,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":276.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1104.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.47944,0.0465,0.05572],"tcp_start":[0.48536,0.03617,0.20095],"tcp_to_object_dist_end":0.02996,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48271,0.0468,0.02515],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29179,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.18227,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11994.0,"raw_peak_contact_force":0.24911,"subtask_id":"grasp_1","tcp_end":[0.47136,0.04578,0.04705],"tcp_start":[0.47944,0.0465,0.05572],"tcp_to_object_dist_end":0.02469,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":751.0,"n_steps_budget":780.0,"object_pos_end":[0.47976,0.0479,0.12058],"object_pos_start":[0.48271,0.0468,0.02515],"object_to_goal_dist_end":0.23505,"object_to_goal_dist_start":0.29179,"object_z_max":0.12991,"peak_contact_force":0.13044,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33975.0,"raw_peak_contact_force":0.46239,"tcp_end":[0.47445,0.04603,0.15378],"tcp_start":[0.47136,0.04578,0.04705],"tcp_to_object_dist_end":0.03367,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":2510.0,"n_steps_budget":1000.0,"object_pos_end":[0.49297,0.05308,0.01602],"object_pos_start":[0.47976,0.0479,0.12058],"object_to_goal_dist_end":0.2912,"object_to_goal_dist_start":0.23505,"object_z_max":0.13661,"peak_contact_force":273004.35751,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24843.0,"raw_peak_contact_force":1.55259,"subtask_id":"transport_arc","tcp_end":[0.58003,0.22742,0.35178],"tcp_start":[0.57666,0.22182,0.35563],"tcp_to_object_dist_end":0.38821,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":312.0,"n_steps_budget":1000.0,"object_pos_end":[0.49297,0.05308,0.01602],"object_pos_start":[0.49297,0.05308,0.01602],"object_to_goal_dist_end":0.2912,"object_to_goal_dist_start":0.2912,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5904.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57657,0.2263,0.25396],"tcp_start":[0.58003,0.22742,0.35178],"tcp_to_object_dist_end":0.30596,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49297,0.05308,0.01602],"object_pos_start":[0.49297,0.05308,0.01602],"object_to_goal_dist_end":0.2912,"object_to_goal_dist_start":0.2912,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57282,0.22442,0.27445],"tcp_start":[0.57657,0.2263,0.25396],"tcp_to_object_dist_end":0.32019,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b1a72366a9c9a56aa2e80fc4399e157c8281abf492ab3c1ede02058762a86ed7`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85714,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16379,"descend_1.grasp_z_offset":0.01027,"lift_1.lift_height":0.14489,"lift_1.lift_time":0.5247,"place_descend.descend_time":1.52126,"place_descend.place_z_offset":0.02933,"transport_to_goal.arc_height":0.05472,"transport_to_goal.transport_speed":0.15969,"transport_to_goal.transport_time":1.50941},"optimized_scores":{"best_composite_score":-0.07914,"best_fitness_score":0.52086,"best_task_score":0.11537},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":11356.0,"contact_point_centroid":[0.54713,-0.02588,-0.00206],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.43104,"mean_force":0.12665,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56415,0.10065,0.27116]},{"body_a":"world","body_b":"grasp_target","contact_count":234.0,"contact_point_centroid":[0.53473,-0.01996,-0.00129],"force_p95":0.20201,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40939,"mean_force":0.0693,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52078,-0.02021,0.04619]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17254.0,"contact_point_centroid":[0.52998,-0.03898,0.1112],"force_p95":0.09605,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26958,"mean_force":0.06597,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52564,-0.02032,0.10956]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14897.0,"contact_point_centroid":[0.52963,-0.00143,0.1076],"force_p95":0.12816,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26828,"mean_force":0.07477,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52532,-0.02032,0.106]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53706,-0.02122,-0.00209],"force_p95":0.1486,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20595,"mean_force":0.12977,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52366,-0.02027,0.04603]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":29.0,"contact_point_centroid":[0.53394,-0.03313,0.14618],"force_p95":0.12085,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13939,"mean_force":0.04355,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52797,-0.02033,0.15165]},{"body_a":"world","body_b":"grasp_target","contact_count":500.0,"contact_point_centroid":[0.53702,-0.02132,-0.00175],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1236,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51155,-0.00694,0.26205]},{"body_a":"world","body_b":"grasp_target","contact_count":1220.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52697,-0.01766,0.13708]},{"body_a":"world","body_b":"grasp_target","contact_count":2780.0,"contact_point_centroid":[0.54714,-0.02585,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.60593,0.22558,0.25448]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54714,-0.02585,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60138,0.22372,0.23153]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4824.0,"contact_point_centroid":[0.5237,-0.001,0.04725],"force_p95":0.07025,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1062,"mean_force":0.04506,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52248,-0.02024,0.04467]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5398.0,"contact_point_centroid":[0.52294,-0.03948,0.04724],"force_p95":0.06694,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06907,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52248,-0.02024,0.04467]},{"body_a":"left_finger","body_b":"right_finger","contact_count":11851.0,"contact_point_centroid":[0.56551,0.10327,0.27597],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01539,"mean_force":0.01048,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.565,0.10326,0.2737]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2999.0,"contact_point_centroid":[0.60664,0.22561,0.25644],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01286,"mean_force":0.01035,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.60592,0.22557,0.25425]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.60421,0.22471,0.23041],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01264,"mean_force":0.01015,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60343,0.22466,0.22832]}],"total_contact_groups":15},"final_pose_error":0.00483,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.54714,-0.02585,0.01602],"final_tcp_position":[0.60744,0.22638,0.24037],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273004.36508,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":126.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12258,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":500.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52457,-0.01498,0.21965],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19413,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":305.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1220.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.53122,-0.02037,0.0552],"tcp_start":[0.52457,-0.01498,0.21965],"tcp_to_object_dist_end":0.02977,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53697,-0.02057,0.02565],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31636,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14622,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12022.0,"raw_peak_contact_force":0.20595,"subtask_id":"grasp_1","tcp_end":[0.52245,-0.02024,0.04463],"tcp_start":[0.53122,-0.02037,0.0552],"tcp_to_object_dist_end":0.0239,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":752.0,"n_steps_budget":810.0,"object_pos_end":[0.53679,-0.02593,0.11578],"object_pos_start":[0.53697,-0.02057,0.02565],"object_to_goal_dist_end":0.27956,"object_to_goal_dist_start":0.31636,"object_z_max":0.13141,"peak_contact_force":0.10596,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32385.0,"raw_peak_contact_force":0.40939,"tcp_end":[0.52812,-0.02038,0.15168],"tcp_start":[0.52245,-0.02024,0.04463],"tcp_to_object_dist_end":0.03735,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":2510.0,"n_steps_budget":1000.0,"object_pos_end":[0.54714,-0.02585,0.01602],"object_pos_start":[0.53679,-0.02593,0.11578],"object_to_goal_dist_end":0.32394,"object_to_goal_dist_start":0.27956,"object_z_max":0.11578,"peak_contact_force":273004.36508,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23236.0,"raw_peak_contact_force":1.43104,"subtask_id":"transport_arc","tcp_end":[0.60832,0.22622,0.32803],"tcp_start":[0.60629,0.22034,0.3318],"tcp_to_object_dist_end":0.40575,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":295.0,"n_steps_budget":1000.0,"object_pos_end":[0.54714,-0.02585,0.01602],"object_pos_start":[0.54714,-0.02585,0.01602],"object_to_goal_dist_end":0.32394,"object_to_goal_dist_start":0.32394,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5779.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.60448,0.2251,0.23139],"tcp_start":[0.60832,0.22622,0.32803],"tcp_to_object_dist_end":0.33563,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54714,-0.02585,0.01602],"object_pos_start":[0.54714,-0.02585,0.01602],"object_to_goal_dist_end":0.32394,"object_to_goal_dist_start":0.32394,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60026,0.22316,0.2508],"tcp_start":[0.60448,0.2251,0.23139],"tcp_to_object_dist_end":0.34634,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```