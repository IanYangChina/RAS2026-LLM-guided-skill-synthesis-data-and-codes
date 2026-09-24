## Search State

- **Seed**: 7
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.1982 | 0.27 | ✅ accepted |
| 7 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2113 | 0.24 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2167 | 0.25 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.0953 | 0.17 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.0966 | 0.24 | ✅ accepted |

**Proposal policy**: task_score is 0.27 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.198) — your mutation base

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

- **Composite score**: 0.198
- **task_score** (E): 0.272
- **fitness_score**: 0.598  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0828 |
| descend_1 | 1.00 | 1.00 | 0.1692 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 1.00 | 1.00 | 0.1081 |
| transport_to_goal | 1.00 | 1.00 | 0.2263 |
| place_descend | 1.00 | 1.00 | 0.0336 |
| release_1 | 1.00 | 1.00 | 0.0207 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.011, 0.224) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 11.240 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.011, 0.224)→(0.506, 0.021, 0.056) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.125 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.021, 0.056)→(0.498, 0.021, 0.046) | (0.511, 0.022, 0.026)→(0.511, 0.021, 0.025) | 0.273→0.274 | 1.00 / 43.667 | 0.172 | 0.235 |
| lift_1 | lift | 1.00 / step_budget | (0.498, 0.021, 0.046)→(0.502, 0.021, 0.154) | (0.511, 0.021, 0.025)→(0.509, 0.021, 0.124) | 0.274→0.228 | 1.00 / 23.333 | 0.109 | 0.411 |
| transport_to_goal | approach | 1.00 / step_budget | (0.502, 0.021, 0.154)→(0.596, 0.198, 0.251) | (0.509, 0.021, 0.124)→(0.587, 0.126, 0.016) | 0.228→0.206 | 1.00 / 8.333 | 0.123 | 1.674 |
| place_descend | descend | 1.00 / step_budget | (0.596, 0.198, 0.251)→(0.596, 0.202, 0.218) | (0.587, 0.126, 0.016)→(0.587, 0.126, 0.016) | 0.206→0.206 | 1.00 / 8.000 | 0.123 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.596, 0.202, 0.218)→(0.592, 0.200, 0.238) | (0.587, 0.126, 0.016)→(0.587, 0.126, 0.016) | 0.206→0.206 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.420
- phase_score: 0.451
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.006
- phase_breakdown.release_1_score: 0.343
- phase_breakdown.transport_arc_score: 0.298
- phase_breakdown.descend_1_score: 0.854
- grasp_place_fitness: 0.672

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.672
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.420
- **Median Q (composite search score)**: 0.176
- **K-run variance**: 0.0028
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.540


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53039,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.23845,"descend_1.grasp_z_offset":0.01103,"lift_1.lift_height":0.14587,"place_descend.place_z_offset":0.02852,"transport_to_goal.transport_speed":0.06551},"optimized_scores":{"best_composite_score":0.27173,"best_fitness_score":0.67173,"best_task_score":0.41972},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1663.0,"contact_point_centroid":[0.63484,0.15631,-0.00259],"force_p95":0.27248,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.60613,"mean_force":0.15161,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.61346,0.16212,0.20422]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.51066,0.03571,-0.0016],"force_p95":0.35554,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40548,"mean_force":0.07554,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49843,0.03638,0.04792]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10890.0,"contact_point_centroid":[0.50635,0.05548,0.11838],"force_p95":0.10442,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28912,"mean_force":0.07086,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50239,0.0367,0.11734]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10103.0,"contact_point_centroid":[0.50627,0.01788,0.12002],"force_p95":0.10894,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27048,"mean_force":0.07362,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5025,0.03671,0.11947]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51261,0.03953,-0.00226],"force_p95":0.19418,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25326,"mean_force":0.14117,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50062,0.03657,0.04744]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5823.0,"contact_point_centroid":[0.55256,0.10509,0.16814],"force_p95":0.12547,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2523,"mean_force":0.08356,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54644,0.08677,0.16959]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5684.0,"contact_point_centroid":[0.55294,0.06933,0.168],"force_p95":0.12151,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2431,"mean_force":0.08704,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54736,0.08777,0.17015]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4084.0,"contact_point_centroid":[0.50009,0.01724,0.04788],"force_p95":0.0825,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16146,"mean_force":0.05216,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49948,0.03648,0.04619]},{"body_a":"world","body_b":"grasp_target","contact_count":172.0,"contact_point_centroid":[0.51251,0.03972,-0.00123],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12402,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50166,0.00628,0.29399]},{"body_a":"world","body_b":"grasp_target","contact_count":1720.0,"contact_point_centroid":[0.51251,0.03972,-0.002],"force_p95":0.12337,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13005,"mean_force":0.12277,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50529,0.02641,0.1701]},{"body_a":"world","body_b":"grasp_target","contact_count":1828.0,"contact_point_centroid":[0.63491,0.15632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61461,0.16518,0.17749]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.63491,0.15632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61012,0.16399,0.17478]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5396.0,"contact_point_centroid":[0.50104,0.05573,0.04852],"force_p95":0.07771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08164,"mean_force":0.04181,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49949,0.03648,0.04621]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1523.0,"contact_point_centroid":[0.61357,0.16207,0.20563],"force_p95":0.01241,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01654,"mean_force":0.01071,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.61316,0.16204,0.20338]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1949.0,"contact_point_centroid":[0.61523,0.16523,0.17959],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.01045,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61461,0.16519,0.17742]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.61365,0.1649,0.1736],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.011,"mean_force":0.01007,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61288,0.16486,0.17142]}],"total_contact_groups":16},"final_pose_error":0.01475,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.63491,0.15632,0.01602],"final_tcp_position":[0.61805,0.1664,0.183],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.60613,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":44.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02595],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21225,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.13053,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":172.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50427,0.01595,0.28445],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25972,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":430.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02595],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21225,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1720.0,"raw_peak_contact_force":0.13005,"subtask_id":"descend_1","tcp_end":[0.50787,0.03707,0.05582],"tcp_start":[0.50427,0.01595,0.28445],"tcp_to_object_dist_end":0.03028,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51252,0.03752,0.02508],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21412,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.18778,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11280.0,"raw_peak_contact_force":0.25326,"subtask_id":"grasp_1","tcp_end":[0.49946,0.03647,0.04616],"tcp_start":[0.50787,0.03707,0.05582],"tcp_to_object_dist_end":0.02483,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":352.0,"n_steps_budget":810.0,"object_pos_end":[0.51042,0.03733,0.11624],"object_pos_start":[0.51252,0.03752,0.02508],"object_to_goal_dist_end":0.18119,"object_to_goal_dist_start":0.21412,"object_z_max":0.12648,"peak_contact_force":0.09858,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21079.0,"raw_peak_contact_force":0.40548,"tcp_end":[0.50329,0.03678,0.14626],"tcp_start":[0.49946,0.03647,0.04616],"tcp_to_object_dist_end":0.03086,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":639.0,"n_steps_budget":1000.0,"object_pos_end":[0.63491,0.15632,0.01602],"object_pos_start":[0.51042,0.03733,0.11624],"object_to_goal_dist_end":0.13023,"object_to_goal_dist_start":0.18119,"object_z_max":0.1648,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14693.0,"raw_peak_contact_force":1.60613,"subtask_id":"transport_arc","tcp_end":[0.61296,0.16194,0.20286],"tcp_start":[0.50329,0.03678,0.14626],"tcp_to_object_dist_end":0.18821,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":57.0,"n_steps_budget":1000.0,"object_pos_end":[0.63491,0.15632,0.01602],"object_pos_start":[0.63491,0.15632,0.01602],"object_to_goal_dist_end":0.13023,"object_to_goal_dist_start":0.13023,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3777.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61419,0.16524,0.1743],"tcp_start":[0.61296,0.16194,0.20286],"tcp_to_object_dist_end":0.15988,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63491,0.15632,0.01602],"object_pos_start":[0.63491,0.15632,0.01602],"object_to_goal_dist_end":0.13023,"object_to_goal_dist_start":0.13023,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60854,0.16347,0.19421],"tcp_start":[0.61419,0.16524,0.1743],"tcp_to_object_dist_end":0.18027,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94366,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16413,"descend_1.grasp_z_offset":0.01003,"lift_1.lift_height":0.16756,"place_descend.place_z_offset":0.02266,"transport_to_goal.transport_speed":0.19535},"optimized_scores":{"best_composite_score":0.17583,"best_fitness_score":0.57583,"best_task_score":0.22651},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2474.0,"contact_point_centroid":[0.56062,0.17251,-0.00245],"force_p95":0.12746,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.9738,"mean_force":0.14254,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56733,0.20835,0.28356]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.48114,0.04513,-0.00155],"force_p95":0.38212,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43477,"mean_force":0.088,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47037,0.04563,0.04839]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2945.0,"contact_point_centroid":[0.5031,0.07098,0.19485],"force_p95":0.15235,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31905,"mean_force":0.10758,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49782,0.08931,0.19782]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12018.0,"contact_point_centroid":[0.47686,0.06474,0.13163],"force_p95":0.10256,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28317,"mean_force":0.06847,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4736,0.0459,0.1308]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11256.0,"contact_point_centroid":[0.47666,0.02703,0.13217],"force_p95":0.11016,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24791,"mean_force":0.0714,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47363,0.0459,0.13171]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48279,0.04856,-0.00224],"force_p95":0.18803,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24651,"mean_force":0.13963,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47252,0.04586,0.04782]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3350.0,"contact_point_centroid":[0.50347,0.10744,0.19534],"force_p95":0.14086,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22597,"mean_force":0.09553,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.4979,0.08942,0.19791]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4603.0,"contact_point_centroid":[0.47067,0.0265,0.04728],"force_p95":0.07688,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15818,"mean_force":0.04688,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47144,0.04575,0.04671]},{"body_a":"world","body_b":"grasp_target","contact_count":504.0,"contact_point_centroid":[0.4827,0.04873,-0.00175],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12359,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49347,0.01603,0.26212]},{"body_a":"world","body_b":"grasp_target","contact_count":1248.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.482,0.04041,0.13765]},{"body_a":"world","body_b":"grasp_target","contact_count":1840.0,"contact_point_centroid":[0.56068,0.17254,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57311,0.22105,0.26026]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56068,0.17254,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57,0.21984,0.25795]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5566.0,"contact_point_centroid":[0.47075,0.06507,0.04755],"force_p95":0.07279,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07705,"mean_force":0.04073,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47145,0.04575,0.04672]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2415.0,"contact_point_centroid":[0.56959,0.21148,0.28775],"force_p95":0.01154,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01629,"mean_force":0.01068,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56911,0.21145,0.28558]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1972.0,"contact_point_centroid":[0.57373,0.22109,0.26253],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.0104,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57311,0.22104,0.26033]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.57244,0.22079,0.25634],"force_p95":0.01093,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01095,"mean_force":0.00994,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57183,0.22073,0.25413]}],"total_contact_groups":16},"final_pose_error":0.01499,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.56068,0.17254,0.01602],"final_tcp_position":[0.57549,0.22234,0.26504],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":33.46677,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":127.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28997,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":33.46677,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":504.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48614,0.03456,0.21972],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19425,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":312.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28997,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1248.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.4795,0.04647,0.05536],"tcp_start":[0.48614,0.03456,0.21972],"tcp_to_object_dist_end":0.0296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4827,0.04675,0.02516],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29181,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.18191,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11969.0,"raw_peak_contact_force":0.24651,"subtask_id":"grasp_1","tcp_end":[0.47142,0.04575,0.04668],"tcp_start":[0.4795,0.04647,0.05536],"tcp_to_object_dist_end":0.02432,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":401.0,"n_steps_budget":930.0,"object_pos_end":[0.48109,0.04643,0.13785],"object_pos_start":[0.4827,0.04675,0.02516],"object_to_goal_dist_end":0.22807,"object_to_goal_dist_start":0.29181,"object_z_max":0.14768,"peak_contact_force":0.12612,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23356.0,"raw_peak_contact_force":0.43477,"tcp_end":[0.47439,0.04596,0.16831],"tcp_start":[0.47142,0.04575,0.04668],"tcp_to_object_dist_end":0.0312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":661.0,"n_steps_budget":1000.0,"object_pos_end":[0.56068,0.17254,0.01602],"object_pos_start":[0.48109,0.04643,0.13785],"object_to_goal_dist_end":0.22275,"object_to_goal_dist_start":0.22807,"object_z_max":0.19523,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11184.0,"raw_peak_contact_force":1.9738,"subtask_id":"transport_arc","tcp_end":[0.57205,0.21744,0.28728],"tcp_start":[0.47439,0.04596,0.16831],"tcp_to_object_dist_end":0.27519,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":60.0,"n_steps_budget":1000.0,"object_pos_end":[0.56068,0.17254,0.01602],"object_pos_start":[0.56068,0.17254,0.01602],"object_to_goal_dist_end":0.22275,"object_to_goal_dist_start":0.22275,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3812.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57279,0.22114,0.2569],"tcp_start":[0.57205,0.21744,0.28728],"tcp_to_object_dist_end":0.24603,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56068,0.17254,0.01602],"object_pos_start":[0.56068,0.17254,0.01602],"object_to_goal_dist_end":0.22275,"object_to_goal_dist_start":0.22275,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56902,0.21932,0.27764],"tcp_start":[0.57279,0.22114,0.2569],"tcp_to_object_dist_end":0.2659,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.97163,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11087,"descend_1.grasp_z_offset":0.01076,"lift_1.lift_height":0.14721,"place_descend.place_z_offset":0.01251,"transport_to_goal.transport_speed":0.19794},"optimized_scores":{"best_composite_score":0.14703,"best_fitness_score":0.54703,"best_task_score":0.16933},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3791.0,"contact_point_centroid":[0.56637,0.04772,-0.00223],"force_p95":0.12537,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.44284,"mean_force":0.13434,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58739,0.16836,0.24354]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.5353,-0.01999,-0.00138],"force_p95":0.33325,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39348,"mean_force":0.07364,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52126,-0.02022,0.04669]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9655.0,"contact_point_centroid":[0.5309,-0.00149,0.11962],"force_p95":0.10841,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27381,"mean_force":0.07885,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52613,-0.02032,0.11789]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11017.0,"contact_point_centroid":[0.53084,-0.039,0.1198],"force_p95":0.10014,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2668,"mean_force":0.07107,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52619,-0.02032,0.11818]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1172.0,"contact_point_centroid":[0.53811,0.01754,0.15432],"force_p95":0.19362,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26229,"mean_force":0.10563,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53168,-0.00108,0.15481]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1566.0,"contact_point_centroid":[0.53838,-0.01681,0.15442],"force_p95":0.12755,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23091,"mean_force":0.08064,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53235,0.00129,0.15592]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53706,-0.02121,-0.00209],"force_p95":0.14845,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20564,"mean_force":0.12978,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52348,-0.02026,0.04662]},{"body_a":"world","body_b":"grasp_target","contact_count":768.0,"contact_point_centroid":[0.53702,-0.02132,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12326,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51274,-0.00793,0.23662]},{"body_a":"world","body_b":"grasp_target","contact_count":840.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52804,-0.01854,0.11204]},{"body_a":"world","body_b":"grasp_target","contact_count":1916.0,"contact_point_centroid":[0.56639,0.04776,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.60208,0.21969,0.228]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.56639,0.04776,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59833,0.21856,0.22329]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4585.0,"contact_point_centroid":[0.52365,-0.00102,0.04804],"force_p95":0.07125,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10619,"mean_force":0.04717,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5223,-0.02024,0.04526]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5200.0,"contact_point_centroid":[0.5233,-0.03945,0.0474],"force_p95":0.06828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07031,"mean_force":0.04269,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5223,-0.02024,0.04526]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3770.0,"contact_point_centroid":[0.59023,0.17541,0.24945],"force_p95":0.01106,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01588,"mean_force":0.01056,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58976,0.1754,0.24727]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2062.0,"contact_point_centroid":[0.60269,0.21974,0.23008],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01294,"mean_force":0.01037,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.60208,0.21971,0.22783]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.60113,0.21956,0.22235],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01263,"mean_force":0.01005,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60049,0.21951,0.21994]}],"total_contact_groups":16},"final_pose_error":0.01466,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.56639,0.04776,0.01602],"final_tcp_position":[0.60472,0.22125,0.23181],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.44284,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":193.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":768.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52703,-0.01674,0.1687],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14311,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":840.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53103,-0.02037,0.05579],"tcp_start":[0.52703,-0.01674,0.1687],"tcp_to_object_dist_end":0.03039,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53697,-0.02055,0.02565],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31633,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.1456,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11585.0,"raw_peak_contact_force":0.20564,"subtask_id":"grasp_1","tcp_end":[0.52227,-0.02024,0.04522],"tcp_start":[0.53103,-0.02037,0.05579],"tcp_to_object_dist_end":0.02448,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":373.0,"n_steps_budget":810.0,"object_pos_end":[0.53528,-0.02038,0.11837],"object_pos_start":[0.53697,-0.02055,0.02565],"object_to_goal_dist_end":0.27409,"object_to_goal_dist_start":0.31633,"object_z_max":0.1295,"peak_contact_force":0.10081,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20754.0,"raw_peak_contact_force":0.39348,"tcp_end":[0.52745,-0.02034,0.14761],"tcp_start":[0.52227,-0.02024,0.04522],"tcp_to_object_dist_end":0.03027,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":767.0,"n_steps_budget":1000.0,"object_pos_end":[0.56639,0.04776,0.01602],"object_pos_start":[0.53528,-0.02038,0.11837],"object_to_goal_dist_end":0.26638,"object_to_goal_dist_start":0.27409,"object_z_max":0.13522,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10299.0,"raw_peak_contact_force":1.44284,"subtask_id":"transport_arc","tcp_end":[0.60186,0.21469,0.26394],"tcp_start":[0.52745,-0.02034,0.14761],"tcp_to_object_dist_end":0.30098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":79.0,"n_steps_budget":1000.0,"object_pos_end":[0.56639,0.04776,0.01602],"object_pos_start":[0.56639,0.04776,0.01602],"object_to_goal_dist_end":0.26638,"object_to_goal_dist_start":0.26638,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3978.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.6016,0.21995,0.22298],"tcp_start":[0.60186,0.21469,0.26394],"tcp_to_object_dist_end":0.27152,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56639,0.04776,0.01602],"object_pos_start":[0.56639,0.04776,0.01602],"object_to_goal_dist_end":0.26638,"object_to_goal_dist_start":0.26638,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59713,0.218,0.24264],"tcp_start":[0.6016,0.21995,0.22298],"tcp_to_object_dist_end":0.2851,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```