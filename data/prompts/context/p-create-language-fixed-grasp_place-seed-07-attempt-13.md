## Search State

- **Seed**: 7
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.0953 | 0.17 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0018 | 0.18 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0077 | 0.20 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | time_limit | time_limit | time_limit | time_limit | 9 | -0.0559 | 0.16 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.1112 | 0.26 | ❌ rejected |

**Proposal policy**: task_score is 0.17 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.095) — your mutation base

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

- **Composite score**: 0.095
- **task_score** (E): 0.166
- **fitness_score**: 0.545  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1109 |
| descend_1 | 1.00 | 1.00 | 0.1398 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 1.00 | 0.33 | 0.1445 |
| transport_to_goal | 1.00 | 1.00 | 0.2165 |
| place_descend | 1.00 | 1.00 | 0.0528 |
| release_1 | 1.00 | 1.00 | 0.0207 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.016, 0.195) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.507, 0.016, 0.195)→(0.506, 0.021, 0.056) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.021, 0.056)→(0.498, 0.021, 0.046) | (0.511, 0.022, 0.026)→(0.511, 0.021, 0.025) | 0.273→0.274 | 1.00 / 43.667 | 0.167 | 0.231 |
| lift_1 | lift | 1.00 / step_budget | (0.498, 0.021, 0.046)→(0.503, 0.021, 0.190) | (0.511, 0.021, 0.025)→(0.513, 0.023, 0.132) | 0.274→0.225 | 0.33 / 8.667 | 0.030 | 0.414 |
| transport_to_goal | approach | 1.00 / step_budget | (0.503, 0.021, 0.190)→(0.595, 0.194, 0.273) | (0.513, 0.023, 0.132)→(0.521, 0.023, 0.016) | 0.225→0.276 | 1.00 / 8.667 | 0.123 | 1.780 |
| place_descend | descend | 1.00 / step_budget | (0.595, 0.194, 0.273)→(0.597, 0.202, 0.221) | (0.521, 0.023, 0.016)→(0.521, 0.023, 0.016) | 0.276→0.276 | 1.00 / 8.667 | 0.123 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.597, 0.202, 0.221)→(0.592, 0.200, 0.241) | (0.521, 0.023, 0.016)→(0.521, 0.023, 0.016) | 0.276→0.276 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.235
- phase_score: 0.390
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.040
- phase_breakdown.release_1_score: 0.339
- phase_breakdown.transport_arc_score: 0.185
- phase_breakdown.descend_1_score: 0.848
- grasp_place_fitness: 0.579

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.579
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.235
- **Median Q (composite search score)**: 0.085
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at lower bound**: descend_1.grasp_z_offset
- **Final σ (mean)**: 0.373


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8427,"average_solve_count":178.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13302,"descend_1.grasp_z_offset":0.01122,"lift_1.lift_height":0.18899,"place_descend.place_z_offset":0.028,"transport_to_goal.arc_height":0.11715,"transport_to_goal.transport_speed":0.0624},"optimized_scores":{"best_composite_score":0.12862,"best_fitness_score":0.57862,"best_task_score":0.23474},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3962.0,"contact_point_centroid":[0.52191,0.03301,-0.00224],"force_p95":0.12534,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.6686,"mean_force":0.13471,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57547,0.1185,0.24282]},{"body_a":"world","body_b":"grasp_target","contact_count":83.0,"contact_point_centroid":[0.51074,0.03646,-0.00152],"force_p95":0.36213,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3931,"mean_force":0.07628,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49836,0.03708,0.04855]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11066.0,"contact_point_centroid":[0.50681,0.05603,0.13826],"force_p95":0.12858,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29464,"mean_force":0.07871,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50253,0.03731,0.13818]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11218.0,"contact_point_centroid":[0.50681,0.01866,0.14131],"force_p95":0.12244,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27647,"mean_force":0.07601,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5027,0.03732,0.14161]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51259,0.03958,-0.00221],"force_p95":0.17923,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23925,"mean_force":0.13742,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50061,0.03727,0.04816]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4129.0,"contact_point_centroid":[0.50004,0.01802,0.04845],"force_p95":0.08031,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1439,"mean_force":0.05156,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49948,0.03718,0.04691]},{"body_a":"world","body_b":"grasp_target","contact_count":644.0,"contact_point_centroid":[0.51251,0.03972,-0.0018],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12339,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50348,0.01405,0.24772]},{"body_a":"world","body_b":"grasp_target","contact_count":1008.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50678,0.03377,0.12356]},{"body_a":"world","body_b":"grasp_target","contact_count":2016.0,"contact_point_centroid":[0.52193,0.03303,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61574,0.16562,0.18266]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52193,0.03303,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61145,0.16484,0.17601]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4889.0,"contact_point_centroid":[0.5003,0.05642,0.04833],"force_p95":0.07888,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08168,"mean_force":0.04553,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49948,0.03718,0.04692]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3972.0,"contact_point_centroid":[0.58058,0.12352,0.24674],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01631,"mean_force":0.01053,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58001,0.1235,0.24448]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2160.0,"contact_point_centroid":[0.61618,0.16566,0.18505],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.0104,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61574,0.16562,0.1827]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.61475,0.16575,0.17476],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.01006,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61416,0.1657,0.17258]}],"total_contact_groups":14},"final_pose_error":0.01493,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.52193,0.03303,0.01602],"final_tcp_position":[0.61934,0.16726,0.18433],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.6686,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":162.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":644.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50755,0.0299,0.1907],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16504,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1008.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.50791,0.03781,0.0566],"tcp_start":[0.50755,0.0299,0.1907],"tcp_to_object_dist_end":0.03098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51251,0.03804,0.02527],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21369,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.17347,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10818.0,"raw_peak_contact_force":0.23925,"subtask_id":"grasp_1","tcp_end":[0.49945,0.03718,0.04688],"tcp_start":[0.50791,0.03781,0.0566],"tcp_to_object_dist_end":0.02526,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":486.0,"n_steps_budget":1000.0,"object_pos_end":[0.51308,0.03282,0.14377],"object_pos_start":[0.51251,0.03804,0.02527],"object_to_goal_dist_end":0.18063,"object_to_goal_dist_start":0.21369,"object_z_max":0.16689,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22367.0,"raw_peak_contact_force":0.3931,"tcp_end":[0.50435,0.0374,0.18902],"tcp_start":[0.49945,0.03718,0.04688],"tcp_to_object_dist_end":0.04631,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":655.0,"n_steps_budget":1000.0,"object_pos_end":[0.52193,0.03303,0.01602],"object_pos_start":[0.51308,0.03282,0.14377],"object_to_goal_dist_end":0.21739,"object_to_goal_dist_start":0.18063,"object_z_max":0.14377,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7934.0,"raw_peak_contact_force":1.6686,"subtask_id":"transport_arc","tcp_end":[0.61225,0.16016,0.22698],"tcp_start":[0.50435,0.0374,0.18902],"tcp_to_object_dist_end":0.26234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":104.0,"n_steps_budget":1000.0,"object_pos_end":[0.52193,0.03303,0.01602],"object_pos_start":[0.52193,0.03303,0.01602],"object_to_goal_dist_end":0.21739,"object_to_goal_dist_start":0.21739,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4176.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.6155,0.1661,0.17558],"tcp_start":[0.61225,0.16016,0.22698],"tcp_to_object_dist_end":0.22786,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52193,0.03303,0.01602],"object_pos_start":[0.52193,0.03303,0.01602],"object_to_goal_dist_end":0.21739,"object_to_goal_dist_start":0.21739,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60989,0.16432,0.19542],"tcp_start":[0.6155,0.1661,0.17558],"tcp_to_object_dist_end":0.23908,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0625,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15214,"descend_1.grasp_z_offset":0.01,"lift_1.lift_height":0.21647,"place_descend.place_z_offset":0.02057,"transport_to_goal.arc_height":0.1103,"transport_to_goal.transport_speed":0.13445},"optimized_scores":{"best_composite_score":0.08495,"best_fitness_score":0.53495,"best_task_score":0.14509},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4573.0,"contact_point_centroid":[0.49512,0.05471,-0.00223],"force_p95":0.12397,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.87268,"mean_force":0.1329,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52877,0.14038,0.32076]},{"body_a":"world","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.48036,0.04537,-0.00157],"force_p95":0.39718,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43664,"mean_force":0.08985,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47029,0.04564,0.04848]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12268.0,"contact_point_centroid":[0.47729,0.06468,0.15011],"force_p95":0.12834,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28598,"mean_force":0.07447,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47364,0.04592,0.14987]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11843.0,"contact_point_centroid":[0.47737,0.02718,0.15332],"force_p95":0.12427,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24978,"mean_force":0.07528,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4738,0.04594,0.15334]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48279,0.04857,-0.00224],"force_p95":0.18845,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24959,"mean_force":0.13978,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47249,0.04587,0.04793]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4605.0,"contact_point_centroid":[0.47064,0.02651,0.04738],"force_p95":0.07683,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13957,"mean_force":0.0469,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47141,0.04577,0.04682]},{"body_a":"world","body_b":"grasp_target","contact_count":560.0,"contact_point_centroid":[0.4827,0.04873,-0.00177],"force_p95":0.13791,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1235,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49319,0.01662,0.25652]},{"body_a":"world","body_b":"grasp_target","contact_count":1164.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48172,0.04095,0.13205]},{"body_a":"world","body_b":"grasp_target","contact_count":2068.0,"contact_point_centroid":[0.49514,0.05471,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57381,0.22115,0.26392]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.49514,0.05471,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5709,0.22058,0.25663]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5579.0,"contact_point_centroid":[0.47073,0.06509,0.04768],"force_p95":0.07286,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07704,"mean_force":0.04059,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47142,0.04577,0.04683]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4634.0,"contact_point_centroid":[0.53213,0.14542,0.32715],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01577,"mean_force":0.01054,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53171,0.1454,0.32492]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2214.0,"contact_point_centroid":[0.57447,0.22121,0.26611],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01263,"mean_force":0.01041,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.57381,0.22116,0.26392]},{"body_a":"left_finger","body_b":"right_finger","contact_count":225.0,"contact_point_centroid":[0.57339,0.22154,0.25484],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01097,"mean_force":0.00995,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57272,0.22149,0.25279]}],"total_contact_groups":14},"final_pose_error":0.01496,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.49514,0.05471,0.01602],"final_tcp_position":[0.5764,0.22312,0.26374],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.87268,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":141.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":560.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48564,0.03561,0.20847],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18294,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":291.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1164.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.47947,0.04649,0.05548],"tcp_start":[0.48564,0.03561,0.20847],"tcp_to_object_dist_end":0.02972,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48271,0.04678,0.02515],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.2918,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.18238,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11984.0,"raw_peak_contact_force":0.24959,"subtask_id":"grasp_1","tcp_end":[0.47139,0.04576,0.04679],"tcp_start":[0.47947,0.04649,0.05548],"tcp_to_object_dist_end":0.02444,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":552.0,"n_steps_budget":1000.0,"object_pos_end":[0.48952,0.05587,0.11555],"object_pos_start":[0.48271,0.04678,0.02515],"object_to_goal_dist_end":0.22729,"object_to_goal_dist_start":0.2918,"object_z_max":0.19421,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24192.0,"raw_peak_contact_force":0.43664,"tcp_end":[0.47546,0.04608,0.21685],"tcp_start":[0.47139,0.04576,0.04679],"tcp_to_object_dist_end":0.10275,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":777.0,"n_steps_budget":1000.0,"object_pos_end":[0.49514,0.05471,0.01602],"object_pos_start":[0.48952,0.05587,0.11555],"object_to_goal_dist_end":0.28956,"object_to_goal_dist_start":0.22729,"object_z_max":0.11555,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9207.0,"raw_peak_contact_force":1.87268,"subtask_id":"transport_arc","tcp_end":[0.57097,0.21413,0.31332],"tcp_start":[0.47546,0.04608,0.21685],"tcp_to_object_dist_end":0.34577,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":117.0,"n_steps_budget":1000.0,"object_pos_end":[0.49514,0.05471,0.01602],"object_pos_start":[0.49514,0.05471,0.01602],"object_to_goal_dist_end":0.28956,"object_to_goal_dist_start":0.28956,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4282.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57369,0.2219,0.25559],"tcp_start":[0.57097,0.21413,0.31332],"tcp_to_object_dist_end":0.30252,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49514,0.05471,0.01602],"object_pos_start":[0.49514,0.05471,0.01602],"object_to_goal_dist_end":0.28956,"object_to_goal_dist_start":0.28956,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56992,0.22006,0.27631],"tcp_start":[0.57369,0.2219,0.25559],"tcp_to_object_dist_end":0.31731,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.96528,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12936,"descend_1.grasp_z_offset":0.01018,"lift_1.lift_height":0.16532,"place_descend.place_z_offset":0.02261,"transport_to_goal.arc_height":0.0786,"transport_to_goal.transport_speed":0.19975},"optimized_scores":{"best_composite_score":0.07237,"best_fitness_score":0.52237,"best_task_score":0.1186},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4038.0,"contact_point_centroid":[0.54588,-0.02022,-0.00223],"force_p95":0.12612,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79904,"mean_force":0.13462,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57818,0.13812,0.28143]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.53527,-0.02005,-0.00138],"force_p95":0.35451,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41166,"mean_force":0.07656,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52131,-0.02024,0.04612]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":782.0,"contact_point_centroid":[0.5333,-0.03491,0.17389],"force_p95":0.20098,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35524,"mean_force":0.10891,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52717,-0.01705,0.17697]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12011.0,"contact_point_centroid":[0.53132,-0.03921,0.1313],"force_p95":0.10014,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27172,"mean_force":0.07039,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52644,-0.02036,0.12995]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12067.0,"contact_point_centroid":[0.53149,-0.00153,0.13199],"force_p95":0.0952,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2703,"mean_force":0.06967,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52647,-0.02036,0.13031]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":539.0,"contact_point_centroid":[0.53336,0.00062,0.17244],"force_p95":0.20044,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2494,"mean_force":0.12252,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52708,-0.01785,0.17436]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53706,-0.02123,-0.00209],"force_p95":0.14838,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20533,"mean_force":0.12969,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52357,-0.02028,0.04606]},{"body_a":"world","body_b":"grasp_target","contact_count":672.0,"contact_point_centroid":[0.53702,-0.02132,-0.00181],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12335,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51239,-0.00764,0.24565]},{"body_a":"world","body_b":"grasp_target","contact_count":976.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52774,-0.01829,0.12074]},{"body_a":"world","body_b":"grasp_target","contact_count":1984.0,"contact_point_centroid":[0.54586,-0.02022,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.60194,0.21748,0.2384]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54586,-0.02022,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59845,0.21696,0.23241]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4824.0,"contact_point_centroid":[0.52365,-0.00101,0.04727],"force_p95":0.07025,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10678,"mean_force":0.04509,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52239,-0.02026,0.04469]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5426.0,"contact_point_centroid":[0.52287,-0.03949,0.04731],"force_p95":0.06687,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06901,"mean_force":0.04097,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52239,-0.02026,0.0447]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4139.0,"contact_point_centroid":[0.58046,0.14367,0.28585],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01638,"mean_force":0.0105,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58004,0.14366,0.2836]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2131.0,"contact_point_centroid":[0.60243,0.21751,0.24058],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0127,"mean_force":0.01039,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.60194,0.21748,0.23839]},{"body_a":"left_finger","body_b":"right_finger","contact_count":227.0,"contact_point_centroid":[0.60129,0.21793,0.23114],"force_p95":0.01082,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01085,"mean_force":0.00981,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60054,0.21789,0.22911]}],"total_contact_groups":16},"final_pose_error":0.01477,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.54586,-0.02022,0.01602],"final_tcp_position":[0.60458,0.21956,0.24089],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.79904,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":169.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":672.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52633,-0.01623,0.18674],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":244.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":976.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53114,-0.02039,0.05524],"tcp_start":[0.52633,-0.01623,0.18674],"tcp_to_object_dist_end":0.02982,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53697,-0.02059,0.02566],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31637,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14603,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12050.0,"raw_peak_contact_force":0.20533,"subtask_id":"grasp_1","tcp_end":[0.52236,-0.02026,0.04466],"tcp_start":[0.53114,-0.02039,0.05524],"tcp_to_object_dist_end":0.02397,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":435.0,"n_steps_budget":930.0,"object_pos_end":[0.53703,-0.02034,0.13675],"object_pos_start":[0.53697,-0.02059,0.02566],"object_to_goal_dist_end":0.26817,"object_to_goal_dist_start":0.31637,"object_z_max":0.14752,"peak_contact_force":0.0901,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24160.0,"raw_peak_contact_force":0.41166,"tcp_end":[0.52796,-0.02039,0.16556],"tcp_start":[0.52236,-0.02026,0.04466],"tcp_to_object_dist_end":0.0302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":786.0,"n_steps_budget":1000.0,"object_pos_end":[0.54586,-0.02022,0.01602],"object_pos_start":[0.53703,-0.02034,0.13675],"object_to_goal_dist_end":0.31981,"object_to_goal_dist_start":0.26817,"object_z_max":0.15845,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9498.0,"raw_peak_contact_force":1.79904,"subtask_id":"transport_arc","tcp_end":[0.60058,0.20847,0.2792],"tcp_start":[0.52796,-0.02039,0.16556],"tcp_to_object_dist_end":0.35293,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":96.0,"n_steps_budget":1000.0,"object_pos_end":[0.54586,-0.02022,0.01602],"object_pos_start":[0.54586,-0.02022,0.01602],"object_to_goal_dist_end":0.31981,"object_to_goal_dist_start":0.31981,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4115.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.60158,0.21831,0.23208],"tcp_start":[0.60058,0.20847,0.2792],"tcp_to_object_dist_end":0.32663,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54586,-0.02022,0.01602],"object_pos_start":[0.54586,-0.02022,0.01602],"object_to_goal_dist_end":0.31981,"object_to_goal_dist_start":0.31981,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59732,0.21641,0.25177],"tcp_start":[0.60158,0.21831,0.23208],"tcp_to_object_dist_end":0.33796,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```