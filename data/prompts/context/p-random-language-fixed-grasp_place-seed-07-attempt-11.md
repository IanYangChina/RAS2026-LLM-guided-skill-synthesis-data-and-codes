## Search State

- **Seed**: 7
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 20 | -0.3920 | 0.26 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | pose_tolerance | 16 | -0.1848 | 0.52 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 16 | -0.0176 | 0.85 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 17 | -0.3643 | 0.33 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 17 | -0.1693 | 0.71 | ❌ rejected |

**Proposal policy**: task_score is 0.26 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.392) — your mutation base

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

- **Composite score**: -0.392
- **task_score** (E): 0.260
- **fitness_score**: 0.608  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 1.000

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0972 |
| descend_1 | 1.00 | 1.00 | 0.1744 |
| grasp_1 | 1.00 | 1.00 | 0.0122 |
| lift_1 | 1.00 | 1.00 | 0.1714 |
| transport_arc | 0.00 | 1.00 | 0.0790 |
| place_1 | 0.67 | 1.00 | 0.1312 |
| release_1 | 1.00 | 1.00 | 0.0215 |
| retract_1 | 1.00 | 1.00 | 0.1392 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.020, 0.212) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 5.222 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.020, 0.212)→(0.506, 0.022, 0.038) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.022, 0.038)→(0.497, 0.021, 0.029) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.274 | 1.00 / 43.000 | 0.149 | 0.222 |
| lift_1 | lift | 1.00 / step_budget | (0.497, 0.021, 0.029)→(0.494, 0.021, 0.200) | (0.511, 0.022, 0.026)→(0.507, 0.021, 0.192) | 0.274→0.223 | 1.00 / 33.667 | 0.089 | 0.617 |
| transport_arc | approach | 0.00 / guard_failure | (0.494, 0.021, 0.200)→(0.521, 0.080, 0.245) | (0.507, 0.021, 0.192)→(0.530, 0.083, 0.220) | 0.223→0.166 | 1.00 / 16.333 | 0.020 | 0.213 |
| place_1 | descend | 0.67 / step_budget | (0.521, 0.080, 0.245)→(0.580, 0.177, 0.228) | (0.530, 0.083, 0.220)→(0.556, 0.130, 0.072) | 0.166→0.178 | 1.00 / 18.000 | 0.116 | 1.314 |
| release_1 | release | 1.00 / step_budget | (0.580, 0.177, 0.228)→(0.576, 0.175, 0.249) | (0.556, 0.130, 0.072)→(0.555, 0.116, 0.012) | 0.178→0.213 | 1.00 / 4.000 | 0.145 | 0.742 |
| retract_1 | retract | 1.00 / step_budget | (0.576, 0.175, 0.249)→(0.603, 0.206, 0.378) | (0.555, 0.116, 0.012)→(0.555, 0.115, 0.016) | 0.213→0.209 | 1.00 / 4.000 | 0.123 | 0.140 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.370
- phase_score: 0.271
- phase_breakdown.approach_1_score: 0.029
- phase_breakdown.transport_arc_score: 0.029
- phase_breakdown.release_1_score: 0.143
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.818
- grasp_place_fitness: 0.661

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.661
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.370
- **Median Q (composite search score)**: -0.407
- **K-run variance**: 0.0015
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: descend_1.grasp_z_offset
- **Final σ (mean)**: 0.306


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45876,"average_solve_count":194.0,"average_success_count":194.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17012,"approach_1.approach_tol":0.0216,"approach_1.speed":0.05956,"descend_1.descend_speed":0.1289,"descend_1.descend_tol":0.02564,"descend_1.grasp_z_offset":0.00687,"grasp_1.grasp_duration":1.03028,"lift_1.lift_height":0.18303,"lift_1.lift_speed":0.04744,"lift_1.lift_tol":0.00749,"place_1.place_speed":0.14734,"place_1.place_tol":0.02924,"place_1.place_z_offset":0.07863,"release_1.release_duration":1.75092,"retract_1.retract_height":0.23921,"retract_1.retract_speed":0.16898,"retract_1.retract_tol":0.03576,"transport_arc.transport_altitude":0.17496,"transport_arc.transport_speed":0.1103,"transport_arc.transport_tol":0.02821},"optimized_scores":{"best_composite_score":-0.3386,"best_fitness_score":0.6614,"best_task_score":0.36958},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":120.0,"contact_point_centroid":[0.59671,0.10308,-0.00881],"force_p95":1.41789,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.98045,"mean_force":0.56497,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59448,0.1456,0.22781]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.50841,0.03746,-0.00151],"force_p95":0.54201,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56371,"mean_force":0.20113,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49823,0.03816,0.03346]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11547.0,"contact_point_centroid":[0.49566,0.05707,0.11202],"force_p95":0.07675,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30257,"mean_force":0.05218,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49568,0.03795,0.11003]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10994.0,"contact_point_centroid":[0.49579,0.0188,0.11345],"force_p95":0.07809,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29454,"mean_force":0.05373,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49568,0.03795,0.11096]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51256,0.03945,-0.00213],"force_p95":0.16092,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23626,"mean_force":0.1328,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50051,0.03836,0.03357]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1322.0,"contact_point_centroid":[0.59821,0.12595,0.20717],"force_p95":0.15833,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18854,"mean_force":0.07193,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59733,0.14651,0.20756]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1251.0,"contact_point_centroid":[0.59769,0.16535,0.209],"force_p95":0.08096,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17695,"mean_force":0.03963,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59808,0.14674,0.20878]},{"body_a":"world","body_b":"grasp_target","contact_count":1872.0,"contact_point_centroid":[0.59722,0.10374,-0.00214],"force_p95":0.12404,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17511,"mean_force":0.11876,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.60891,0.15801,0.29839]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16206.0,"contact_point_centroid":[0.55725,0.08441,0.20841],"force_p95":0.09292,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15197,"mean_force":0.06395,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.55567,0.10357,0.20693]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4068.0,"contact_point_centroid":[0.49991,0.01906,0.03509],"force_p95":0.08091,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15166,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49933,0.03826,0.03229]},{"body_a":"world","body_b":"grasp_target","contact_count":1388.0,"contact_point_centroid":[0.51251,0.03972,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50273,0.01661,0.25351]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20663.0,"contact_point_centroid":[0.55856,0.12451,0.20811],"force_p95":0.07638,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13642,"mean_force":0.04772,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.55781,0.1057,0.20715]},{"body_a":"world","body_b":"grasp_target","contact_count":1996.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50632,0.03662,0.12334]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3942.0,"contact_point_centroid":[0.50398,0.02836,0.20289],"force_p95":0.08147,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11773,"mean_force":0.05585,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50288,0.04742,0.20046]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4234.0,"contact_point_centroid":[0.50438,0.06708,0.2027],"force_p95":0.07544,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11658,"mean_force":0.05248,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50334,0.04802,0.2008]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5003.0,"contact_point_centroid":[0.49989,0.05742,0.03411],"force_p95":0.07362,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08249,"mean_force":0.04462,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49934,0.03826,0.0323]}],"total_contact_groups":16},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.59721,0.10375,0.01602],"final_tcp_position":[0.62436,0.17013,0.3647],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.98045,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":348.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1388.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50764,0.03452,0.20692],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18104,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":499.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1996.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50752,0.03893,0.04129],"tcp_start":[0.50764,0.03452,0.20692],"tcp_to_object_dist_end":0.01608,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.03836,0.02555],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21338,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15303,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10871.0,"raw_peak_contact_force":0.23626,"subtask_id":"grasp_1","tcp_end":[0.4993,0.03826,0.03226],"tcp_start":[0.50752,0.03893,0.04129],"tcp_to_object_dist_end":0.01474,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":568.0,"n_steps_budget":1000.0,"object_pos_end":[0.50618,0.0381,0.18465],"object_pos_start":[0.51243,0.03836,0.02555],"object_to_goal_dist_end":0.1854,"object_to_goal_dist_start":0.21338,"object_z_max":0.18438,"peak_contact_force":0.07932,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22629.0,"raw_peak_contact_force":0.56371,"tcp_end":[0.49599,0.03798,0.19569],"tcp_start":[0.4993,0.03826,0.03226],"tcp_to_object_dist_end":0.01502,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":221.0,"n_steps_budget":1000.0,"object_pos_end":[0.52138,0.05515,0.193],"object_pos_start":[0.50618,0.0381,0.18465],"object_to_goal_dist_end":0.16539,"object_to_goal_dist_start":0.1854,"object_z_max":0.19294,"peak_contact_force":0.0,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8176.0,"raw_peak_contact_force":0.11773,"subtask_id":"transport_arc","tcp_end":[0.50974,0.05531,0.20619],"tcp_start":[0.49599,0.03798,0.19569],"tcp_to_object_dist_end":0.01759,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.59969,0.14718,0.18503],"object_pos_start":[0.52138,0.05515,0.193],"object_to_goal_dist_end":0.05495,"object_to_goal_dist_start":0.16539,"object_z_max":0.193,"peak_contact_force":0.10173,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":36869.0,"raw_peak_contact_force":0.15197,"subtask_id":"release_1","tcp_end":[0.59939,0.14693,0.21192],"tcp_start":[0.50974,0.05531,0.20619],"tcp_to_object_dist_end":0.0269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59526,0.10521,0.00356],"object_pos_start":[0.59969,0.14718,0.18503],"object_to_goal_dist_end":0.15996,"object_to_goal_dist_start":0.05495,"object_z_max":0.18503,"peak_contact_force":0.19068,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2693.0,"raw_peak_contact_force":1.98045,"subtask_id":"release_1","tcp_end":[0.59445,0.1456,0.23255],"tcp_start":[0.59939,0.14693,0.21192],"tcp_to_object_dist_end":0.23253,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":468.0,"n_steps_budget":600.0,"object_pos_end":[0.59721,0.10375,0.01602],"object_pos_start":[0.59526,0.10521,0.00356],"object_to_goal_dist_end":0.14931,"object_to_goal_dist_start":0.15996,"object_z_max":0.01668,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1872.0,"raw_peak_contact_force":0.17511,"tcp_end":[0.62436,0.17013,0.3647],"tcp_start":[0.59445,0.1456,0.23255],"tcp_to_object_dist_end":0.35597,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58852,"average_solve_count":209.0,"average_success_count":209.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1483,"approach_1.approach_tol":0.0344,"approach_1.speed":0.0429,"descend_1.descend_speed":0.172,"descend_1.descend_tol":0.03129,"descend_1.grasp_z_offset":0.0,"grasp_1.grasp_duration":2.15828,"lift_1.lift_height":0.15399,"lift_1.lift_speed":0.06296,"lift_1.lift_tol":0.01392,"place_1.place_speed":0.0882,"place_1.place_tol":0.03185,"place_1.place_z_offset":0.07427,"release_1.release_duration":1.75643,"retract_1.retract_height":0.15856,"retract_1.retract_speed":0.09111,"retract_1.retract_tol":0.034,"transport_arc.transport_altitude":0.11161,"transport_arc.transport_speed":0.09016,"transport_arc.transport_tol":0.02849},"optimized_scores":{"best_composite_score":-0.43038,"best_fitness_score":0.56962,"best_task_score":0.17917},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3702.0,"contact_point_centroid":[0.49163,0.11763,-0.00227],"force_p95":0.12421,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92145,"mean_force":0.13578,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.51622,0.13291,0.22639]},{"body_a":"world","body_b":"grasp_target","contact_count":81.0,"contact_point_centroid":[0.47975,0.04658,-0.00151],"force_p95":0.59213,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68354,"mean_force":0.17425,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46908,0.0469,0.02793]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8243.0,"contact_point_centroid":[0.46764,0.06572,0.0901],"force_p95":0.09645,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31923,"mean_force":0.05703,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46658,0.04665,0.0883]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7705.0,"contact_point_centroid":[0.46794,0.02762,0.09232],"force_p95":0.09439,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28138,"mean_force":0.05955,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46659,0.04665,0.09021]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6378.0,"contact_point_centroid":[0.48309,0.08852,0.17951],"force_p95":0.14436,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25824,"mean_force":0.09374,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.47838,0.07011,0.1799]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48276,0.04842,-0.00216],"force_p95":0.16724,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25318,"mean_force":0.13477,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47132,0.04714,0.02772]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6300.0,"contact_point_centroid":[0.48252,0.05035,0.17835],"force_p95":0.14926,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2514,"mean_force":0.09106,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.47751,0.06872,0.17858]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5003.0,"contact_point_centroid":[0.47003,0.02779,0.02963],"force_p95":0.07115,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15131,"mean_force":0.04304,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47019,0.04703,0.02659]},{"body_a":"world","body_b":"grasp_target","contact_count":1636.0,"contact_point_centroid":[0.4827,0.04873,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48986,0.02076,0.24343]},{"body_a":"world","body_b":"grasp_target","contact_count":1736.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4784,0.04537,0.10967]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.49153,0.11767,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.53308,0.1618,0.25091]},{"body_a":"world","body_b":"grasp_target","contact_count":1788.0,"contact_point_centroid":[0.49153,0.11767,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55397,0.19263,0.32042]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5533.0,"contact_point_centroid":[0.46985,0.06638,0.02898],"force_p95":0.07056,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08356,"mean_force":0.04118,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4702,0.04703,0.02659]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3747.0,"contact_point_centroid":[0.51777,0.13466,0.22988],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0164,"mean_force":0.01049,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.51735,0.13463,0.22763]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.53562,0.16254,0.24845],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01099,"mean_force":0.01016,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.53508,0.16251,0.24614]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2.0,"contact_point_centroid":[0.49666,0.10364,0.19403],"force_p95":0.0,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.49222,0.09215,0.20111]}],"total_contact_groups":16},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.49153,0.11767,0.01602],"final_tcp_position":[0.57656,0.22245,0.37109],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":15.4218,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":410.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":15.4218,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1636.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48112,0.04317,0.18624],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16032,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":434.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1736.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47809,0.04781,0.0346],"tcp_start":[0.48112,0.04317,0.18624],"tcp_to_object_dist_end":0.00978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48259,0.04718,0.02546],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29137,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15957,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12336.0,"raw_peak_contact_force":0.25318,"subtask_id":"grasp_1","tcp_end":[0.47016,0.04702,0.02656],"tcp_start":[0.47809,0.04781,0.0346],"tcp_to_object_dist_end":0.01248,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":436.0,"n_steps_budget":1000.0,"object_pos_end":[0.48383,0.0469,0.15494],"object_pos_start":[0.48259,0.04718,0.02546],"object_to_goal_dist_end":0.22006,"object_to_goal_dist_start":0.29137,"object_z_max":0.15466,"peak_contact_force":0.10807,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16029.0,"raw_peak_contact_force":0.68354,"tcp_end":[0.46658,0.04666,0.1609],"tcp_start":[0.47016,0.04702,0.02656],"tcp_to_object_dist_end":0.01825,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":608.0,"n_steps_budget":1000.0,"object_pos_end":[0.5017,0.09747,0.16747],"object_pos_start":[0.48383,0.0469,0.15494],"object_to_goal_dist_end":0.16631,"object_to_goal_dist_start":0.22006,"object_z_max":0.17634,"peak_contact_force":0.04857,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12678.0,"raw_peak_contact_force":0.25824,"subtask_id":"transport_arc","tcp_end":[0.49222,0.09215,0.20111],"tcp_start":[0.46658,0.04666,0.1609],"tcp_to_object_dist_end":0.03535,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49153,0.11767,0.01602],"object_pos_start":[0.5017,0.09747,0.16747],"object_to_goal_dist_end":0.25791,"object_to_goal_dist_start":0.16631,"object_z_max":0.16747,"peak_contact_force":0.12263,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7451.0,"raw_peak_contact_force":1.92145,"subtask_id":"release_1","tcp_end":[0.53608,0.16271,0.24844],"tcp_start":[0.49222,0.09215,0.20111],"tcp_to_object_dist_end":0.2409,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49153,0.11767,0.01602],"object_pos_start":[0.49153,0.11767,0.01602],"object_to_goal_dist_end":0.25791,"object_to_goal_dist_start":0.25791,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.53197,0.16139,0.27123],"tcp_start":[0.53608,0.16271,0.24844],"tcp_to_object_dist_end":0.26207,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":447.0,"n_steps_budget":990.0,"object_pos_end":[0.49153,0.11767,0.01602],"object_pos_start":[0.49153,0.11767,0.01602],"object_to_goal_dist_end":0.25791,"object_to_goal_dist_start":0.25791,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1788.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57656,0.22245,0.37109],"tcp_start":[0.53197,0.16139,0.27123],"tcp_to_object_dist_end":0.37984,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23214,"average_solve_count":336.0,"average_success_count":336.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.20916,"approach_1.approach_tol":0.01958,"approach_1.speed":0.14288,"descend_1.descend_speed":0.05683,"descend_1.descend_tol":0.04045,"descend_1.grasp_z_offset":0.00234,"grasp_1.grasp_duration":1.69224,"lift_1.lift_height":0.23603,"lift_1.lift_speed":0.01377,"lift_1.lift_tol":0.00777,"place_1.place_speed":0.05887,"place_1.place_tol":0.02307,"place_1.place_z_offset":0.02062,"release_1.release_duration":1.24598,"retract_1.retract_height":0.20947,"retract_1.retract_speed":0.09077,"retract_1.retract_tol":0.03713,"transport_arc.transport_altitude":0.23173,"transport_arc.transport_speed":0.19072,"transport_arc.transport_tol":0.02645},"optimized_scores":{"best_composite_score":-0.40701,"best_fitness_score":0.59299,"best_task_score":0.23043},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2994.0,"contact_point_centroid":[0.57691,0.12421,-0.00252],"force_p95":0.12736,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.86929,"mean_force":0.1428,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.58567,0.16867,0.26271]},{"body_a":"world","body_b":"grasp_target","contact_count":91.0,"contact_point_centroid":[0.53251,-0.02059,-0.00145],"force_p95":0.5677,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60279,"mean_force":0.22777,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52182,-0.02083,0.02777]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14521.0,"contact_point_centroid":[0.51977,-0.00164,0.13481],"force_p95":0.07867,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28925,"mean_force":0.0554,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51928,-0.02076,0.13231]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15345.0,"contact_point_centroid":[0.51974,-0.03983,0.13279],"force_p95":0.07658,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27617,"mean_force":0.05303,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51927,-0.02076,0.13066]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11267.0,"contact_point_centroid":[0.53873,0.01049,0.27736],"force_p95":0.14311,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26282,"mean_force":0.07938,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53583,0.0294,0.27696]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13875.0,"contact_point_centroid":[0.53969,0.05037,0.27898],"force_p95":0.11407,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24,"mean_force":0.06496,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5367,0.03181,0.27878]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":102.0,"contact_point_centroid":[0.56453,0.1092,0.32067],"force_p95":0.15382,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18804,"mean_force":0.05292,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.55987,0.09416,0.32572]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02113,-0.00204],"force_p95":0.13627,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17565,"mean_force":0.12649,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52422,-0.02087,0.02824]},{"body_a":"world","body_b":"grasp_target","contact_count":1004.0,"contact_point_centroid":[0.53702,-0.02132,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51303,-0.00876,0.27065]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3.0,"contact_point_centroid":[0.56711,0.07899,0.31915],"force_p95":0.12728,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12747,"mean_force":0.11678,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.55961,0.0934,0.32651]},{"body_a":"world","body_b":"grasp_target","contact_count":2688.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52865,-0.01945,0.13839]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57687,0.12418,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60158,0.21934,0.22369]},{"body_a":"world","body_b":"grasp_target","contact_count":2500.0,"contact_point_centroid":[0.57687,0.12418,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.6037,0.22234,0.31953]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4100.0,"contact_point_centroid":[0.52384,-0.00164,0.02957],"force_p95":0.07702,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11657,"mean_force":0.05179,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52299,-0.02085,0.02684]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4904.0,"contact_point_centroid":[0.52384,-0.03993,0.02865],"force_p95":0.069,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09271,"mean_force":0.04477,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52299,-0.02085,0.02684]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3071.0,"contact_point_centroid":[0.58708,0.17093,0.26323],"force_p95":0.01116,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01627,"mean_force":0.01055,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.5865,0.17092,0.26101]}],"total_contact_groups":17},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.57687,0.12418,0.01602],"final_tcp_position":[0.6092,0.22669,0.39712],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.86929,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":252.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1004.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52825,-0.01797,0.2425],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21668,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":672.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2688.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53157,-0.021,0.03667],"tcp_start":[0.52825,-0.01797,0.2425],"tcp_to_object_dist_end":0.01197,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53689,-0.02073,0.02584],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31639,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13321,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10804.0,"raw_peak_contact_force":0.17565,"subtask_id":"grasp_1","tcp_end":[0.52296,-0.02084,0.02681],"tcp_start":[0.53157,-0.021,0.03667],"tcp_to_object_dist_end":0.01396,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":784.0,"n_steps_budget":1000.0,"object_pos_end":[0.5312,-0.02074,0.23521],"object_pos_start":[0.53689,-0.02073,0.02584],"object_to_goal_dist_end":0.26226,"object_to_goal_dist_start":0.31639,"object_z_max":0.23495,"peak_contact_force":0.08103,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29957.0,"raw_peak_contact_force":0.60279,"tcp_end":[0.52,-0.02077,0.2432],"tcp_start":[0.52296,-0.02084,0.02681],"tcp_to_object_dist_end":0.01376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":927.0,"n_steps_budget":1000.0,"object_pos_end":[0.5667,0.09548,0.29986],"object_pos_start":[0.5312,-0.02074,0.23521],"object_to_goal_dist_end":0.16716,"object_to_goal_dist_start":0.26226,"object_z_max":0.30096,"peak_contact_force":0.01017,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25142.0,"raw_peak_contact_force":0.26282,"subtask_id":"transport_arc","tcp_end":[0.55959,0.09337,0.3265],"tcp_start":[0.52,-0.02077,0.2432],"tcp_to_object_dist_end":0.02765,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":864.0,"n_steps_budget":1000.0,"object_pos_end":[0.57687,0.12418,0.01602],"object_pos_start":[0.5667,0.09548,0.29986],"object_to_goal_dist_end":0.22017,"object_to_goal_dist_start":0.16716,"object_z_max":0.29986,"peak_contact_force":0.12263,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6170.0,"raw_peak_contact_force":1.86929,"subtask_id":"release_1","tcp_end":[0.60497,0.22057,0.22359],"tcp_start":[0.55959,0.09337,0.3265],"tcp_to_object_dist_end":0.23057,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57687,0.12418,0.01602],"object_pos_start":[0.57687,0.12418,0.01602],"object_to_goal_dist_end":0.22017,"object_to_goal_dist_start":0.22017,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.60038,0.21875,0.24305],"tcp_start":[0.60497,0.22057,0.22359],"tcp_to_object_dist_end":0.24706,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":625.0,"n_steps_budget":1000.0,"object_pos_end":[0.57687,0.12418,0.01602],"object_pos_start":[0.57687,0.12418,0.01602],"object_to_goal_dist_end":0.22017,"object_to_goal_dist_start":0.22017,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2500.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.6092,0.22669,0.39712],"tcp_start":[0.60038,0.21875,0.24305],"tcp_to_object_dist_end":0.39597,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```