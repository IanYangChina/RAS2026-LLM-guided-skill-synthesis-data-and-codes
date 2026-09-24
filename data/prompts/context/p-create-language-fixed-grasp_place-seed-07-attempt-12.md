## Search State

- **Seed**: 7
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0018 | 0.18 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0077 | 0.20 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | time_limit | time_limit | time_limit | time_limit | 9 | -0.0559 | 0.16 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.1112 | 0.26 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.1982 | 0.27 | ✅ accepted |

**Proposal policy**: task_score is 0.18 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.002) — your mutation base

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

- **Composite score**: 0.002
- **task_score** (E): 0.180
- **fitness_score**: 0.552  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.550

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1075 |
| descend_1 | 1.00 | 1.00 | 0.1428 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 1.00 | 1.00 | 0.1318 |
| transport_to_goal | 1.00 | 1.00 | 0.2267 |
| place_descend | 1.00 | 1.00 | 0.0522 |
| release_1 | 1.00 | 1.00 | 0.0207 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.505, 0.017, 0.199) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.505, 0.017, 0.199)→(0.506, 0.021, 0.056) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.021, 0.056)→(0.498, 0.021, 0.047) | (0.511, 0.022, 0.026)→(0.511, 0.021, 0.025) | 0.273→0.274 | 1.00 / 43.333 | 0.168 | 0.232 |
| lift_1 | lift | 1.00 / step_budget | (0.498, 0.021, 0.047)→(0.491, 0.020, 0.178) | (0.511, 0.021, 0.025)→(0.498, 0.021, 0.147) | 0.274→0.229 | 1.00 / 22.000 | 0.114 | 0.434 |
| transport_to_goal | approach | 1.00 / step_budget | (0.491, 0.020, 0.178)→(0.593, 0.193, 0.273) | (0.498, 0.021, 0.147)→(0.515, 0.036, 0.016) | 0.229→0.268 | 1.00 / 8.333 | 0.123 | 1.680 |
| place_descend | descend | 1.00 / step_budget | (0.593, 0.193, 0.273)→(0.596, 0.201, 0.222) | (0.515, 0.036, 0.016)→(0.515, 0.036, 0.016) | 0.268→0.268 | 1.00 / 8.333 | 0.123 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.596, 0.201, 0.222)→(0.592, 0.200, 0.242) | (0.515, 0.036, 0.016)→(0.515, 0.036, 0.016) | 0.268→0.268 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.280
- phase_score: 0.428
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.017
- phase_breakdown.release_1_score: 0.543
- phase_breakdown.transport_arc_score: 0.205
- phase_breakdown.descend_1_score: 0.829
- grasp_place_fitness: 0.600

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.600
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.280
- **Median Q (composite search score)**: -0.019
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.388


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.08966,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17589,"descend_1.grasp_z_offset":0.01271,"grasp_1.grasp_time":0.35159,"lift_1.lift_height":0.16224,"place_descend.place_z_offset":0.00042,"release_1.release_time":0.31174,"transport_to_goal.arc_height":0.0536,"transport_to_goal.transport_speed":0.14038},"optimized_scores":{"best_composite_score":0.0496,"best_fitness_score":0.5996,"best_task_score":0.2799},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3147.0,"contact_point_centroid":[0.53611,0.06535,-0.00233],"force_p95":0.12499,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.58319,"mean_force":0.13668,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58545,0.13274,0.23259]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.5104,0.0367,-0.00155],"force_p95":0.37377,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41968,"mean_force":0.08175,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49825,0.03696,0.04985]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11719.0,"contact_point_centroid":[0.49896,0.05522,0.14061],"force_p95":0.11733,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3024,"mean_force":0.07394,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49479,0.03669,0.14058]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10533.0,"contact_point_centroid":[0.49835,0.01796,0.13704],"force_p95":0.13155,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29523,"mean_force":0.08199,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4949,0.0367,0.13817]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":513.0,"contact_point_centroid":[0.50036,0.05797,0.1886],"force_p95":0.2127,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25783,"mean_force":0.11061,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49439,0.03978,0.1921]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":470.0,"contact_point_centroid":[0.50053,0.02172,0.18796],"force_p95":0.17048,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23963,"mean_force":0.11677,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.49439,0.03978,0.19209]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5126,0.03959,-0.00221],"force_p95":0.18099,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23941,"mean_force":0.13777,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50071,0.03717,0.04951]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4121.0,"contact_point_centroid":[0.50009,0.01791,0.04933],"force_p95":0.07952,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14111,"mean_force":0.05171,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49958,0.03708,0.04827]},{"body_a":"world","body_b":"grasp_target","contact_count":428.0,"contact_point_centroid":[0.51251,0.03972,-0.00171],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12379,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50326,0.01215,0.26831]},{"body_a":"world","body_b":"grasp_target","contact_count":1304.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50657,0.03199,0.1448]},{"body_a":"world","body_b":"grasp_target","contact_count":2188.0,"contact_point_centroid":[0.53619,0.06534,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.6153,0.16561,0.16001]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53619,0.06534,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61093,0.1652,0.14867]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4898.0,"contact_point_centroid":[0.50035,0.05632,0.04927],"force_p95":0.07861,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08145,"mean_force":0.0454,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49959,0.03708,0.04828]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3131.0,"contact_point_centroid":[0.59134,0.13823,0.23492],"force_p95":0.01113,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01654,"mean_force":0.01049,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.59083,0.1382,0.23267]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2315.0,"contact_point_centroid":[0.61593,0.16565,0.16218],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01052,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.6153,0.16561,0.15999]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.6145,0.16617,0.14753],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.01006,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61388,0.16612,0.1452]}],"total_contact_groups":16},"final_pose_error":0.01478,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.53619,0.06534,0.01602],"final_tcp_position":[0.61954,0.16779,0.15693],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.58319,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":108.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12237,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":428.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50695,0.02644,0.23202],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.2065,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":326.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1304.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.50799,0.0377,0.05794],"tcp_start":[0.50695,0.02644,0.23202],"tcp_to_object_dist_end":0.0323,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51251,0.03802,0.02525],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21372,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.1755,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10819.0,"raw_peak_contact_force":0.23941,"subtask_id":"grasp_1","tcp_end":[0.49955,0.03708,0.04823],"tcp_start":[0.50799,0.0377,0.05794],"tcp_to_object_dist_end":0.0264,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":456.0,"n_steps_budget":1000.0,"object_pos_end":[0.49803,0.03817,0.15102],"object_pos_start":[0.51251,0.03802,0.02525],"object_to_goal_dist_end":0.18672,"object_to_goal_dist_start":0.21372,"object_z_max":0.16133,"peak_contact_force":0.12809,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22334.0,"raw_peak_contact_force":0.41968,"tcp_end":[0.49245,0.03652,0.18528],"tcp_start":[0.49955,0.03708,0.04823],"tcp_to_object_dist_end":0.03475,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":538.0,"n_steps_budget":1000.0,"object_pos_end":[0.53619,0.06534,0.01602],"object_pos_start":[0.49803,0.03817,0.15102],"object_to_goal_dist_end":0.191,"object_to_goal_dist_start":0.18672,"object_z_max":0.16653,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7261.0,"raw_peak_contact_force":1.58319,"subtask_id":"transport_arc","tcp_end":[0.6101,0.15856,0.22117],"tcp_start":[0.49245,0.03652,0.18528],"tcp_to_object_dist_end":0.23715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":147.0,"n_steps_budget":1000.0,"object_pos_end":[0.53619,0.06534,0.01602],"object_pos_start":[0.53619,0.06534,0.01602],"object_to_goal_dist_end":0.191,"object_to_goal_dist_start":0.191,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4503.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61535,0.16655,0.1482],"tcp_start":[0.6101,0.15856,0.22117],"tcp_to_object_dist_end":0.18434,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53619,0.06534,0.01602],"object_pos_start":[0.53619,0.06534,0.01602],"object_to_goal_dist_end":0.191,"object_to_goal_dist_start":0.191,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60919,0.16464,0.1681],"tcp_start":[0.61535,0.16655,0.1482],"tcp_to_object_dist_end":0.19575,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.04375,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08686,"descend_1.grasp_z_offset":0.01001,"grasp_1.grasp_time":0.44753,"lift_1.lift_height":0.16571,"place_descend.place_z_offset":0.03728,"release_1.release_time":0.86066,"transport_to_goal.arc_height":0.10864,"transport_to_goal.transport_speed":0.12338},"optimized_scores":{"best_composite_score":-0.01911,"best_fitness_score":0.53089,"best_task_score":0.13749},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4209.0,"contact_point_centroid":[0.48007,0.04934,-0.00226],"force_p95":0.12407,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.74104,"mean_force":0.13377,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52932,0.14913,0.31869]},{"body_a":"world","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.48033,0.04533,-0.00159],"force_p95":0.40262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44563,"mean_force":0.09419,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46999,0.04546,0.04858]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":873.0,"contact_point_centroid":[0.467,0.06006,0.19836],"force_p95":0.18049,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31904,"mean_force":0.09245,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.4607,0.04187,0.1999]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":793.0,"contact_point_centroid":[0.46676,0.02347,0.19722],"force_p95":0.17838,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30498,"mean_force":0.0982,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.46074,0.04192,0.19962]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12355.0,"contact_point_centroid":[0.47022,0.06392,0.14146],"force_p95":0.10613,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29654,"mean_force":0.07082,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46671,0.04515,0.14085]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11646.0,"contact_point_centroid":[0.46996,0.02631,0.14301],"force_p95":0.11741,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26248,"mean_force":0.07422,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46666,0.04515,0.14281]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4828,0.04857,-0.00225],"force_p95":0.19161,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25214,"mean_force":0.14058,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47235,0.04571,0.04801]},{"body_a":"world","body_b":"grasp_target","contact_count":892.0,"contact_point_centroid":[0.4827,0.04873,-0.00185],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12317,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49196,0.01888,0.22482]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4597.0,"contact_point_centroid":[0.47053,0.02635,0.04754],"force_p95":0.07704,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13767,"mean_force":0.04697,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47127,0.0456,0.0469]},{"body_a":"world","body_b":"grasp_target","contact_count":684.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48066,0.04286,0.10041]},{"body_a":"world","body_b":"grasp_target","contact_count":1936.0,"contact_point_centroid":[0.48009,0.04933,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.5727,0.21981,0.27546]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.48009,0.04933,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57004,0.21908,0.27152]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5602.0,"contact_point_centroid":[0.4706,0.06494,0.04787],"force_p95":0.07362,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0779,"mean_force":0.04049,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47128,0.0456,0.04691]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4267.0,"contact_point_centroid":[0.53341,0.15467,0.3238],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01654,"mean_force":0.01054,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53287,0.15464,0.32157]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2080.0,"contact_point_centroid":[0.57343,0.21986,0.27774],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01268,"mean_force":0.01038,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.5727,0.2198,0.27545]},{"body_a":"left_finger","body_b":"right_finger","contact_count":218.0,"contact_point_centroid":[0.57231,0.21999,0.26992],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01097,"mean_force":0.01017,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57172,0.21993,0.26766]}],"total_contact_groups":16},"final_pose_error":0.01472,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.48009,0.04933,0.01602],"final_tcp_position":[0.57516,0.22148,0.27858],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.74104,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":224.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":892.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.4836,0.03958,0.14496],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1193,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":171.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":684.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47934,0.04632,0.05557],"tcp_start":[0.4836,0.03958,0.14496],"tcp_to_object_dist_end":0.02984,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48272,0.04668,0.02511],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29189,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.18534,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11999.0,"raw_peak_contact_force":0.25214,"subtask_id":"grasp_1","tcp_end":[0.47124,0.0456,0.04687],"tcp_start":[0.47934,0.04632,0.05557],"tcp_to_object_dist_end":0.02463,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":453.0,"n_steps_budget":1000.0,"object_pos_end":[0.47088,0.04596,0.15629],"object_pos_start":[0.48272,0.04668,0.02511],"object_to_goal_dist_end":0.22644,"object_to_goal_dist_start":0.29189,"object_z_max":0.1662,"peak_contact_force":0.12303,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24082.0,"raw_peak_contact_force":0.44563,"tcp_end":[0.46439,0.04494,0.18798],"tcp_start":[0.47124,0.0456,0.04687],"tcp_to_object_dist_end":0.03237,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":832.0,"n_steps_budget":1000.0,"object_pos_end":[0.48009,0.04933,0.01602],"object_pos_start":[0.47088,0.04596,0.15629],"object_to_goal_dist_end":0.29763,"object_to_goal_dist_start":0.22644,"object_z_max":0.18355,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10142.0,"raw_peak_contact_force":1.74104,"subtask_id":"transport_arc","tcp_end":[0.56937,0.21287,0.31019],"tcp_start":[0.46439,0.04494,0.18798],"tcp_to_object_dist_end":0.34822,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":84.0,"n_steps_budget":1000.0,"object_pos_end":[0.48009,0.04933,0.01602],"object_pos_start":[0.48009,0.04933,0.01602],"object_to_goal_dist_end":0.29763,"object_to_goal_dist_start":0.29763,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4016.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57262,0.22032,0.27046],"tcp_start":[0.56937,0.21287,0.31019],"tcp_to_object_dist_end":0.32023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48009,0.04933,0.01602],"object_pos_start":[0.48009,0.04933,0.01602],"object_to_goal_dist_end":0.29763,"object_to_goal_dist_start":0.29763,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56915,0.21858,0.29122],"tcp_start":[0.57262,0.22032,0.27046],"tcp_to_object_dist_end":0.33513,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.96471,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16278,"descend_1.grasp_z_offset":0.01011,"grasp_1.grasp_time":0.47026,"lift_1.lift_height":0.142,"place_descend.place_z_offset":0.03957,"release_1.release_time":0.47768,"transport_to_goal.arc_height":0.11562,"transport_to_goal.transport_speed":0.10572},"optimized_scores":{"best_composite_score":-0.02508,"best_fitness_score":0.52492,"best_task_score":0.12298},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4655.0,"contact_point_centroid":[0.52926,-0.00808,-0.00222],"force_p95":0.12386,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.71597,"mean_force":0.13229,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56735,0.12215,0.30051]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.5346,-0.01992,-0.0014],"force_p95":0.41089,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43606,"mean_force":0.09296,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52114,-0.02022,0.04583]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1236.0,"contact_point_centroid":[0.51756,-0.04006,0.17771],"force_p95":0.19194,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32937,"mean_force":0.10794,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51182,-0.02147,0.17872]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11498.0,"contact_point_centroid":[0.52187,-0.00131,0.12907],"force_p95":0.1,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28695,"mean_force":0.0708,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51718,-0.02012,0.12712]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11480.0,"contact_point_centroid":[0.52179,-0.03897,0.12829],"force_p95":0.10162,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28682,"mean_force":0.07127,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51719,-0.02012,0.1267]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1582.0,"contact_point_centroid":[0.51777,-0.00326,0.17921],"force_p95":0.14209,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24618,"mean_force":0.0866,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51175,-0.02146,0.18071]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53705,-0.02121,-0.00209],"force_p95":0.14704,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20405,"mean_force":0.12949,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52365,-0.02027,0.04582]},{"body_a":"world","body_b":"grasp_target","contact_count":504.0,"contact_point_centroid":[0.53702,-0.02132,-0.00175],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12359,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51153,-0.00694,0.26174]},{"body_a":"world","body_b":"grasp_target","contact_count":1216.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52694,-0.01766,0.13656]},{"body_a":"world","body_b":"grasp_target","contact_count":1944.0,"contact_point_centroid":[0.52926,-0.00809,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.60151,0.21661,0.25307]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52926,-0.00809,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59839,0.21611,0.2481]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4919.0,"contact_point_centroid":[0.52351,-0.00107,0.04726],"force_p95":0.06874,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11373,"mean_force":0.04395,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52247,-0.02024,0.04446]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4952.0,"contact_point_centroid":[0.52347,-0.03952,0.04624],"force_p95":0.07122,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07336,"mean_force":0.04483,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52247,-0.02024,0.04446]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4761.0,"contact_point_centroid":[0.56995,0.12765,0.30525],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0165,"mean_force":0.01049,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56949,0.12764,0.30298]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.6009,0.21703,0.24676],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01274,"mean_force":0.01016,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6003,0.217,0.24477]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2094.0,"contact_point_centroid":[0.602,0.21664,0.25525],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0127,"mean_force":0.01036,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.60151,0.2166,0.25305]}],"total_contact_groups":16},"final_pose_error":0.01464,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.52926,-0.00809,0.01602],"final_tcp_position":[0.60408,0.21859,0.25655],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.71597,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":127.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12259,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":504.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52457,-0.01498,0.21892],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19341,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":304.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1216.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.53121,-0.02037,0.05498],"tcp_start":[0.52457,-0.01498,0.21892],"tcp_to_object_dist_end":0.02955,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53696,-0.0206,0.02567],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31637,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14368,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11671.0,"raw_peak_contact_force":0.20405,"subtask_id":"grasp_1","tcp_end":[0.52244,-0.02024,0.04442],"tcp_start":[0.53121,-0.02037,0.05498],"tcp_to_object_dist_end":0.02372,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":406.0,"n_steps_budget":900.0,"object_pos_end":[0.52363,-0.02,0.13278],"object_pos_start":[0.53696,-0.0206,0.02567],"object_to_goal_dist_end":0.27289,"object_to_goal_dist_start":0.31637,"object_z_max":0.14337,"peak_contact_force":0.09025,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23058.0,"raw_peak_contact_force":0.43606,"tcp_end":[0.51473,-0.02006,0.16099],"tcp_start":[0.52244,-0.02024,0.04442],"tcp_to_object_dist_end":0.02958,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52926,-0.00809,0.01602],"object_pos_start":[0.52363,-0.02,0.13278],"object_to_goal_dist_end":0.31436,"object_to_goal_dist_start":0.27289,"object_z_max":0.17403,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12234.0,"raw_peak_contact_force":1.71597,"subtask_id":"transport_arc","tcp_end":[0.59927,0.2071,0.2888],"tcp_start":[0.51473,-0.02006,0.16099],"tcp_to_object_dist_end":0.35442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":86.0,"n_steps_budget":1000.0,"object_pos_end":[0.52926,-0.00809,0.01602],"object_pos_start":[0.52926,-0.00809,0.01602],"object_to_goal_dist_end":0.31436,"object_to_goal_dist_start":0.31436,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4038.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.60129,0.2174,0.24776],"tcp_start":[0.59927,0.2071,0.2888],"tcp_to_object_dist_end":0.33127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52926,-0.00809,0.01602],"object_pos_start":[0.52926,-0.00809,0.01602],"object_to_goal_dist_end":0.31436,"object_to_goal_dist_start":0.31436,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59736,0.21559,0.26746],"tcp_start":[0.60129,0.2174,0.24776],"tcp_to_object_dist_end":0.34336,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```