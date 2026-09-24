## Search State

- **Seed**: 7
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 17 | -0.3888 | 0.27 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 16 | -0.0055 | 0.89 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 19 | -0.3651 | 0.30 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 19 | -0.4341 | 0.17 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 20 | -0.3970 | 0.25 | ✅ accepted |

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

## Current Skill (Q=-0.389) — your mutation base

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

- **Composite score**: -0.389
- **task_score** (E): 0.270
- **fitness_score**: 0.611  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 1.000

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0454 |
| descend_1 | 1.00 | 1.00 | 0.2483 |
| grasp_1 | 1.00 | 1.00 | 0.0122 |
| lift_1 | 1.00 | 1.00 | 0.1470 |
| transport_arc | 0.00 | 1.00 | 0.1155 |
| place_1 | 0.67 | 1.00 | 0.1202 |
| release_1 | 1.00 | 1.00 | 0.0212 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.019, 0.290) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.507, 0.019, 0.290)→(0.506, 0.022, 0.042) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.022, 0.042)→(0.498, 0.022, 0.033) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.274 | 1.00 / 43.000 | 0.147 | 0.214 |
| lift_1 | lift | 1.00 / step_budget | (0.498, 0.022, 0.033)→(0.494, 0.021, 0.180) | (0.511, 0.022, 0.026)→(0.507, 0.021, 0.168) | 0.274→0.226 | 1.00 / 32.333 | 0.090 | 0.565 |
| transport_arc | approach | 0.00 / step_budget | (0.494, 0.021, 0.180)→(0.539, 0.096, 0.249) | (0.507, 0.021, 0.168)→(0.534, 0.085, 0.156) | 0.226→0.172 | 1.00 / 29.333 | 0.090 | 0.675 |
| place_1 | descend | 0.67 / step_budget | (0.539, 0.096, 0.249)→(0.589, 0.186, 0.217) | (0.534, 0.085, 0.156)→(0.566, 0.163, 0.078) | 0.172→0.145 | 1.00 / 13.667 | 0.169 | 0.782 |
| release_1 | release | 1.00 / step_budget | (0.589, 0.186, 0.217)→(0.584, 0.184, 0.237) | (0.566, 0.163, 0.078)→(0.563, 0.162, 0.016) | 0.145→0.197 | 1.00 / 4.000 | 0.152 | 0.704 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.303
- phase_score: 0.315
- phase_breakdown.approach_1_score: 0.003
- phase_breakdown.transport_arc_score: 0.060
- phase_breakdown.release_1_score: 0.310
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.850
- grasp_place_fitness: 0.627

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.627
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.303
- **Median Q (composite search score)**: -0.390
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.336


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.35,"average_solve_count":200.0,"average_success_count":200.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.29896,"approach_1.approach_tol":0.01139,"approach_1.speed":0.07544,"descend_1.descend_speed":0.05041,"descend_1.descend_tol":0.03164,"descend_1.grasp_z_offset":0.00888,"grasp_1.grasp_duration":2.75555,"lift_1.lift_height":0.13098,"lift_1.lift_speed":0.10632,"lift_1.lift_tol":0.03864,"place_1.place_speed":0.1433,"place_1.place_tol":0.00839,"place_1.place_z_offset":0.04075,"release_1.release_duration":1.05148,"transport_arc.transport_altitude":0.20988,"transport_arc.transport_speed":0.18961,"transport_arc.transport_tol":0.02777},"optimized_scores":{"best_composite_score":-0.37301,"best_fitness_score":0.62699,"best_task_score":0.30348},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2068.0,"contact_point_centroid":[0.54215,0.0828,-0.00248],"force_p95":0.1865,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.84962,"mean_force":0.14411,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54941,0.09545,0.22928]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.50988,0.03793,-0.00145],"force_p95":0.49513,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57083,"mean_force":0.12835,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49829,0.03837,0.03575]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5510.0,"contact_point_centroid":[0.49812,0.01921,0.08677],"force_p95":0.10583,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33112,"mean_force":0.06798,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49586,0.03817,0.08445]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5943.0,"contact_point_centroid":[0.49796,0.0571,0.08395],"force_p95":0.10621,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32004,"mean_force":0.06428,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49587,0.03817,0.08205]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3939.0,"contact_point_centroid":[0.51337,0.03473,0.16587],"force_p95":0.16671,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26302,"mean_force":0.09558,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50782,0.05323,0.16523]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4342.0,"contact_point_centroid":[0.51426,0.0724,0.16674],"force_p95":0.13622,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24469,"mean_force":0.0892,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50857,0.05403,0.16639]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51254,0.03948,-0.00211],"force_p95":0.15404,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22164,"mean_force":0.13101,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50071,0.03858,0.03575]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4078.0,"contact_point_centroid":[0.50003,0.01928,0.03728],"force_p95":0.07998,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1462,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49954,0.03848,0.03447]},{"body_a":"world","body_b":"grasp_target","contact_count":1616.0,"contact_point_centroid":[0.51251,0.03972,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5039,0.01946,0.30953]},{"body_a":"world","body_b":"grasp_target","contact_count":3632.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50743,0.03748,0.18033]},{"body_a":"world","body_b":"grasp_target","contact_count":1904.0,"contact_point_centroid":[0.54212,0.0828,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.59453,0.14214,0.21631]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54212,0.0828,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61577,0.16637,0.18218]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4976.0,"contact_point_centroid":[0.50004,0.05762,0.03629],"force_p95":0.07261,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08349,"mean_force":0.04465,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49954,0.03848,0.03448]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1976.0,"contact_point_centroid":[0.55202,0.09759,0.23477],"force_p95":0.01157,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01618,"mean_force":0.01049,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55154,0.09758,0.23255]},{"body_a":"left_finger","body_b":"right_finger","contact_count":214.0,"contact_point_centroid":[0.61883,0.16729,0.18098],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01036,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6184,0.16726,0.17876]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2052.0,"contact_point_centroid":[0.59498,0.1421,0.21866],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01275,"mean_force":0.01035,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.59447,0.14208,0.2164]}],"total_contact_groups":16},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.54212,0.0828,0.01602],"final_tcp_position":[0.61983,0.16753,0.18198],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.84962,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":405.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1616.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50902,0.03595,0.32043],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.29446,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":908.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3632.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.5077,0.03915,0.04348],"tcp_start":[0.50902,0.03595,0.32043],"tcp_to_object_dist_end":0.01812,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.03856,0.02563],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21321,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14762,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10854.0,"raw_peak_contact_force":0.22164,"subtask_id":"grasp_1","tcp_end":[0.49951,0.03848,0.03444],"tcp_start":[0.5077,0.03915,0.04348],"tcp_to_object_dist_end":0.01564,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":355.0,"n_steps_budget":780.0,"object_pos_end":[0.513,0.03842,0.13277],"object_pos_start":[0.51243,0.03856,0.02563],"object_to_goal_dist_end":0.1768,"object_to_goal_dist_start":0.21321,"object_z_max":0.13251,"peak_contact_force":0.10605,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11529.0,"raw_peak_contact_force":0.57083,"tcp_end":[0.49579,0.03817,0.14604],"tcp_start":[0.49951,0.03848,0.03444],"tcp_to_object_dist_end":0.02173,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54212,0.0828,0.01602],"object_pos_start":[0.513,0.03842,0.13277],"object_to_goal_dist_end":0.17887,"object_to_goal_dist_start":0.1768,"object_z_max":0.16493,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12325.0,"raw_peak_contact_force":1.84962,"subtask_id":"transport_arc","tcp_end":[0.56887,0.11491,0.25908],"tcp_start":[0.49579,0.03817,0.14604],"tcp_to_object_dist_end":0.24662,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":476.0,"n_steps_budget":1000.0,"object_pos_end":[0.54212,0.0828,0.01602],"object_pos_start":[0.54212,0.0828,0.01602],"object_to_goal_dist_end":0.17887,"object_to_goal_dist_start":0.17887,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3956.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.61983,0.16753,0.18198],"tcp_start":[0.56887,0.11491,0.25908],"tcp_to_object_dist_end":0.20189,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54212,0.0828,0.01602],"object_pos_start":[0.54212,0.0828,0.01602],"object_to_goal_dist_end":0.17887,"object_to_goal_dist_start":0.17887,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1014.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61424,0.16585,0.20158],"tcp_start":[0.61983,0.16753,0.18198],"tcp_to_object_dist_end":0.21571,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31288,"average_solve_count":163.0,"average_success_count":163.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.25791,"approach_1.approach_tol":0.01806,"approach_1.speed":0.08891,"descend_1.descend_speed":0.12805,"descend_1.descend_tol":0.0226,"descend_1.grasp_z_offset":0.00084,"grasp_1.grasp_duration":1.32596,"lift_1.lift_height":0.12028,"lift_1.lift_speed":0.05403,"lift_1.lift_tol":0.01915,"place_1.place_speed":0.1177,"place_1.place_tol":0.02761,"place_1.place_z_offset":0.02246,"release_1.release_duration":1.81143,"transport_arc.transport_altitude":0.15726,"transport_arc.transport_speed":0.03992,"transport_arc.transport_tol":0.028},"optimized_scores":{"best_composite_score":-0.4036,"best_fitness_score":0.5964,"best_task_score":0.23234},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":93.0,"contact_point_centroid":[0.55366,0.1961,-0.00919],"force_p95":1.36942,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.07301,"mean_force":0.70581,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.54562,0.17742,0.22281]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.47964,0.04641,-0.00153],"force_p95":0.55401,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65427,"mean_force":0.18469,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46933,0.04689,0.02885]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7115.0,"contact_point_centroid":[0.46683,0.06581,0.07821],"force_p95":0.07682,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31248,"mean_force":0.05097,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46695,0.04666,0.07625]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10314.0,"contact_point_centroid":[0.51693,0.11107,0.20211],"force_p95":0.14799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27523,"mean_force":0.08026,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.51426,0.12988,0.20228]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55169,0.19685,-0.00262],"force_p95":0.12548,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2739,"mean_force":0.11506,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54307,0.17752,0.22548]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6541.0,"contact_point_centroid":[0.46698,0.02747,0.07773],"force_p95":0.08076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27374,"mean_force":0.0539,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46695,0.04666,0.07505]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48276,0.04843,-0.00216],"force_p95":0.16716,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25184,"mean_force":0.13467,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47158,0.04713,0.02874]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12739.0,"contact_point_centroid":[0.51797,0.1495,0.20209],"force_p95":0.12213,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24857,"mean_force":0.06782,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.51497,0.13097,0.20274]},{"body_a":"world","body_b":"grasp_target","contact_count":812.0,"contact_point_centroid":[0.4827,0.04873,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12323,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49101,0.01922,0.29143]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5007.0,"contact_point_centroid":[0.47022,0.02778,0.03042],"force_p95":0.07007,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1273,"mean_force":0.04303,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47045,0.04702,0.0276]},{"body_a":"world","body_b":"grasp_target","contact_count":3024.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47975,0.04348,0.15875]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20196.0,"contact_point_centroid":[0.48057,0.05384,0.16306],"force_p95":0.07337,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09024,"mean_force":0.04928,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.4801,0.07294,0.16139]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19658.0,"contact_point_centroid":[0.4807,0.09236,0.16322],"force_p95":0.07472,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08386,"mean_force":0.05081,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48025,0.07321,0.16174]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5532.0,"contact_point_centroid":[0.47003,0.06637,0.02979],"force_p95":0.0703,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08232,"mean_force":0.04115,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47046,0.04702,0.02761]},{"body_a":"left_finger","body_b":"right_finger","contact_count":115.0,"contact_point_centroid":[0.54541,0.17818,0.22193],"force_p95":0.01495,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01767,"mean_force":0.0117,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5447,0.17815,0.21969]}],"total_contact_groups":15},"final_pose_error":0.06832,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.55169,0.19682,0.01602],"final_tcp_position":[0.54637,0.17857,0.22332],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":2.07301,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":204.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":812.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48333,0.03932,0.28491],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25906,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":756.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3024.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.4783,0.04779,0.03561],"tcp_start":[0.48333,0.03932,0.28491],"tcp_to_object_dist_end":0.01059,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4826,0.04719,0.02546],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29136,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15974,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12339.0,"raw_peak_contact_force":0.25184,"subtask_id":"grasp_1","tcp_end":[0.47042,0.04702,0.02757],"tcp_start":[0.4783,0.04779,0.03561],"tcp_to_object_dist_end":0.01236,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":337.0,"n_steps_budget":1000.0,"object_pos_end":[0.47843,0.04656,0.12351],"object_pos_start":[0.4826,0.04719,0.02546],"object_to_goal_dist_end":0.23532,"object_to_goal_dist_start":0.29136,"object_z_max":0.12322,"peak_contact_force":0.08367,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13740.0,"raw_peak_contact_force":0.65427,"tcp_end":[0.46674,0.04664,0.1282],"tcp_start":[0.47042,0.04702,0.02757],"tcp_to_object_dist_end":0.01259,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50193,0.09436,0.1781],"object_pos_start":[0.47843,0.04656,0.12351],"object_to_goal_dist_end":0.16499,"object_to_goal_dist_start":0.23532,"object_z_max":0.17806,"peak_contact_force":0.06919,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":39854.0,"raw_peak_contact_force":0.09024,"subtask_id":"transport_arc","tcp_end":[0.49375,0.09441,0.19149],"tcp_start":[0.46674,0.04664,0.1282],"tcp_to_object_dist_end":0.01569,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55191,0.19574,-0.00103],"object_pos_start":[0.50193,0.09436,0.1781],"object_to_goal_dist_end":0.23578,"object_to_goal_dist_start":0.16499,"object_z_max":0.19545,"peak_contact_force":0.2976,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":23146.0,"raw_peak_contact_force":2.07301,"tcp_end":[0.54637,0.17857,0.22332],"tcp_start":[0.49375,0.09441,0.19149],"tcp_to_object_dist_end":0.22507,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55169,0.19682,0.01602],"object_pos_start":[0.55191,0.19574,-0.00103],"object_to_goal_dist_end":0.21893,"object_to_goal_dist_start":0.23578,"object_z_max":0.01668,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":915.0,"raw_peak_contact_force":0.2739,"subtask_id":"release_1","tcp_end":[0.54183,0.17703,0.24568],"tcp_start":[0.54637,0.17857,0.22332],"tcp_to_object_dist_end":0.23072,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37226,"average_solve_count":274.0,"average_success_count":274.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.23521,"approach_1.approach_tol":0.02877,"approach_1.speed":0.07548,"descend_1.descend_speed":0.07688,"descend_1.descend_tol":0.04989,"descend_1.grasp_z_offset":0.01258,"grasp_1.grasp_duration":2.07326,"lift_1.lift_height":0.2484,"lift_1.lift_speed":0.01017,"lift_1.lift_tol":0.02926,"place_1.place_speed":0.08548,"place_1.place_tol":0.01351,"place_1.place_z_offset":0.04164,"release_1.release_duration":1.88036,"transport_arc.transport_altitude":0.1512,"transport_arc.transport_speed":0.06765,"transport_arc.transport_tol":0.03272},"optimized_scores":{"best_composite_score":-0.38992,"best_fitness_score":0.61008,"best_task_score":0.27564},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.58563,0.20813,-0.01015],"force_p95":1.55922,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.71538,"mean_force":0.54005,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59722,0.20887,0.25913]},{"body_a":"world","body_b":"grasp_target","contact_count":90.0,"contact_point_centroid":[0.533,-0.02089,-0.00146],"force_p95":0.44963,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47114,"mean_force":0.17981,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52207,-0.02082,0.03788]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15533.0,"contact_point_centroid":[0.52004,-0.00164,0.15047],"force_p95":0.07821,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28176,"mean_force":0.05499,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51963,-0.02076,0.148]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16221.0,"contact_point_centroid":[0.52001,-0.03984,0.14886],"force_p95":0.07679,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26532,"mean_force":0.0532,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51962,-0.02076,0.1467]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02118,-0.00205],"force_p95":0.13652,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16838,"mean_force":0.12651,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52444,-0.02086,0.03834]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":950.0,"contact_point_centroid":[0.60308,0.22914,0.24102],"force_p95":0.08463,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15838,"mean_force":0.0545,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60002,0.2102,0.24161]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":921.0,"contact_point_centroid":[0.60246,0.19126,0.24072],"force_p95":0.08474,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15044,"mean_force":0.05496,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60004,0.21021,0.24166]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16236.0,"contact_point_centroid":[0.57983,0.12822,0.26682],"force_p95":0.08385,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15032,"mean_force":0.05953,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.5776,0.14718,0.26629]},{"body_a":"world","body_b":"grasp_target","contact_count":904.0,"contact_point_centroid":[0.53702,-0.02132,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12317,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51313,-0.00876,0.2815]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16937.0,"contact_point_centroid":[0.58048,0.1657,0.26753],"force_p95":0.08049,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13751,"mean_force":0.05692,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.57745,0.14677,0.26642]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4107.0,"contact_point_centroid":[0.52399,-0.00163,0.03968],"force_p95":0.0771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12527,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52322,-0.02084,0.03694]},{"body_a":"world","body_b":"grasp_target","contact_count":2684.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52853,-0.01928,0.15484]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4900.0,"contact_point_centroid":[0.524,-0.03992,0.03875],"force_p95":0.06917,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08948,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52322,-0.02084,0.03694]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19953.0,"contact_point_centroid":[0.53804,0.05121,0.28073],"force_p95":0.07153,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08559,"mean_force":0.04866,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53707,0.03214,0.27927]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18938.0,"contact_point_centroid":[0.53839,0.01436,0.28137],"force_p95":0.07644,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08524,"mean_force":0.05129,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53756,0.03349,0.27975]}],"total_contact_groups":15},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.59482,0.20727,0.01583],"final_tcp_position":[0.60135,0.2105,0.24531],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.71538,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":227.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":904.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52785,-0.01764,0.26514],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23932,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":671.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2684.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53168,-0.02099,0.04681],"tcp_start":[0.52785,-0.01764,0.26514],"tcp_to_object_dist_end":0.02147,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53692,-0.02077,0.02582],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31642,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13385,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10807.0,"raw_peak_contact_force":0.16838,"subtask_id":"grasp_1","tcp_end":[0.52319,-0.02084,0.0369],"tcp_start":[0.53168,-0.02099,0.04681],"tcp_to_object_dist_end":0.01764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":830.0,"n_steps_budget":1000.0,"object_pos_end":[0.52861,-0.02071,0.24832],"object_pos_start":[0.53692,-0.02077,0.02582],"object_to_goal_dist_end":0.26473,"object_to_goal_dist_start":0.31642,"object_z_max":0.24806,"peak_contact_force":0.07934,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":31844.0,"raw_peak_contact_force":0.47114,"tcp_end":[0.52047,-0.02078,0.26564],"tcp_start":[0.52319,-0.02084,0.0369],"tcp_to_object_dist_end":0.01914,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55726,0.07727,0.27267],"object_pos_start":[0.52861,-0.02071,0.24832],"object_to_goal_dist_end":0.17239,"object_to_goal_dist_start":0.26473,"object_z_max":0.27263,"peak_contact_force":0.07817,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38891.0,"raw_peak_contact_force":0.08559,"subtask_id":"transport_arc","tcp_end":[0.55351,0.07728,0.29546],"tcp_start":[0.52047,-0.02078,0.26564],"tcp_to_object_dist_end":0.0231,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60424,0.21059,0.21782],"object_pos_start":[0.55726,0.07727,0.27267],"object_to_goal_dist_end":0.02098,"object_to_goal_dist_start":0.17239,"object_z_max":0.27267,"peak_contact_force":0.08714,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":33173.0,"raw_peak_contact_force":0.15032,"tcp_end":[0.60135,0.2105,0.24531],"tcp_start":[0.55351,0.07728,0.29546],"tcp_to_object_dist_end":0.02764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59482,0.20727,0.01583],"object_pos_start":[0.60424,0.21059,0.21782],"object_to_goal_dist_end":0.1933,"object_to_goal_dist_start":0.02098,"object_z_max":0.21782,"peak_contact_force":0.21085,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2015.0,"raw_peak_contact_force":1.71538,"subtask_id":"release_1","tcp_end":[0.5972,0.20886,0.26506],"tcp_start":[0.60135,0.2105,0.24531],"tcp_to_object_dist_end":0.24925,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```