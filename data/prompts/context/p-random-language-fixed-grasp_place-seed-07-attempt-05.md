## Search State

- **Seed**: 7
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 16 | -0.0055 | 0.89 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 19 | -0.3651 | 0.30 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 19 | -0.4341 | 0.17 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 20 | -0.3970 | 0.25 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 20 | -0.4756 | 0.15 | ✅ accepted |

**Proposal policy**: task_score is 0.89 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.005) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_1
  anchor: object
  target_entity: None
- id: descend_1
  anchor: object
  target_entity: None
  offset:
  - 0.0
  - 0.0
  - 0.02
- id: grasp_1
  anchor: object
  target_entity: None
  metric: contact
  offset:
  - 0.0
  - 0.0
  - 0.02
- id: transport_arc
  target_entity: None
- id: release_1
  target_entity: None
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
      tolerance: 0.1
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_tol:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: approach_1
- id: descend_1
  type: descend
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
      tolerance: 0.1
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    descend_tol:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    grasp_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.1
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
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
    orientation:
      mode: none
  parameters:
    grasp_duration:
      type: scalar
      range:
      - 0.5
      - 3.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
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
    tolerance: 0.02
    orientation:
      mode: keep_current
      tolerance: 0.1
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
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    lift_tol:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: object_lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.0
    on_failure: abort
  retries:
    max_attempts: 0
    strategy: repeat
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
      tolerance: 0.1
  parameters:
    transport_altitude:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    transport_tol:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: transport_grasp_guard
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: continue
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: transport_arc
- id: place_1
  type: descend
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
      tolerance: 0.1
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    place_tol:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    place_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.1
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.01

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_tol: status=consumed; consumers=termination.pose_tolerance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_tol: status=consumed; consumers=termination.pose_tolerance (replace)
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)
  - retries: max_attempts=0, strategy=repeat
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
    - lift_tol: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=object_lift_check, when=after_phase, predicate=object_lifted, on_failure=abort, threshold=0.0
  - retries: max_attempts=0, strategy=repeat
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - transport_altitude: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_tol: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=transport_grasp_guard, when=during_phase, predicate=bilateral_grasp, on_failure=continue, threshold=0.0
  - retries: max_attempts=0, strategy=repeat
- **place_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_tol: status=consumed; consumers=termination.pose_tolerance (replace)
    - place_z_offset: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, -0.01]

## Design Metrics

- **Composite score**: -0.005
- **task_score** (E): 0.886
- **fitness_score**: 0.915  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.920

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0602 |
| descend_1 | 1.00 | 1.00 | 0.2137 |
| grasp_1 | 1.00 | 1.00 | 0.0122 |
| lift_1 | 1.00 | 1.00 | 0.2047 |
| transport_arc | 0.00 | 1.00 | 0.0887 |
| place_1 | 0.67 | 1.00 | 0.1326 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.018, 0.260) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.507, 0.018, 0.260)→(0.506, 0.022, 0.046) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.022, 0.046)→(0.498, 0.021, 0.037) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.274 | 1.00 / 42.000 | 0.147 | 0.210 |
| lift_1 | lift | 1.00 / step_budget | (0.498, 0.021, 0.037)→(0.495, 0.021, 0.242) | (0.511, 0.022, 0.026)→(0.503, 0.021, 0.225) | 0.274→0.225 | 1.00 / 40.000 | 0.076 | 0.494 |
| transport_arc | approach | 0.00 / guard_failure | (0.495, 0.021, 0.242)→(0.536, 0.088, 0.281) | (0.503, 0.021, 0.225)→(0.541, 0.087, 0.259) | 0.225→0.161 | 1.00 / 37.000 | 0.027 | 0.131 |
| place_1 | descend | 0.67 / step_budget | (0.536, 0.088, 0.281)→(0.594, 0.187, 0.226) | (0.541, 0.087, 0.259)→(0.596, 0.186, 0.200) | 0.161→0.030 | 1.00 / 29.667 | 0.102 | 0.178 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.147
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.252
- phase_breakdown.approach_1_score: 0.005
- phase_breakdown.transport_arc_score: 0.041
- phase_breakdown.release_1_score: 0.000
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.794
- grasp_place_fitness: 0.978

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.978
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.046
- **K-run variance**: 0.0066
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.319


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.19454,"average_solve_count":293.0,"average_success_count":293.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.27665,"approach_1.approach_tol":0.03288,"approach_1.speed":0.09354,"descend_1.descend_speed":0.06053,"descend_1.descend_tol":0.02394,"descend_1.grasp_z_offset":0.005,"grasp_1.grasp_duration":1.61084,"lift_1.lift_height":0.23152,"lift_1.lift_speed":0.03523,"lift_1.lift_tol":0.03573,"place_1.place_speed":0.06348,"place_1.place_tol":0.03361,"place_1.place_z_offset":0.04284,"transport_arc.transport_altitude":0.16586,"transport_arc.transport_speed":0.10676,"transport_arc.transport_tol":0.02612},"optimized_scores":{"best_composite_score":0.05786,"best_fitness_score":0.97786,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.50802,0.03796,-0.00153],"force_p95":0.53676,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56055,"mean_force":0.21347,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49831,0.03826,0.03163]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15436.0,"contact_point_centroid":[0.49571,0.05721,0.13569],"force_p95":0.07422,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28879,"mean_force":0.05054,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49589,0.03806,0.13402]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14979.0,"contact_point_centroid":[0.49583,0.0189,0.13839],"force_p95":0.07488,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28093,"mean_force":0.05121,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4959,0.03806,0.13627]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51255,0.03945,-0.00212],"force_p95":0.15893,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23519,"mean_force":0.13228,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50062,0.03846,0.03185]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10971.0,"contact_point_centroid":[0.59002,0.11563,0.22124],"force_p95":0.09239,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17661,"mean_force":0.06254,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.58702,0.13452,0.2206]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10962.0,"contact_point_centroid":[0.59148,0.15472,0.21999],"force_p95":0.08509,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17149,"mean_force":0.0628,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.58828,0.1358,0.2191]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4069.0,"contact_point_centroid":[0.49998,0.01916,0.03338],"force_p95":0.08059,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1483,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49944,0.03837,0.03058]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13243.0,"contact_point_centroid":[0.52713,0.05126,0.25482],"force_p95":0.08779,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14093,"mean_force":0.05952,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52538,0.07024,0.25315]},{"body_a":"world","body_b":"grasp_target","contact_count":992.0,"contact_point_centroid":[0.51251,0.03972,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12312,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50349,0.01783,0.29877]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13597.0,"contact_point_centroid":[0.52694,0.08903,0.25423],"force_p95":0.08566,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12674,"mean_force":0.05834,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52517,0.07005,0.25302]},{"body_a":"world","body_b":"grasp_target","contact_count":3368.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50684,0.03639,0.1682]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4992.0,"contact_point_centroid":[0.49997,0.05752,0.0324],"force_p95":0.07324,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08521,"mean_force":0.04467,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49945,0.03837,0.03058]}],"total_contact_groups":12},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62509,0.16788,0.16125],"final_tcp_position":[0.62031,0.16797,0.18271],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.56055,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":249.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":992.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50816,0.03388,0.29991],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27399,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":842.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3368.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50765,0.03903,0.03957],"tcp_start":[0.50816,0.03388,0.29991],"tcp_to_object_dist_end":0.01441,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51241,0.03841,0.02558],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21334,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15128,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10861.0,"raw_peak_contact_force":0.23519,"subtask_id":"grasp_1","tcp_end":[0.49942,0.03836,0.03054],"tcp_start":[0.50765,0.03903,0.03957],"tcp_to_object_dist_end":0.01391,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":744.0,"n_steps_budget":1000.0,"object_pos_end":[0.50652,0.03815,0.23198],"object_pos_start":[0.51241,0.03841,0.02558],"object_to_goal_dist_end":0.20068,"object_to_goal_dist_start":0.21334,"object_z_max":0.23171,"peak_contact_force":0.07006,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":30507.0,"raw_peak_contact_force":0.56055,"tcp_end":[0.49652,0.03811,0.24248],"tcp_start":[0.49942,0.03836,0.03054],"tcp_to_object_dist_end":0.01449,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":799.0,"n_steps_budget":1000.0,"object_pos_end":[0.56179,0.09889,0.24936],"object_pos_start":[0.50652,0.03815,0.23198],"object_to_goal_dist_end":0.14365,"object_to_goal_dist_start":0.20068,"object_z_max":0.24931,"peak_contact_force":0.0,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26840.0,"raw_peak_contact_force":0.14093,"subtask_id":"transport_arc","tcp_end":[0.55354,0.0991,0.26677],"tcp_start":[0.49652,0.03811,0.24248],"tcp_to_object_dist_end":0.01927,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":710.0,"n_steps_budget":1000.0,"object_pos_end":[0.62509,0.16788,0.16125],"object_pos_start":[0.56179,0.09889,0.24936],"object_to_goal_dist_end":0.01706,"object_to_goal_dist_start":0.14365,"object_z_max":0.24936,"peak_contact_force":0.09373,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":21933.0,"raw_peak_contact_force":0.17661,"tcp_end":[0.62031,0.16797,0.18271],"tcp_start":[0.55354,0.0991,0.26677],"tcp_to_object_dist_end":0.02199,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39695,"average_solve_count":262.0,"average_success_count":262.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.21925,"approach_1.approach_tol":0.02869,"approach_1.speed":0.1021,"descend_1.descend_speed":0.06915,"descend_1.descend_tol":0.02843,"descend_1.grasp_z_offset":0.01694,"grasp_1.grasp_duration":1.74121,"lift_1.lift_height":0.23398,"lift_1.lift_speed":0.02847,"lift_1.lift_tol":0.02709,"place_1.place_speed":0.10307,"place_1.place_tol":0.01964,"place_1.place_z_offset":0.0308,"transport_arc.transport_altitude":0.17358,"transport_arc.transport_speed":0.07504,"transport_arc.transport_tol":0.02857},"optimized_scores":{"best_composite_score":0.04619,"best_fitness_score":0.96619,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":89.0,"contact_point_centroid":[0.47912,0.04675,-0.00156],"force_p95":0.41302,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43256,"mean_force":0.16706,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46959,0.04685,0.04475]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14969.0,"contact_point_centroid":[0.46735,0.06574,0.15365],"force_p95":0.07514,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28152,"mean_force":0.05167,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46736,0.04663,0.15171]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13998.0,"contact_point_centroid":[0.46674,0.02746,0.15049],"force_p95":0.0794,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24964,"mean_force":0.05393,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46733,0.04662,0.14798]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48275,0.04853,-0.00214],"force_p95":0.16098,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22571,"mean_force":0.13327,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47174,0.04707,0.04482]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12069.0,"contact_point_centroid":[0.54359,0.19198,0.28308],"force_p95":0.10338,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22009,"mean_force":0.05819,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.54415,0.17299,0.28397]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12641.0,"contact_point_centroid":[0.54469,0.15737,0.28162],"force_p95":0.08315,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21229,"mean_force":0.05544,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.54625,0.17628,0.28206]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19918.0,"contact_point_centroid":[0.49088,0.06964,0.28773],"force_p95":0.07303,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14342,"mean_force":0.0489,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49211,0.08886,0.28666]},{"body_a":"world","body_b":"grasp_target","contact_count":860.0,"contact_point_centroid":[0.4827,0.04873,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1232,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49118,0.01882,0.27651]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21960.0,"contact_point_centroid":[0.49182,0.10802,0.28712],"force_p95":0.06727,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13675,"mean_force":0.04497,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49214,0.0889,0.2867]},{"body_a":"world","body_b":"grasp_target","contact_count":2632.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47954,0.0436,0.15141]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4769.0,"contact_point_centroid":[0.4699,0.02773,0.04723],"force_p95":0.07297,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10849,"mean_force":0.0451,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47065,0.04696,0.04368]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5277.0,"contact_point_centroid":[0.47054,0.06627,0.04562],"force_p95":0.07152,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07355,"mean_force":0.04283,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47065,0.04696,0.04368]}],"total_contact_groups":12},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57545,0.22273,0.22424],"final_tcp_position":[0.57612,0.22306,0.25555],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.43256,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":216.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":860.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48305,0.03969,0.25322],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22738,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":658.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2632.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47836,0.04771,0.05173],"tcp_start":[0.48305,0.03969,0.25322],"tcp_to_object_dist_end":0.02609,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48267,0.04739,0.02549],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29119,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.1555,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11846.0,"raw_peak_contact_force":0.22571,"subtask_id":"grasp_1","tcp_end":[0.47062,0.04696,0.04365],"tcp_start":[0.47836,0.04771,0.05173],"tcp_to_object_dist_end":0.02179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":725.0,"n_steps_budget":1000.0,"object_pos_end":[0.47457,0.04664,0.2354],"object_pos_start":[0.48267,0.04739,0.02549],"object_to_goal_dist_end":0.21152,"object_to_goal_dist_start":0.29119,"object_z_max":0.23512,"peak_contact_force":0.07799,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29056.0,"raw_peak_contact_force":0.43256,"tcp_end":[0.46793,0.04668,0.258],"tcp_start":[0.47062,0.04696,0.04365],"tcp_to_object_dist_end":0.02355,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.517,0.1259,0.28809],"object_pos_start":[0.47457,0.04664,0.2354],"object_to_goal_dist_end":0.13464,"object_to_goal_dist_start":0.21152,"object_z_max":0.28805,"peak_contact_force":0.08196,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":41878.0,"raw_peak_contact_force":0.14342,"subtask_id":"transport_arc","tcp_end":[0.51569,0.12614,0.31578],"tcp_start":[0.46793,0.04668,0.258],"tcp_to_object_dist_end":0.02772,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":698.0,"n_steps_budget":1000.0,"object_pos_end":[0.57545,0.22273,0.22424],"object_pos_start":[0.517,0.1259,0.28809],"object_to_goal_dist_end":0.01085,"object_to_goal_dist_start":0.13464,"object_z_max":0.28809,"peak_contact_force":0.11019,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":24710.0,"raw_peak_contact_force":0.22009,"tcp_end":[0.57612,0.22306,0.25555],"tcp_start":[0.51569,0.12614,0.31578],"tcp_to_object_dist_end":0.03133,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.49749,"average_solve_count":199.0,"average_success_count":199.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19248,"approach_1.approach_tol":0.04344,"approach_1.speed":0.14717,"descend_1.descend_speed":0.08602,"descend_1.descend_tol":0.02015,"descend_1.grasp_z_offset":0.01377,"grasp_1.grasp_duration":2.14114,"lift_1.lift_height":0.20749,"lift_1.lift_speed":0.04983,"lift_1.lift_tol":0.02541,"place_1.place_speed":0.12019,"place_1.place_tol":0.0117,"place_1.place_z_offset":0.03541,"transport_arc.transport_altitude":0.19228,"transport_arc.transport_speed":0.07165,"transport_arc.transport_tol":0.03151},"optimized_scores":{"best_composite_score":-0.12042,"best_fitness_score":0.79958,"best_task_score":0.65704},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.53298,-0.02044,-0.00141],"force_p95":0.46346,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48807,"mean_force":0.16301,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52204,-0.02082,0.03925]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12691.0,"contact_point_centroid":[0.51989,-0.00163,0.13191],"force_p95":0.07882,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30188,"mean_force":0.05571,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51948,-0.02076,0.12941]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13301.0,"contact_point_centroid":[0.51986,-0.03984,0.13012],"force_p95":0.07769,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28283,"mean_force":0.05379,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51947,-0.02076,0.12795]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02118,-0.00205],"force_p95":0.13651,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16836,"mean_force":0.12651,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52439,-0.02086,0.03953]},{"body_a":"world","body_b":"grasp_target","contact_count":1136.0,"contact_point_centroid":[0.53702,-0.02132,-0.00188],"force_p95":0.13644,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12306,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51328,-0.00892,0.26308]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16311.0,"contact_point_centroid":[0.56428,0.12595,0.24715],"force_p95":0.08478,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13734,"mean_force":0.05967,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.56193,0.10695,0.24692]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17155.0,"contact_point_centroid":[0.56482,0.0876,0.24835],"force_p95":0.08128,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13307,"mean_force":0.05637,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.56176,0.10653,0.24695]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4108.0,"contact_point_centroid":[0.52396,-0.00163,0.04087],"force_p95":0.07712,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12599,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52317,-0.02084,0.03813]},{"body_a":"world","body_b":"grasp_target","contact_count":2192.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.529,-0.01963,0.13668]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12111.0,"contact_point_centroid":[0.52986,-0.00819,0.24459],"force_p95":0.07748,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10826,"mean_force":0.05414,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52868,0.01091,0.24236]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12882.0,"contact_point_centroid":[0.52966,0.02961,0.24401],"force_p95":0.07439,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09777,"mean_force":0.05121,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52853,0.01058,0.24208]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4900.0,"contact_point_centroid":[0.52397,-0.03992,0.03994],"force_p95":0.06918,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08899,"mean_force":0.04469,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52318,-0.02084,0.03813]}],"total_contact_groups":12},"final_pose_error":0.06387,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.58889,0.16879,0.21321],"final_tcp_position":[0.58547,0.16898,0.24009],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.48807,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":285.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1136.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52884,-0.01833,0.22711],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20128,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":548.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2192.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53162,-0.02099,0.048],"tcp_start":[0.52884,-0.01833,0.22711],"tcp_to_object_dist_end":0.02264,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53692,-0.02078,0.02582],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31643,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13388,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10808.0,"raw_peak_contact_force":0.16836,"subtask_id":"grasp_1","tcp_end":[0.52314,-0.02084,0.0381],"tcp_start":[0.53162,-0.02099,0.048],"tcp_to_object_dist_end":0.01845,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":678.0,"n_steps_budget":1000.0,"object_pos_end":[0.52878,-0.02072,0.20825],"object_pos_start":[0.53692,-0.02078,0.02582],"object_to_goal_dist_end":0.26151,"object_to_goal_dist_start":0.31643,"object_z_max":0.20799,"peak_contact_force":0.08024,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26080.0,"raw_peak_contact_force":0.48807,"tcp_end":[0.52002,-0.02076,0.22594],"tcp_start":[0.52314,-0.02084,0.0381],"tcp_to_object_dist_end":0.01974,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":679.0,"n_steps_budget":1000.0,"object_pos_end":[0.54332,0.03742,0.23824],"object_pos_start":[0.52878,-0.02072,0.20825],"object_to_goal_dist_end":0.20412,"object_to_goal_dist_start":0.26151,"object_z_max":0.23821,"peak_contact_force":0.0,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24993.0,"raw_peak_contact_force":0.10826,"subtask_id":"transport_arc","tcp_end":[0.53826,0.03745,0.26022],"tcp_start":[0.52002,-0.02076,0.22594],"tcp_to_object_dist_end":0.02255,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58889,0.16879,0.21321],"object_pos_start":[0.54332,0.03742,0.23824],"object_to_goal_dist_end":0.063,"object_to_goal_dist_start":0.20412,"object_z_max":0.23824,"peak_contact_force":0.10258,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":33466.0,"raw_peak_contact_force":0.13734,"tcp_end":[0.58547,0.16898,0.24009],"tcp_start":[0.53826,0.03745,0.26022],"tcp_to_object_dist_end":0.0271,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```