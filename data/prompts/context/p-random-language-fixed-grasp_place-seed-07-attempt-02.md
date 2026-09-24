## Search State

- **Seed**: 7
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 20 | -0.3970 | 0.25 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | -0.4756 | 0.15 | ❌ rejected |
| 0 | descend → insert → grasp → approach → align → retract | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2211 | 0.19 | ✅ accepted |

**Proposal policy**: task_score is 0.25 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.397) — your mutation base

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
    tolerance: 0.01
    orientation:
      mode: keep_current
      tolerance: 0.1
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.15
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
      default: 0.01
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
  generator: arc_cartesian
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
    arc_clearance:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    arc_height:
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
      default: 0.06
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
  retries:
    max_attempts: 0
    strategy: repeat
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
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.01
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
    - arc_clearance: status=consumed; consumers=generator.arc_height (replace)
    - arc_height: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_tol: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]
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

- **Composite score**: -0.397
- **task_score** (E): 0.250
- **fitness_score**: 0.603  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 1.000

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0877 |
| descend_1 | 1.00 | 1.00 | 0.1829 |
| grasp_1 | 0.00 | 1.00 | 0.0000 |
| lift_1 | 0.33 | 1.00 | 0.1336 |
| transport_arc | 0.00 | 1.00 | 0.1176 |
| descend_2 | 0.67 | 1.00 | 0.1936 |
| release_1 | 1.00 | 1.00 | 0.0220 |
| retract_1 | 1.00 | 1.00 | 0.1586 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.019, 0.223) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.019, 0.223)→(0.506, 0.022, 0.040) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 0.00 / guard_failure | (0.501, 0.022, 0.035)→(0.501, 0.022, 0.035) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.274 | 1.00 / 44.000 | 0.144 | 0.208 |
| lift_1 | lift | 0.33 / step_budget | (0.501, 0.022, 0.035)→(0.497, 0.021, 0.168) | (0.511, 0.022, 0.026)→(0.505, 0.022, 0.150) | 0.274→0.223 | 1.00 / 33.667 | 0.108 | 0.613 |
| transport_arc | approach | 0.00 / step_budget | (0.497, 0.021, 0.168)→(0.490, 0.009, 0.281) | (0.505, 0.022, 0.150)→(0.494, 0.004, 0.146) | 0.223→0.272 | 1.00 / 20.333 | 3249.645 | 0.839 |
| descend_2 | descend | 0.67 / step_budget | (0.490, 0.009, 0.281)→(0.578, 0.150, 0.197) | (0.494, 0.004, 0.146)→(0.547, 0.094, 0.102) | 0.272→0.167 | 1.00 / 14.667 | 0.124 | 0.230 |
| release_1 | release | 1.00 / step_budget | (0.578, 0.150, 0.197)→(0.572, 0.149, 0.218) | (0.547, 0.094, 0.102)→(0.547, 0.095, 0.019) | 0.167→0.225 | 1.00 / 2.667 | 0.206 | 1.088 |
| retract_1 | retract | 1.00 / step_budget | (0.572, 0.149, 0.218)→(0.571, 0.148, 0.377) | (0.547, 0.095, 0.019)→(0.545, 0.098, 0.019) | 0.225→0.226 | 1.00 / 4.000 | 0.123 | 0.249 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.423
- phase_score: 0.303
- phase_breakdown.approach_1_score: 0.052
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.012
- phase_breakdown.descend_1_score: 0.739
- phase_breakdown.release_1_score: 0.463
- grasp_place_fitness: 0.694

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.694
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.423
- **Median Q (composite search score)**: -0.436
- **K-run variance**: 0.0041
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.326


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18774,"average_solve_count":261.0,"average_success_count":261.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14057,"approach_1.approach_tol":0.01297,"approach_1.speed":0.11229,"descend_1.descend_speed":0.02577,"descend_1.descend_tol":0.03033,"descend_1.grasp_z_offset":0.00129,"descend_2.descend_2_speed":0.19693,"descend_2.descend_2_tol":0.02834,"grasp_1.grasp_duration":2.67398,"lift_1.lift_height":0.27625,"lift_1.lift_speed":0.05989,"lift_1.lift_tol":0.04268,"release_1.release_duration":1.40845,"retract_1.retract_height":0.12071,"retract_1.retract_speed":0.091,"retract_1.retract_tol":0.03299,"transport_arc.arc_clearance":0.1616,"transport_arc.arc_height":0.17992,"transport_arc.transport_speed":0.06675,"transport_arc.transport_tol":0.02056},"optimized_scores":{"best_composite_score":-0.30635,"best_fitness_score":0.69365,"best_task_score":0.4228},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":117.0,"contact_point_centroid":[0.60218,0.16459,-0.00865],"force_p95":1.2989,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.37408,"mean_force":0.60063,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60187,0.15419,0.15604]},{"body_a":"world","body_b":"grasp_target","contact_count":196.0,"contact_point_centroid":[0.50786,0.03758,-0.00122],"force_p95":0.42015,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63966,"mean_force":0.10058,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50052,0.03837,0.03202]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12235.0,"contact_point_centroid":[0.55637,0.07962,0.18528],"force_p95":0.11842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37319,"mean_force":0.08047,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.5519,0.09838,0.18546]},{"body_a":"world","body_b":"grasp_target","contact_count":2972.0,"contact_point_centroid":[0.62844,0.16678,-0.00202],"force_p95":0.1254,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37182,"mean_force":0.1246,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.59866,0.15325,0.21842]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20454.0,"contact_point_centroid":[0.49813,0.05734,0.08156],"force_p95":0.07249,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32038,"mean_force":0.04932,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4981,0.03818,0.07957]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13501.0,"contact_point_centroid":[0.55592,0.11609,0.18626],"force_p95":0.10076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29128,"mean_force":0.07355,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.55112,0.09757,0.18601]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20444.0,"contact_point_centroid":[0.49815,0.01903,0.08167],"force_p95":0.07281,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28747,"mean_force":0.04892,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4981,0.03818,0.07956]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":673.0,"contact_point_centroid":[0.60906,0.17407,0.13883],"force_p95":0.14742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28448,"mean_force":0.0914,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6059,0.15541,0.14254]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":528.0,"contact_point_centroid":[0.61044,0.13721,0.13948],"force_p95":0.13068,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25262,"mean_force":0.08792,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60613,0.15548,0.14287]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.51254,0.03947,-0.00213],"force_p95":0.15303,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22257,"mean_force":0.13228,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50285,0.03857,0.03076]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18407.0,"contact_point_centroid":[0.48568,0.00856,0.17998],"force_p95":0.08269,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13941,"mean_force":0.05382,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48466,0.02758,0.17869]},{"body_a":"world","body_b":"grasp_target","contact_count":1584.0,"contact_point_centroid":[0.51251,0.03972,-0.00191],"force_p95":0.13467,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50283,0.01719,0.23905]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17833.0,"contact_point_centroid":[0.48614,0.04691,0.17995],"force_p95":0.08688,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12858,"mean_force":0.05542,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48493,0.02783,0.17846]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5792.0,"contact_point_centroid":[0.50259,0.01936,0.0322],"force_p95":0.07199,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12534,"mean_force":0.04495,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5024,0.03853,0.03026]},{"body_a":"world","body_b":"grasp_target","contact_count":2004.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50605,0.03705,0.10644]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5976.0,"contact_point_centroid":[0.50257,0.05777,0.03211],"force_p95":0.07244,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0847,"mean_force":0.04507,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5024,0.03853,0.03026]}],"total_contact_groups":16},"final_pose_error":0.01448,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62859,0.16702,0.01602],"final_tcp_position":[0.59918,0.15334,0.27338],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.37408,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":397.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1584.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50772,0.03542,0.1781],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.15221,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":501.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2004.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50737,0.03893,0.0358],"tcp_start":[0.50772,0.03542,0.1781],"tcp_to_object_dist_end":0.01108,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51241,0.03869,0.02562],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21315,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14735,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13572.0,"raw_peak_contact_force":0.22257,"subtask_id":"grasp_1","tcp_end":[0.50237,0.03853,0.03023],"tcp_start":[0.50237,0.03853,0.03024],"tcp_to_object_dist_end":0.01105,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50547,0.0382,0.11723],"object_pos_start":[0.51241,0.03867,0.02564],"object_to_goal_dist_end":0.18364,"object_to_goal_dist_start":0.21314,"object_z_max":0.11712,"peak_contact_force":0.06826,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41094.0,"raw_peak_contact_force":0.63966,"tcp_end":[0.4982,0.0382,0.12815],"tcp_start":[0.50237,0.03853,0.03023],"tcp_to_object_dist_end":0.01312,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49866,0.02999,0.21778],"object_pos_start":[0.50547,0.0382,0.11723],"object_to_goal_dist_end":0.20549,"object_to_goal_dist_start":0.18364,"object_z_max":0.21768,"peak_contact_force":0.11055,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36240.0,"raw_peak_contact_force":0.13941,"subtask_id":"transport_arc","tcp_end":[0.48742,0.03018,0.23576],"tcp_start":[0.4982,0.0382,0.12815],"tcp_to_object_dist_end":0.0212,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61126,0.15634,0.11437],"object_pos_start":[0.49866,0.02999,0.21778],"object_to_goal_dist_end":0.03831,"object_to_goal_dist_start":0.20549,"object_z_max":0.2178,"peak_contact_force":0.1268,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":25736.0,"raw_peak_contact_force":0.37319,"tcp_end":[0.60805,0.15589,0.14657],"tcp_start":[0.48742,0.03018,0.23576],"tcp_to_object_dist_end":0.03236,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62076,0.16145,0.01857],"object_pos_start":[0.61126,0.15634,0.11437],"object_to_goal_dist_end":0.12712,"object_to_goal_dist_start":0.03831,"object_z_max":0.11437,"peak_contact_force":0.26795,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1318.0,"raw_peak_contact_force":1.37408,"subtask_id":"release_1","tcp_end":[0.60178,0.15417,0.16688],"tcp_start":[0.60805,0.15589,0.14657],"tcp_to_object_dist_end":0.1497,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.62859,0.16702,0.01602],"object_pos_start":[0.62076,0.16145,0.01857],"object_to_goal_dist_end":0.12913,"object_to_goal_dist_start":0.12712,"object_z_max":0.01885,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2972.0,"raw_peak_contact_force":0.37182,"tcp_end":[0.59918,0.15334,0.27338],"tcp_start":[0.60178,0.15417,0.16688],"tcp_to_object_dist_end":0.25939,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.09217,"average_solve_count":217.0,"average_success_count":217.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.20733,"approach_1.approach_tol":0.02583,"approach_1.speed":0.09649,"descend_1.descend_speed":0.06641,"descend_1.descend_tol":0.02684,"descend_1.grasp_z_offset":0.00048,"descend_2.descend_2_speed":0.10035,"descend_2.descend_2_tol":0.03876,"grasp_1.grasp_duration":0.55281,"lift_1.lift_height":0.22548,"lift_1.lift_speed":0.15527,"lift_1.lift_tol":0.0126,"release_1.release_duration":1.15057,"retract_1.retract_height":0.2129,"retract_1.retract_speed":0.16076,"retract_1.retract_tol":0.01825,"transport_arc.arc_clearance":0.17848,"transport_arc.arc_height":0.22687,"transport_arc.transport_speed":0.11197,"transport_arc.transport_tol":0.01976},"optimized_scores":{"best_composite_score":-0.44915,"best_fitness_score":0.55085,"best_task_score":0.13491},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3520.0,"contact_point_centroid":[0.47286,0.04889,-0.00235],"force_p95":0.12463,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.15826,"mean_force":0.13732,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46667,0.04403,0.31852]},{"body_a":"world","body_b":"grasp_target","contact_count":131.0,"contact_point_centroid":[0.48011,0.04628,-0.00119],"force_p95":0.46533,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72737,"mean_force":0.07711,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4721,0.04714,0.03241]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":93.0,"contact_point_centroid":[0.47611,0.02868,0.23675],"force_p95":0.26839,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37113,"mean_force":0.17843,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46991,0.04652,0.24225]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13304.0,"contact_point_centroid":[0.47207,0.06589,0.1169],"force_p95":0.11351,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34833,"mean_force":0.06697,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46993,0.04693,0.11532]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13379.0,"contact_point_centroid":[0.4722,0.02807,0.11738],"force_p95":0.11606,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34446,"mean_force":0.06601,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46993,0.04693,0.11582]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.48274,0.04844,-0.00216],"force_p95":0.15979,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23454,"mean_force":0.13439,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47394,0.04734,0.03081]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":208.0,"contact_point_centroid":[0.47478,0.06274,0.23791],"force_p95":0.16919,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22733,"mean_force":0.09098,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46937,0.04609,0.24307]},{"body_a":"world","body_b":"grasp_target","contact_count":940.0,"contact_point_centroid":[0.4827,0.04873,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12315,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49094,0.01917,0.27131]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5782.0,"contact_point_centroid":[0.47372,0.02812,0.03231],"force_p95":0.07318,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13244,"mean_force":0.04496,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47352,0.04729,0.03037]},{"body_a":"world","body_b":"grasp_target","contact_count":2748.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47919,0.04395,0.13777]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47281,0.04887,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.52626,0.14211,0.29935]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.47281,0.04887,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56909,0.21581,0.23285]},{"body_a":"world","body_b":"grasp_target","contact_count":3128.0,"contact_point_centroid":[0.47281,0.04887,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.56672,0.21453,0.34591]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6000.0,"contact_point_centroid":[0.47369,0.06655,0.03222],"force_p95":0.07372,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08569,"mean_force":0.04504,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47353,0.0473,0.03037]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3529.0,"contact_point_centroid":[0.46713,0.04421,0.32371],"force_p95":0.01106,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01636,"mean_force":0.01063,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.4668,0.0442,0.32143]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4284.0,"contact_point_centroid":[0.52681,0.14233,0.30143],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01268,"mean_force":0.01041,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.52639,0.14231,0.29917]}],"total_contact_groups":17},"final_pose_error":0.01741,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.47281,0.04887,0.01602],"final_tcp_position":[0.56803,0.2149,0.44815],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":9748.72396,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":236.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":940.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48266,0.04035,0.24255],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21669,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":687.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2748.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47827,0.04776,0.03534],"tcp_start":[0.48266,0.04035,0.24255],"tcp_to_object_dist_end":0.01036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.04749,0.02553],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29112,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15252,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13586.0,"raw_peak_contact_force":0.23454,"subtask_id":"grasp_1","tcp_end":[0.4735,0.04729,0.03035],"tcp_start":[0.47351,0.04729,0.03035],"tcp_to_object_dist_end":0.01031,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":872.0,"n_steps_budget":930.0,"object_pos_end":[0.48363,0.04718,0.2191],"object_pos_start":[0.48261,0.04747,0.02555],"object_to_goal_dist_end":0.20686,"object_to_goal_dist_start":0.29112,"object_z_max":0.21896,"peak_contact_force":0.18769,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26814.0,"raw_peak_contact_force":0.72737,"tcp_end":[0.47064,0.047,0.24114],"tcp_start":[0.4735,0.04729,0.03035],"tcp_to_object_dist_end":0.02557,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47281,0.04887,0.01602],"object_pos_start":[0.48363,0.04718,0.2191],"object_to_goal_dist_end":0.30047,"object_to_goal_dist_start":0.20686,"object_z_max":0.21972,"peak_contact_force":9748.72396,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7350.0,"raw_peak_contact_force":2.15826,"subtask_id":"transport_arc","tcp_end":[0.47862,0.06248,0.37575],"tcp_start":[0.47064,0.047,0.24114],"tcp_to_object_dist_end":0.36004,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47281,0.04887,0.01602],"object_pos_start":[0.47281,0.04887,0.01602],"object_to_goal_dist_end":0.30047,"object_to_goal_dist_start":0.30047,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8284.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57238,0.21703,0.23188],"tcp_start":[0.47862,0.06248,0.37575],"tcp_to_object_dist_end":0.29119,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47281,0.04887,0.01602],"object_pos_start":[0.47281,0.04887,0.01602],"object_to_goal_dist_end":0.30047,"object_to_goal_dist_start":0.30047,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.56795,0.21523,0.25265],"tcp_start":[0.57238,0.21703,0.23188],"tcp_to_object_dist_end":0.30451,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":782.0,"n_steps_budget":840.0,"object_pos_end":[0.47281,0.04887,0.01602],"object_pos_start":[0.47281,0.04887,0.01602],"object_to_goal_dist_end":0.30047,"object_to_goal_dist_start":0.30047,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3128.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56803,0.2149,0.44815],"tcp_start":[0.56795,0.21523,0.25265],"tcp_to_object_dist_end":0.47262,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71134,"average_solve_count":194.0,"average_success_count":194.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.21592,"approach_1.approach_tol":0.0219,"approach_1.speed":0.09418,"descend_1.descend_speed":0.10758,"descend_1.descend_tol":0.00648,"descend_1.grasp_z_offset":0.01521,"descend_2.descend_2_speed":0.08393,"descend_2.descend_2_tol":0.02848,"grasp_1.grasp_duration":1.23603,"lift_1.lift_height":0.1652,"lift_1.lift_speed":0.05607,"lift_1.lift_tol":0.01754,"release_1.release_duration":0.61936,"retract_1.retract_height":0.18857,"retract_1.retract_speed":0.12454,"retract_1.retract_tol":0.01115,"transport_arc.arc_clearance":0.19282,"transport_arc.arc_height":0.26899,"transport_arc.transport_speed":0.06899,"transport_arc.transport_tol":0.01895},"optimized_scores":{"best_composite_score":-0.43565,"best_fitness_score":0.56435,"best_task_score":0.19213},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":117.0,"contact_point_centroid":[0.5461,0.07879,-0.01024],"force_p95":1.42919,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.76794,"mean_force":0.62448,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54742,0.0774,0.22733]},{"body_a":"world","body_b":"grasp_target","contact_count":211.0,"contact_point_centroid":[0.5321,-0.02085,-0.00119],"force_p95":0.2872,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47204,"mean_force":0.08825,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52467,-0.02085,0.04502]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20467.0,"contact_point_centroid":[0.5224,-0.0399,0.09099],"force_p95":0.07225,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29519,"mean_force":0.04929,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52229,-0.0208,0.08903]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19357.0,"contact_point_centroid":[0.52256,-0.00164,0.08986],"force_p95":0.07727,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29193,"mean_force":0.05176,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5223,-0.0208,0.08787]},{"body_a":"world","body_b":"grasp_target","contact_count":3424.0,"contact_point_centroid":[0.53307,0.07873,-0.00208],"force_p95":0.1811,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25287,"mean_force":0.12669,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54533,0.07704,0.32277]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17169.0,"contact_point_centroid":[0.50999,-0.02975,0.17891],"force_p95":0.08997,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21871,"mean_force":0.0575,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50883,-0.04884,0.17808]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19369.0,"contact_point_centroid":[0.50959,-0.06812,0.17933],"force_p95":0.0794,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21425,"mean_force":0.05123,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50873,-0.04913,0.17864]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10911.0,"contact_point_centroid":[0.52901,-0.0164,0.21835],"force_p95":0.1253,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19421,"mean_force":0.08308,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.52468,0.00181,0.22034]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9461.0,"contact_point_centroid":[0.52946,0.02102,0.21771],"force_p95":0.13197,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19095,"mean_force":0.09595,"phase_index":5.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.52498,0.00259,0.22029]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":543.0,"contact_point_centroid":[0.55541,0.09651,0.20491],"force_p95":0.12858,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18681,"mean_force":0.09169,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55072,0.07804,0.20987]},{"body_a":"world","body_b":"grasp_target","contact_count":1804.0,"contact_point_centroid":[0.53703,-0.02126,-0.00205],"force_p95":0.13454,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16539,"mean_force":0.12661,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52713,-0.0209,0.04395]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":603.0,"contact_point_centroid":[0.55535,0.05981,0.20501],"force_p95":0.11652,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16037,"mean_force":0.081,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55074,0.07804,0.20991]},{"body_a":"world","body_b":"grasp_target","contact_count":956.0,"contact_point_centroid":[0.53702,-0.02132,-0.00186],"force_p95":0.13695,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12314,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51304,-0.00873,0.27356]},{"body_a":"world","body_b":"grasp_target","contact_count":2376.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52876,-0.01939,0.14801]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5840.0,"contact_point_centroid":[0.52685,-0.00171,0.04532],"force_p95":0.06879,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10975,"mean_force":0.04498,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52667,-0.02089,0.04341]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5889.0,"contact_point_centroid":[0.52687,-0.04009,0.04529],"force_p95":0.06902,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08689,"mean_force":0.04503,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52667,-0.02089,0.04341]}],"total_contact_groups":16},"final_pose_error":0.01497,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.5322,0.07869,0.02602],"final_tcp_position":[0.54634,0.07715,0.40936],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.76794,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":240.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":956.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52814,-0.01787,0.24851],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.2227,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":594.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2376.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53175,-0.02099,0.04951],"tcp_start":[0.52814,-0.01787,0.24851],"tcp_to_object_dist_end":0.02408,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53694,-0.02102,0.02583],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31661,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13315,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":13533.0,"raw_peak_contact_force":0.16539,"subtask_id":"grasp_1","tcp_end":[0.52665,-0.02089,0.04339],"tcp_start":[0.52665,-0.02089,0.04339],"tcp_to_object_dist_end":0.02035,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5271,-0.02086,0.11219],"object_pos_start":[0.53694,-0.02101,0.02584],"object_to_goal_dist_end":0.27892,"object_to_goal_dist_start":0.31659,"object_z_max":0.1121,"peak_contact_force":0.06735,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40035.0,"raw_peak_contact_force":0.47204,"tcp_end":[0.52243,-0.0208,0.13528],"tcp_start":[0.52665,-0.02089,0.04339],"tcp_to_object_dist_end":0.02355,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51,-0.06696,0.20381],"object_pos_start":[0.5271,-0.02086,0.11219],"object_to_goal_dist_end":0.31133,"object_to_goal_dist_start":0.27892,"object_z_max":0.20371,"peak_contact_force":0.10164,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36538.0,"raw_peak_contact_force":0.21871,"subtask_id":"transport_arc","tcp_end":[0.50275,-0.06676,0.23187],"tcp_start":[0.52243,-0.0208,0.13528],"tcp_to_object_dist_end":0.02899,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":17.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55711,0.07773,0.17561],"object_pos_start":[0.51,-0.06696,0.20381],"object_to_goal_dist_end":0.16233,"object_to_goal_dist_start":0.31133,"object_z_max":0.20384,"peak_contact_force":0.12175,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":20372.0,"raw_peak_contact_force":0.19421,"tcp_end":[0.55236,0.07799,0.21295],"tcp_start":[0.50275,-0.06676,0.23187],"tcp_to_object_dist_end":0.03764,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54833,0.07529,0.02166],"object_pos_start":[0.55711,0.07773,0.17561],"object_to_goal_dist_end":0.24818,"object_to_goal_dist_start":0.16233,"object_z_max":0.17561,"peak_contact_force":0.22622,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1263.0,"raw_peak_contact_force":1.76794,"subtask_id":"release_1","tcp_end":[0.54736,0.0774,0.23573],"tcp_start":[0.55236,0.07799,0.21295],"tcp_to_object_dist_end":0.21409,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":896.0,"n_steps_budget":960.0,"object_pos_end":[0.5322,0.07869,0.02602],"object_pos_start":[0.54833,0.07529,0.02166],"object_to_goal_dist_end":0.24744,"object_to_goal_dist_start":0.24818,"object_z_max":0.02992,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3424.0,"raw_peak_contact_force":0.25287,"tcp_end":[0.54634,0.07715,0.40936],"tcp_start":[0.54736,0.0774,0.23573],"tcp_to_object_dist_end":0.38361,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```