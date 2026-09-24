## Search State

- **Seed**: 7
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 19 | -0.3651 | 0.30 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 19 | -0.4341 | 0.17 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 20 | -0.3970 | 0.25 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 20 | -0.4756 | 0.15 | ✅ accepted |
| 0 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.2211 | 0.19 | ✅ accepted |

**Proposal policy**: task_score is 0.30 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.365) — your mutation base

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
    offset:
    - 0.0
    - 0.0
    - 0.0
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
  guards:
  - id: grasp_check
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
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
    offset:
    - 0.0
    - 0.0
    - 0.0
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
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: transport_arc
- id: descend_2
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
    descend_2_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    descend_2_tol:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.01
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
    orientation:
      mode: none
  parameters:
    release_duration:
      type: scalar
      range:
      - 0.5
      - 2.0
      default: 1.0
      binds_to:
      - path: duration.max_time
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: release_1
- id: retract_1
  type: retract
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
    tolerance: 0.01
    orientation:
      mode: keep_current
      tolerance: 0.1
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
    retract_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.07
      binds_to:
      - path: generator.speed
        mode: replace
    retract_tol:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0

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
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]
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
  - guards:
    - id=grasp_check, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=1, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
    - lift_tol: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=object_lift_check, when=after_phase, predicate=object_lifted, on_failure=abort, threshold=0.0
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - transport_altitude: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_tol: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=transport_grasp_guard, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=1, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - descend_2_speed: status=consumed; consumers=generator.speed (replace)
    - descend_2_tol: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, -0.01]
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings:
    - release_duration: status=consumed; consumers=duration.max_time (replace)
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current, tolerance=0.1
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - retract_speed: status=consumed; consumers=generator.speed (replace)
    - retract_tol: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: -0.365
- **task_score** (E): 0.304
- **fitness_score**: 0.635  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 1.000

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0771 |
| descend_1 | 1.00 | 1.00 | 0.1988 |
| grasp_1 | 0.00 | 1.00 | 0.0000 |
| lift_1 | 1.00 | 1.00 | 0.1578 |
| transport_arc | 0.00 | 1.00 | 0.0428 |
| descend_2 | 0.67 | 1.00 | 0.1247 |
| release_1 | 1.00 | 1.00 | 0.0220 |
| retract_1 | 0.33 | 1.00 | 0.1310 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.019, 0.234) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.019, 0.234)→(0.506, 0.022, 0.036) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 0.00 / guard_failure | (0.501, 0.022, 0.030)→(0.501, 0.022, 0.030) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.274 | 1.00 / 44.000 | 0.144 | 0.207 |
| lift_1 | lift | 1.00 / step_budget | (0.501, 0.022, 0.030)→(0.497, 0.021, 0.188) | (0.511, 0.022, 0.026)→(0.509, 0.021, 0.179) | 0.274→0.219 | 1.00 / 34.333 | 0.085 | 0.616 |
| transport_arc | approach | 0.00 / guard_failure | (0.499, 0.028, 0.193)→(0.526, 0.059, 0.206) | (0.509, 0.021, 0.179)→(0.535, 0.057, 0.192) | 0.219→0.180 | 1.00 / 35.667 | 0.024 | 0.123 |
| descend_2 | descend | 0.67 / step_budget | (0.526, 0.059, 0.206)→(0.580, 0.155, 0.182) | (0.535, 0.059, 0.193)→(0.582, 0.155, 0.160) | 0.178→0.072 | 1.00 / 32.333 | 0.090 | 0.142 |
| release_1 | release | 1.00 / step_budget | (0.580, 0.155, 0.182)→(0.574, 0.154, 0.203) | (0.582, 0.155, 0.160)→(0.574, 0.160, 0.022) | 0.072→0.186 | 1.00 / 4.000 | 0.126 | 1.438 |
| retract_1 | retract | 0.33 / step_budget | (0.574, 0.154, 0.203)→(0.572, 0.153, 0.334) | (0.574, 0.160, 0.022)→(0.571, 0.160, 0.023) | 0.186→0.186 | 1.00 / 4.000 | 27.129 | 0.144 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.443
- phase_score: 0.390
- phase_breakdown.approach_1_score: 0.025
- phase_breakdown.transport_arc_score: 0.131
- phase_breakdown.release_1_score: 0.632
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.721
- grasp_place_fitness: 0.705

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.705
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.443
- **Median Q (composite search score)**: -0.394
- **K-run variance**: 0.0025
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.308


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26378,"average_solve_count":254.0,"average_success_count":254.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17771,"approach_1.approach_tol":0.01584,"approach_1.speed":0.13976,"descend_1.descend_speed":0.12977,"descend_1.descend_tol":0.02163,"descend_1.grasp_z_offset":2e-05,"descend_2.descend_2_speed":0.0869,"descend_2.descend_2_tol":0.02398,"grasp_1.grasp_duration":0.6303,"lift_1.lift_height":0.17389,"lift_1.lift_speed":0.01894,"lift_1.lift_tol":0.02323,"release_1.release_duration":1.48572,"retract_1.retract_height":0.34331,"retract_1.retract_speed":0.06786,"retract_1.retract_tol":0.02715,"transport_arc.transport_altitude":0.10529,"transport_arc.transport_speed":0.14296,"transport_arc.transport_tol":0.0134},"optimized_scores":{"best_composite_score":-0.29528,"best_fitness_score":0.70472,"best_task_score":0.44309},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":290.0,"contact_point_centroid":[0.60125,0.16655,-0.00456],"force_p95":0.95935,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.17757,"mean_force":0.24847,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61318,0.16571,0.15072]},{"body_a":"world","body_b":"grasp_target","contact_count":102.0,"contact_point_centroid":[0.50859,0.03821,-0.00159],"force_p95":0.51751,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53774,"mean_force":0.23015,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50129,0.03842,0.02979]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11160.0,"contact_point_centroid":[0.49896,0.05736,0.10628],"force_p95":0.07493,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25964,"mean_force":0.05152,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49877,0.03821,0.10444]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11160.0,"contact_point_centroid":[0.49899,0.01907,0.10639],"force_p95":0.07358,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23213,"mean_force":0.05092,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49877,0.03821,0.10444]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.51254,0.03945,-0.00213],"force_p95":0.15332,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22394,"mean_force":0.13242,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50296,0.03856,0.02941]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1234.0,"contact_point_centroid":[0.61791,0.18636,0.13971],"force_p95":0.07085,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21394,"mean_force":0.04335,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61762,0.16714,0.13808]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1217.0,"contact_point_centroid":[0.61793,0.14798,0.14024],"force_p95":0.06939,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18815,"mean_force":0.04265,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61765,0.16715,0.13812]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.60094,0.16655,-0.00198],"force_p95":0.12448,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15218,"mean_force":0.12255,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.60993,0.1647,0.21413]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8920.0,"contact_point_centroid":[0.59867,0.16517,0.17769],"force_p95":0.07106,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14007,"mean_force":0.05018,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59841,0.14601,0.17599]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8920.0,"contact_point_centroid":[0.59867,0.12689,0.17805],"force_p95":0.07049,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13954,"mean_force":0.04983,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.59841,0.14601,0.17599]},{"body_a":"world","body_b":"grasp_target","contact_count":1184.0,"contact_point_centroid":[0.51251,0.03972,-0.00189],"force_p95":0.13638,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12304,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50288,0.01651,0.25709]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5786.0,"contact_point_centroid":[0.5027,0.01936,0.03086],"force_p95":0.07202,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1242,"mean_force":0.04497,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50251,0.03853,0.02891]},{"body_a":"world","body_b":"grasp_target","contact_count":2164.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50632,0.0365,0.1234]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.53918,0.06369,0.20157],"force_p95":0.07076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10002,"mean_force":0.04873,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53893,0.08282,0.19959]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20000.0,"contact_point_centroid":[0.53914,0.10197,0.20137],"force_p95":0.07165,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09703,"mean_force":0.04903,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53893,0.08282,0.19959]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5976.0,"contact_point_centroid":[0.50268,0.05777,0.03077],"force_p95":0.07247,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08596,"mean_force":0.0451,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50251,0.03853,0.02892]}],"total_contact_groups":16},"final_pose_error":0.23478,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60093,0.16655,0.02602],"final_tcp_position":[0.61044,0.1648,0.27003],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":81.14225,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":297.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1184.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50766,0.03426,0.2142],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18832,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":541.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2164.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.5075,0.03893,0.03447],"tcp_start":[0.50766,0.03426,0.2142],"tcp_to_object_dist_end":0.00985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51241,0.03866,0.02561],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21317,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14748,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13566.0,"raw_peak_contact_force":0.22394,"subtask_id":"grasp_1","tcp_end":[0.50248,0.03852,0.02889],"tcp_start":[0.50249,0.03852,0.02889],"tcp_to_object_dist_end":0.01045,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":558.0,"n_steps_budget":1000.0,"object_pos_end":[0.50729,0.03827,0.17724],"object_pos_start":[0.51241,0.03865,0.02563],"object_to_goal_dist_end":0.18311,"object_to_goal_dist_start":0.21316,"object_z_max":0.17697,"peak_contact_force":0.07404,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22422.0,"raw_peak_contact_force":0.53774,"tcp_end":[0.49903,0.03823,0.18314],"tcp_start":[0.50248,0.03852,0.02889],"tcp_to_object_dist_end":0.01014,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57959,0.12309,0.20216],"object_pos_start":[0.50729,0.03827,0.17724],"object_to_goal_dist_end":0.0895,"object_to_goal_dist_start":0.18311,"object_z_max":0.20213,"peak_contact_force":0.07321,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40000.0,"raw_peak_contact_force":0.10002,"subtask_id":"transport_arc","tcp_end":[0.57781,0.12311,0.21862],"tcp_start":[0.49903,0.03823,0.18314],"tcp_to_object_dist_end":0.01655,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":446.0,"n_steps_budget":1000.0,"object_pos_end":[0.62123,0.16741,0.12414],"object_pos_start":[0.57959,0.12309,0.20216],"object_to_goal_dist_end":0.02242,"object_to_goal_dist_start":0.0895,"object_z_max":0.20216,"peak_contact_force":0.07074,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":17840.0,"raw_peak_contact_force":0.14007,"tcp_end":[0.61953,0.16755,0.14184],"tcp_start":[0.57781,0.12311,0.21862],"tcp_to_object_dist_end":0.01778,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60227,0.16627,0.02654],"object_pos_start":[0.62123,0.16741,0.12414],"object_to_goal_dist_end":0.12131,"object_to_goal_dist_start":0.02242,"object_z_max":0.12414,"peak_contact_force":0.12809,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2741.0,"raw_peak_contact_force":1.17757,"subtask_id":"release_1","tcp_end":[0.61309,0.16569,0.16148],"tcp_start":[0.61953,0.16755,0.14184],"tcp_to_object_dist_end":0.13537,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60093,0.16655,0.02602],"object_pos_start":[0.60227,0.16627,0.02654],"object_to_goal_dist_end":0.1221,"object_to_goal_dist_start":0.12131,"object_z_max":0.02663,"peak_contact_force":81.14225,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.15218,"tcp_end":[0.61044,0.1648,0.27003],"tcp_start":[0.61309,0.16569,0.16148],"tcp_to_object_dist_end":0.2442,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54054,"average_solve_count":259.0,"average_success_count":259.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.21341,"approach_1.approach_tol":0.03337,"approach_1.speed":0.1318,"descend_1.descend_speed":0.09046,"descend_1.descend_tol":0.01929,"descend_1.grasp_z_offset":0.00012,"descend_2.descend_2_speed":0.16913,"descend_2.descend_2_tol":0.04182,"grasp_1.grasp_duration":0.62096,"lift_1.lift_height":0.20552,"lift_1.lift_speed":0.01314,"lift_1.lift_tol":0.03876,"release_1.release_duration":1.47316,"retract_1.retract_height":0.2382,"retract_1.retract_speed":0.12366,"retract_1.retract_tol":0.02922,"transport_arc.transport_altitude":0.22147,"transport_arc.transport_speed":0.08333,"transport_arc.transport_tol":0.0116},"optimized_scores":{"best_composite_score":-0.39356,"best_fitness_score":0.60644,"best_task_score":0.24515},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":188.0,"contact_point_centroid":[0.54274,0.19522,-0.00796],"force_p95":1.25301,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.61627,"mean_force":0.39983,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55536,0.19625,0.23721]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.47857,0.04661,-0.00159],"force_p95":0.5395,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56405,"mean_force":0.23457,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47251,0.04718,0.03088]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12640.0,"contact_point_centroid":[0.47033,0.0661,0.1234],"force_p95":0.07471,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28036,"mean_force":0.05125,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47015,0.04695,0.12157]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12640.0,"contact_point_centroid":[0.47036,0.02781,0.12353],"force_p95":0.07363,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24798,"mean_force":0.05061,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47015,0.04695,0.12157]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.48274,0.04844,-0.00216],"force_p95":0.15973,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23481,"mean_force":0.13439,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47404,0.04735,0.03033]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1287.0,"contact_point_centroid":[0.55895,0.21693,0.22164],"force_p95":0.07053,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16976,"mean_force":0.04213,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55851,0.19766,0.21973]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.54269,0.19525,-0.00198],"force_p95":0.12494,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15509,"mean_force":0.12153,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55373,0.19551,0.3369]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1222.0,"contact_point_centroid":[0.55845,0.17849,0.22214],"force_p95":0.07168,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14811,"mean_force":0.04251,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55851,0.19766,0.21974]},{"body_a":"world","body_b":"grasp_target","contact_count":896.0,"contact_point_centroid":[0.4827,0.04873,-0.00185],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12317,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49107,0.019,0.27398]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5781.0,"contact_point_centroid":[0.4738,0.02813,0.03183],"force_p95":0.07313,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13144,"mean_force":0.04497,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47361,0.0473,0.02989]},{"body_a":"world","body_b":"grasp_target","contact_count":2700.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47944,0.04382,0.14025]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19773.0,"contact_point_centroid":[0.52104,0.11767,0.22585],"force_p95":0.07263,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11456,"mean_force":0.04918,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.52104,0.13683,0.22366]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20616.0,"contact_point_centroid":[0.51982,0.15373,0.22564],"force_p95":0.07066,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10553,"mean_force":0.04775,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.51964,0.13462,0.2237]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3440.0,"contact_point_centroid":[0.47314,0.03532,0.22398],"force_p95":0.07287,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09697,"mean_force":0.04945,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.47291,0.05442,0.222]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3442.0,"contact_point_centroid":[0.47311,0.07359,0.2238],"force_p95":0.07242,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08908,"mean_force":0.0495,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.47291,0.05443,0.222]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6000.0,"contact_point_centroid":[0.47378,0.06656,0.03175],"force_p95":0.07368,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08594,"mean_force":0.04505,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47361,0.0473,0.02989]}],"total_contact_groups":16},"final_pose_error":0.04434,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.54269,0.19525,0.02602],"final_tcp_position":[0.55493,0.19582,0.43829],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.61627,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":225.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":896.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48284,0.04006,0.24798],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22213,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":675.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2700.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47837,0.04777,0.03486],"tcp_start":[0.48284,0.04006,0.24798],"tcp_to_object_dist_end":0.00989,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.04749,0.02553],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29113,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15246,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13585.0,"raw_peak_contact_force":0.23481,"subtask_id":"grasp_1","tcp_end":[0.47359,0.0473,0.02987],"tcp_start":[0.47359,0.0473,0.02987],"tcp_to_object_dist_end":0.01001,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":632.0,"n_steps_budget":1000.0,"object_pos_end":[0.47789,0.04703,0.20858],"object_pos_start":[0.48261,0.04747,0.02555],"object_to_goal_dist_end":0.2106,"object_to_goal_dist_start":0.29112,"object_z_max":0.2083,"peak_contact_force":0.07354,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25372.0,"raw_peak_contact_force":0.56405,"tcp_end":[0.47053,0.04699,0.21565],"tcp_start":[0.47359,0.0473,0.02987],"tcp_to_object_dist_end":0.0102,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":172.0,"n_steps_budget":1000.0,"object_pos_end":[0.48466,0.05927,0.21882],"object_pos_start":[0.47789,0.04703,0.20858],"object_to_goal_dist_end":0.19582,"object_to_goal_dist_start":0.2106,"object_z_max":0.22031,"peak_contact_force":0.0,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6882.0,"raw_peak_contact_force":0.09697,"subtask_id":"transport_arc","tcp_end":[0.47594,0.0619,0.229],"tcp_start":[0.47506,0.05922,0.22694],"tcp_to_object_dist_end":0.01366,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55922,0.19777,0.2026],"object_pos_start":[0.4853,0.06193,0.22038],"object_to_goal_dist_end":0.04751,"object_to_goal_dist_start":0.19311,"object_z_max":0.22038,"peak_contact_force":0.07185,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":40389.0,"raw_peak_contact_force":0.11456,"tcp_end":[0.55996,0.19788,0.22288],"tcp_start":[0.47594,0.0619,0.229],"tcp_to_object_dist_end":0.02029,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54988,0.19533,0.02149],"object_pos_start":[0.55922,0.19777,0.2026],"object_to_goal_dist_end":0.21407,"object_to_goal_dist_start":0.04751,"object_z_max":0.2026,"peak_contact_force":0.13218,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2697.0,"raw_peak_contact_force":1.61627,"subtask_id":"release_1","tcp_end":[0.55532,0.19624,0.24444],"tcp_start":[0.55996,0.19788,0.22288],"tcp_to_object_dist_end":0.22301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54269,0.19525,0.02602],"object_pos_start":[0.54988,0.19533,0.02149],"object_to_goal_dist_end":0.21088,"object_to_goal_dist_start":0.21407,"object_z_max":0.02697,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.15509,"tcp_end":[0.55493,0.19582,0.43829],"tcp_start":[0.55532,0.19624,0.24444],"tcp_to_object_dist_end":0.41246,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70621,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.20691,"approach_1.approach_tol":0.03114,"approach_1.speed":0.07792,"descend_1.descend_speed":0.0775,"descend_1.descend_tol":0.00979,"descend_1.grasp_z_offset":0.00293,"descend_2.descend_2_speed":0.08336,"descend_2.descend_2_tol":0.03703,"grasp_1.grasp_duration":2.33366,"lift_1.lift_height":0.15267,"lift_1.lift_speed":0.14952,"lift_1.lift_tol":0.03233,"release_1.release_duration":0.9877,"retract_1.retract_height":0.25365,"retract_1.retract_speed":0.05572,"retract_1.retract_tol":0.02925,"transport_arc.transport_altitude":0.19753,"transport_arc.transport_speed":0.06106,"transport_arc.transport_tol":0.04045},"optimized_scores":{"best_composite_score":-0.40649,"best_fitness_score":0.59351,"best_task_score":0.22472},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":306.0,"contact_point_centroid":[0.56877,0.11891,-0.00526],"force_p95":0.91788,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.52002,"mean_force":0.25805,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5544,0.09989,0.19139]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.53445,-0.02083,-0.00137],"force_p95":0.56526,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74754,"mean_force":0.15134,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52511,-0.02088,0.03237]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6868.0,"contact_point_centroid":[0.52419,-0.00178,0.09193],"force_p95":0.10295,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36426,"mean_force":0.06278,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52268,-0.02083,0.08969]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7251.0,"contact_point_centroid":[0.52417,-0.03983,0.09071],"force_p95":0.10244,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36294,"mean_force":0.06011,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52266,-0.02083,0.08892]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":261.0,"contact_point_centroid":[0.56363,0.08283,0.17298],"force_p95":0.2031,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23524,"mean_force":0.15526,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55866,0.10083,0.17805]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1281.0,"contact_point_centroid":[0.52802,-0.03371,0.16817],"force_p95":0.10675,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17062,"mean_force":0.08209,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52268,-0.01524,0.16655]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10940.0,"contact_point_centroid":[0.5441,0.02777,0.17167],"force_p95":0.12927,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16994,"mean_force":0.08379,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.53972,0.04626,0.17233]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11379.0,"contact_point_centroid":[0.54465,0.06485,0.17159],"force_p95":0.12539,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16729,"mean_force":0.08107,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.53977,0.04643,0.17234]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":424.0,"contact_point_centroid":[0.56356,0.11828,0.17281],"force_p95":0.13182,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16523,"mean_force":0.09201,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55842,0.10077,0.17763]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53702,-0.02122,-0.00205],"force_p95":0.13433,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1636,"mean_force":0.12648,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5269,-0.02092,0.0317]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1098.0,"contact_point_centroid":[0.52778,0.00328,0.16879],"force_p95":0.1171,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14143,"mean_force":0.09163,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52268,-0.01539,0.16649]},{"body_a":"world","body_b":"grasp_target","contact_count":1032.0,"contact_point_centroid":[0.53702,-0.02132,-0.00187],"force_p95":0.13668,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1231,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51306,-0.00881,0.26954]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.56946,0.11891,-0.00198],"force_p95":0.12291,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12616,"mean_force":0.1226,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55145,0.09932,0.24748]},{"body_a":"world","body_b":"grasp_target","contact_count":2508.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52867,-0.01949,0.13761]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5832.0,"contact_point_centroid":[0.52661,-0.00173,0.03307],"force_p95":0.06868,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10407,"mean_force":0.04496,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52643,-0.02091,0.03116]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5896.0,"contact_point_centroid":[0.52663,-0.04011,0.03304],"force_p95":0.0689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0891,"mean_force":0.04506,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52643,-0.02091,0.03116]}],"total_contact_groups":16},"final_pose_error":0.16307,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.56946,0.11891,0.01602],"final_tcp_position":[0.5518,0.09936,0.29333],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.52002,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":259.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1032.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52837,-0.01805,0.24035],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":627.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2508.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53161,-0.021,0.03724],"tcp_start":[0.52837,-0.01805,0.24035],"tcp_to_object_dist_end":0.01246,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53691,-0.02096,0.02584],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31656,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13284,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13532.0,"raw_peak_contact_force":0.1636,"subtask_id":"grasp_1","tcp_end":[0.52641,-0.0209,0.03114],"tcp_start":[0.52641,-0.0209,0.03114],"tcp_to_object_dist_end":0.01176,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":411.0,"n_steps_budget":660.0,"object_pos_end":[0.54069,-0.02084,0.15266],"object_pos_start":[0.53691,-0.02095,0.02585],"object_to_goal_dist_end":0.2639,"object_to_goal_dist_start":0.31655,"object_z_max":0.15241,"peak_contact_force":0.10712,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14196.0,"raw_peak_contact_force":0.74754,"tcp_end":[0.52286,-0.02082,0.1644],"tcp_start":[0.52641,-0.0209,0.03114],"tcp_to_object_dist_end":0.02134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":103.0,"n_steps_budget":1000.0,"object_pos_end":[0.53942,-0.01173,0.15419],"object_pos_start":[0.54069,-0.02084,0.15266],"object_to_goal_dist_end":0.25537,"object_to_goal_dist_start":0.2639,"object_z_max":0.1554,"peak_contact_force":0.0,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2379.0,"raw_peak_contact_force":0.17062,"subtask_id":"transport_arc","tcp_end":[0.52297,-0.00865,0.16963],"tcp_start":[0.5228,-0.01207,0.16798],"tcp_to_object_dist_end":0.02277,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56479,0.101,0.15407],"object_pos_start":[0.53939,-0.00841,0.15547],"object_to_goal_dist_end":0.14486,"object_to_goal_dist_start":0.25199,"object_z_max":0.15548,"peak_contact_force":0.12708,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":22319.0,"raw_peak_contact_force":0.16994,"tcp_end":[0.55985,0.10085,0.18017],"tcp_start":[0.52297,-0.00865,0.16963],"tcp_to_object_dist_end":0.02657,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56948,0.11889,0.01658],"object_pos_start":[0.56479,0.101,0.15407],"object_to_goal_dist_end":0.22346,"object_to_goal_dist_start":0.14486,"object_z_max":0.15407,"peak_contact_force":0.11647,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":991.0,"raw_peak_contact_force":1.52002,"subtask_id":"release_1","tcp_end":[0.55431,0.09988,0.20273],"tcp_start":[0.55985,0.10085,0.18017],"tcp_to_object_dist_end":0.18773,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56946,0.11891,0.01602],"object_pos_start":[0.56948,0.11889,0.01658],"object_to_goal_dist_end":0.22394,"object_to_goal_dist_start":0.22346,"object_z_max":0.01659,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12616,"tcp_end":[0.5518,0.09936,0.29333],"tcp_start":[0.55431,0.09988,0.20273],"tcp_to_object_dist_end":0.27856,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```