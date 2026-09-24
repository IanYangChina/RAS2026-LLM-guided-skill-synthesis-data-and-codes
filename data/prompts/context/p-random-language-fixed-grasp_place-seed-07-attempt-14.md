## Search State

- **Seed**: 7
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 17 | -0.4098 | 0.23 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 18 | -0.3990 | 0.25 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 17 | -0.3672 | 0.31 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 20 | -0.3920 | 0.26 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | pose_tolerance | 16 | -0.1848 | 0.52 | ❌ rejected |

**Proposal policy**: task_score is 0.23 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.410) — your mutation base

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

- **Composite score**: -0.410
- **task_score** (E): 0.232
- **fitness_score**: 0.590  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 1.000

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0791 |
| descend_1 | 1.00 | 1.00 | 0.1899 |
| grasp_1 | 1.00 | 1.00 | 0.0122 |
| lift_1 | 1.00 | 1.00 | 0.1629 |
| transport_arc | 0.00 | 1.00 | 0.1355 |
| place_1 | 0.67 | 1.00 | 0.1130 |
| release_1 | 1.00 | 1.00 | 0.0208 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.018, 0.232) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 2.784 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.018, 0.232)→(0.506, 0.022, 0.042) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.022, 0.042)→(0.498, 0.021, 0.033) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.274 | 1.00 / 43.000 | 0.148 | 0.213 |
| lift_1 | lift | 1.00 / step_budget | (0.498, 0.021, 0.033)→(0.494, 0.021, 0.196) | (0.511, 0.022, 0.026)→(0.509, 0.021, 0.183) | 0.274→0.223 | 1.00 / 29.333 | 0.097 | 0.597 |
| transport_arc | approach | 0.00 / step_budget | (0.494, 0.021, 0.196)→(0.547, 0.111, 0.277) | (0.509, 0.021, 0.183)→(0.529, 0.084, 0.122) | 0.223→0.206 | 1.00 / 16.667 | 3249.701 | 1.150 |
| place_1 | descend | 0.67 / step_budget | (0.547, 0.111, 0.277)→(0.596, 0.191, 0.231) | (0.529, 0.084, 0.122)→(0.546, 0.116, 0.086) | 0.206→0.158 | 1.00 / 16.000 | 0.113 | 0.171 |
| release_1 | release | 1.00 / step_budget | (0.596, 0.191, 0.231)→(0.591, 0.190, 0.251) | (0.546, 0.116, 0.086)→(0.544, 0.114, 0.016) | 0.158→0.225 | 1.00 / 4.000 | 0.194 | 0.758 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.302
- phase_score: 0.323
- phase_breakdown.approach_1_score: 0.013
- phase_breakdown.transport_arc_score: 0.086
- phase_breakdown.release_1_score: 0.276
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.833
- grasp_place_fitness: 0.627

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.627
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.302
- **Median Q (composite search score)**: -0.412
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.329


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67702,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.21208,"approach_1.approach_tol":0.02472,"approach_1.speed":0.13853,"descend_1.descend_speed":0.0909,"descend_1.descend_tol":0.04655,"descend_1.grasp_z_offset":0.00784,"grasp_1.grasp_duration":0.85954,"lift_1.lift_height":0.1081,"lift_1.lift_speed":0.16016,"lift_1.lift_tol":0.02711,"place_1.place_speed":0.03575,"place_1.place_tol":0.04745,"place_1.place_z_offset":0.05139,"release_1.release_duration":0.95182,"transport_arc.transport_altitude":0.18818,"transport_arc.transport_speed":0.18755,"transport_arc.transport_tol":0.04369},"optimized_scores":{"best_composite_score":-0.3729,"best_fitness_score":0.6271,"best_task_score":0.30238},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1930.0,"contact_point_centroid":[0.54139,0.08246,-0.00246],"force_p95":0.2157,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.67758,"mean_force":0.14678,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54839,0.09463,0.20536]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.51,0.03787,-0.00143],"force_p95":0.54273,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59714,"mean_force":0.13215,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49809,0.0381,0.03475]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4416.0,"contact_point_centroid":[0.49788,0.01892,0.07539],"force_p95":0.10814,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33428,"mean_force":0.06737,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49582,0.03791,0.07285]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4751.0,"contact_point_centroid":[0.4979,0.05686,0.07338],"force_p95":0.10622,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32586,"mean_force":0.06434,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49585,0.03791,0.07139]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4289.0,"contact_point_centroid":[0.51355,0.03533,0.14342],"force_p95":0.1676,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3127,"mean_force":0.09676,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50813,0.05382,0.14274]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4719.0,"contact_point_centroid":[0.51444,0.07295,0.14423],"force_p95":0.14163,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26793,"mean_force":0.09073,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50883,0.05457,0.14384]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51256,0.03946,-0.00214],"force_p95":0.16172,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23592,"mean_force":0.13296,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50056,0.03831,0.03461]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4069.0,"contact_point_centroid":[0.49994,0.01901,0.03613],"force_p95":0.08105,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15312,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49938,0.03821,0.03333]},{"body_a":"world","body_b":"grasp_target","contact_count":888.0,"contact_point_centroid":[0.51251,0.03972,-0.00185],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12318,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50278,0.01561,0.27309]},{"body_a":"world","body_b":"grasp_target","contact_count":2528.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50633,0.03566,0.14338]},{"body_a":"world","body_b":"grasp_target","contact_count":3444.0,"contact_point_centroid":[0.54136,0.08244,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.59739,0.1453,0.20458]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54136,0.08244,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61809,0.16839,0.18887]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5005.0,"contact_point_centroid":[0.49993,0.05738,0.03515],"force_p95":0.0738,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08288,"mean_force":0.04461,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49939,0.03821,0.03334]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1807.0,"contact_point_centroid":[0.55121,0.09691,0.21105],"force_p95":0.01176,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01776,"mean_force":0.01053,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55065,0.09689,0.20886]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3665.0,"contact_point_centroid":[0.59787,0.14529,0.20677],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01047,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.59736,0.14527,0.20461]},{"body_a":"left_finger","body_b":"right_finger","contact_count":219.0,"contact_point_centroid":[0.62113,0.16928,0.18765],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.01013,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62068,0.16925,0.18556]}],"total_contact_groups":16},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.54136,0.08244,0.01602],"final_tcp_position":[0.622,0.16958,0.18865],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.67758,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":223.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":888.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50736,0.03262,0.24648],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22063,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":632.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2528.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50757,0.03887,0.04234],"tcp_start":[0.50736,0.03262,0.24648],"tcp_to_object_dist_end":0.01707,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.03834,0.02554],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2134,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15377,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10874.0,"raw_peak_contact_force":0.23592,"subtask_id":"grasp_1","tcp_end":[0.49936,0.03821,0.0333],"tcp_start":[0.50757,0.03887,0.04234],"tcp_to_object_dist_end":0.0152,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":279.0,"n_steps_budget":600.0,"object_pos_end":[0.51281,0.03816,0.11002],"object_pos_start":[0.51243,0.03834,0.02554],"object_to_goal_dist_end":0.18014,"object_to_goal_dist_start":0.2134,"object_z_max":0.10976,"peak_contact_force":0.10688,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9247.0,"raw_peak_contact_force":0.59714,"tcp_end":[0.4955,0.03789,0.12204],"tcp_start":[0.49936,0.03821,0.0333],"tcp_to_object_dist_end":0.02107,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54136,0.08244,0.01602],"object_pos_start":[0.51281,0.03816,0.11002],"object_to_goal_dist_end":0.17941,"object_to_goal_dist_start":0.18014,"object_z_max":0.14387,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":12745.0,"raw_peak_contact_force":1.67758,"subtask_id":"transport_arc","tcp_end":[0.56599,0.11225,0.23259],"tcp_start":[0.4955,0.03789,0.12204],"tcp_to_object_dist_end":0.21999,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":861.0,"n_steps_budget":1000.0,"object_pos_end":[0.54136,0.08244,0.01602],"object_pos_start":[0.54136,0.08244,0.01602],"object_to_goal_dist_end":0.17941,"object_to_goal_dist_start":0.17941,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7109.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.622,0.16958,0.18865],"tcp_start":[0.56599,0.11225,0.23259],"tcp_to_object_dist_end":0.20951,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54136,0.08244,0.01602],"object_pos_start":[0.54136,0.08244,0.01602],"object_to_goal_dist_end":0.17941,"object_to_goal_dist_start":0.17941,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1019.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.6166,0.16788,0.20822],"tcp_start":[0.622,0.16958,0.18865],"tcp_to_object_dist_end":0.22338,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24638,"average_solve_count":276.0,"average_success_count":276.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.21065,"approach_1.approach_tol":0.0146,"approach_1.speed":0.03061,"descend_1.descend_speed":0.18244,"descend_1.descend_tol":0.02572,"descend_1.grasp_z_offset":0.01408,"grasp_1.grasp_duration":2.27618,"lift_1.lift_height":0.29955,"lift_1.lift_speed":0.02315,"lift_1.lift_tol":0.03903,"place_1.place_speed":0.15176,"place_1.place_tol":0.02043,"place_1.place_z_offset":0.02703,"release_1.release_duration":0.97706,"transport_arc.transport_altitude":0.19752,"transport_arc.transport_speed":0.02953,"transport_arc.transport_tol":0.00916},"optimized_scores":{"best_composite_score":-0.41221,"best_fitness_score":0.58779,"best_task_score":0.23642},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.5553,0.20935,-0.00897],"force_p95":1.35428,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.02836,"mean_force":0.50937,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5714,0.21997,0.27023]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.47988,0.04665,-0.00154],"force_p95":0.44771,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48608,"mean_force":0.12597,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46941,0.04684,0.04192]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":930.0,"contact_point_centroid":[0.57311,0.24026,0.24919],"force_p95":0.09199,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35302,"mean_force":0.06335,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57397,0.22134,0.25181]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18410.0,"contact_point_centroid":[0.46785,0.06578,0.18031],"force_p95":0.07929,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30022,"mean_force":0.05357,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46744,0.04665,0.17812]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1044.0,"contact_point_centroid":[0.57237,0.20228,0.25044],"force_p95":0.09373,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27686,"mean_force":0.06004,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57394,0.22133,0.25172]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10052.0,"contact_point_centroid":[0.54484,0.15523,0.30574],"force_p95":0.0926,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26737,"mean_force":0.06237,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.54568,0.17431,0.30593]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10413.0,"contact_point_centroid":[0.54526,0.19345,0.305],"force_p95":0.08041,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26661,"mean_force":0.05658,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.54585,0.17458,0.30563]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18270.0,"contact_point_centroid":[0.46804,0.02754,0.18241],"force_p95":0.07779,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25711,"mean_force":0.05349,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46744,0.04665,0.17995]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48275,0.04856,-0.00215],"force_p95":0.16348,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22929,"mean_force":0.13357,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47165,0.04707,0.04186]},{"body_a":"world","body_b":"grasp_target","contact_count":996.0,"contact_point_centroid":[0.4827,0.04873,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12312,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49093,0.01893,0.27284]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5039.0,"contact_point_centroid":[0.47028,0.02772,0.0434],"force_p95":0.07014,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12665,"mean_force":0.043,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47054,0.04697,0.04072]},{"body_a":"world","body_b":"grasp_target","contact_count":2196.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47941,0.04384,0.14607]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18843.0,"contact_point_centroid":[0.49329,0.06896,0.34095],"force_p95":0.07698,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10403,"mean_force":0.05153,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49243,0.088,0.33959]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18491.0,"contact_point_centroid":[0.49418,0.1072,0.34121],"force_p95":0.08043,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08965,"mean_force":0.05267,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49251,0.08812,0.33967]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5527.0,"contact_point_centroid":[0.4701,0.06629,0.04282],"force_p95":0.07008,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07284,"mean_force":0.04086,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47055,0.04697,0.04073]}],"total_contact_groups":15},"final_pose_error":0.0099,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.56402,0.21528,0.01533],"final_tcp_position":[0.57533,0.2217,0.25552],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":8.10624,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":250.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":8.10624,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":996.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48272,0.04014,0.24557],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21972,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":549.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2196.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.4783,0.04772,0.04878],"tcp_start":[0.48272,0.04014,0.24557],"tcp_to_object_dist_end":0.0232,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48265,0.04743,0.02548],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29118,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15772,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12366.0,"raw_peak_contact_force":0.22929,"subtask_id":"grasp_1","tcp_end":[0.47052,0.04696,0.04069],"tcp_start":[0.4783,0.04772,0.04878],"tcp_to_object_dist_end":0.01946,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":940.0,"n_steps_budget":1000.0,"object_pos_end":[0.47536,0.04668,0.29887],"object_pos_start":[0.48265,0.04743,0.02548],"object_to_goal_dist_end":0.22183,"object_to_goal_dist_start":0.29118,"object_z_max":0.2986,"peak_contact_force":0.06951,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36764.0,"raw_peak_contact_force":0.48608,"tcp_end":[0.46844,0.04674,0.32058],"tcp_start":[0.47052,0.04696,0.04069],"tcp_to_object_dist_end":0.02279,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51964,0.12684,0.33469],"object_pos_start":[0.47536,0.04668,0.29887],"object_to_goal_dist_end":0.15855,"object_to_goal_dist_start":0.22183,"object_z_max":0.33466,"peak_contact_force":0.08454,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37334.0,"raw_peak_contact_force":0.10403,"subtask_id":"transport_arc","tcp_end":[0.51691,0.1269,0.36171],"tcp_start":[0.46844,0.04674,0.32058],"tcp_to_object_dist_end":0.02716,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":577.0,"n_steps_budget":1000.0,"object_pos_end":[0.57052,0.22121,0.22578],"object_pos_start":[0.51964,0.12684,0.33469],"object_to_goal_dist_end":0.01447,"object_to_goal_dist_start":0.15855,"object_z_max":0.33469,"peak_contact_force":0.09439,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":20465.0,"raw_peak_contact_force":0.26737,"subtask_id":"release_1","tcp_end":[0.57533,0.2217,0.25552],"tcp_start":[0.51691,0.1269,0.36171],"tcp_to_object_dist_end":0.03013,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56402,0.21528,0.01533],"object_pos_start":[0.57052,0.22121,0.22578],"object_to_goal_dist_end":0.21632,"object_to_goal_dist_start":0.01447,"object_z_max":0.22578,"peak_contact_force":0.33562,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2122.0,"raw_peak_contact_force":2.02836,"subtask_id":"release_1","tcp_end":[0.57138,0.21997,0.27601],"tcp_start":[0.57533,0.2217,0.25552],"tcp_to_object_dist_end":0.26082,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02419,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16818,"approach_1.approach_tol":0.02662,"approach_1.speed":0.15309,"descend_1.descend_speed":0.11882,"descend_1.descend_tol":0.02819,"descend_1.grasp_z_offset":0.00117,"grasp_1.grasp_duration":2.93245,"lift_1.lift_height":0.13938,"lift_1.lift_speed":0.09855,"lift_1.lift_tol":0.01905,"place_1.place_speed":0.08982,"place_1.place_tol":0.01945,"place_1.place_z_offset":0.05848,"release_1.release_duration":1.32923,"transport_arc.transport_altitude":0.1503,"transport_arc.transport_speed":0.18747,"transport_arc.transport_tol":0.03419},"optimized_scores":{"best_composite_score":-0.4442,"best_fitness_score":0.5558,"best_task_score":0.15591},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2410.0,"contact_point_centroid":[0.5272,0.04314,-0.00234],"force_p95":0.15328,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.66892,"mean_force":0.14545,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54585,0.06124,0.20923]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.53363,-0.02083,-0.00135],"force_p95":0.62754,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70741,"mean_force":0.1572,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52172,-0.02084,0.02703]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5628.0,"contact_point_centroid":[0.52194,-0.00187,0.08086],"force_p95":0.11098,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33995,"mean_force":0.07362,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51904,-0.02078,0.07851]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6132.0,"contact_point_centroid":[0.52205,-0.03958,0.07885],"force_p95":0.10669,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31504,"mean_force":0.06881,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51907,-0.02078,0.07718]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2614.0,"contact_point_centroid":[0.52797,-0.02114,0.15631],"force_p95":0.19917,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31056,"mean_force":0.11291,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52263,-0.00266,0.15632]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3337.0,"contact_point_centroid":[0.52846,0.01738,0.15693],"force_p95":0.17172,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2888,"mean_force":0.09976,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5232,-0.0007,0.15774]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02113,-0.00204],"force_p95":0.13563,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17507,"mean_force":0.12634,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52423,-0.02089,0.02712]},{"body_a":"world","body_b":"grasp_target","contact_count":1352.0,"contact_point_centroid":[0.53702,-0.02132,-0.0019],"force_p95":0.13562,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51346,-0.00914,0.25162]},{"body_a":"world","body_b":"grasp_target","contact_count":2004.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52918,-0.01987,0.11878]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.52665,0.04314,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.57517,0.14403,0.24116]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52665,0.04314,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58726,0.18177,0.24937]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4100.0,"contact_point_centroid":[0.52384,-0.00167,0.02846],"force_p95":0.0768,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11422,"mean_force":0.05178,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52299,-0.02087,0.02572]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4904.0,"contact_point_centroid":[0.52384,-0.03995,0.02753],"force_p95":0.06887,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0924,"mean_force":0.04476,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52299,-0.02087,0.02573]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2342.0,"contact_point_centroid":[0.54727,0.06422,0.21405],"force_p95":0.01163,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01592,"mean_force":0.01064,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54698,0.06422,0.21176]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4259.0,"contact_point_centroid":[0.57575,0.14423,0.2434],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.01047,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.57524,0.14422,0.24119]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.58988,0.18258,0.24776],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01094,"mean_force":0.00988,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.58923,0.18256,0.24558]}],"total_contact_groups":16},"final_pose_error":0.05226,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.52665,0.04314,0.01602],"final_tcp_position":[0.5903,0.18275,0.24842],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":9748.89703,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":339.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1352.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52937,-0.01879,0.20389],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17805,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":501.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2004.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53161,-0.02102,0.03557],"tcp_start":[0.52937,-0.01879,0.20389],"tcp_to_object_dist_end":0.01098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53688,-0.02074,0.02584],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3164,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13265,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10804.0,"raw_peak_contact_force":0.17507,"subtask_id":"grasp_1","tcp_end":[0.52296,-0.02086,0.02569],"tcp_start":[0.53161,-0.02102,0.03557],"tcp_to_object_dist_end":0.01392,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":397.0,"n_steps_budget":900.0,"object_pos_end":[0.53911,-0.02065,0.13877],"object_pos_start":[0.53688,-0.02074,0.02584],"object_to_goal_dist_end":0.26737,"object_to_goal_dist_start":0.3164,"object_z_max":0.13852,"peak_contact_force":0.116,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11838.0,"raw_peak_contact_force":0.70741,"tcp_end":[0.51904,-0.02077,0.14547],"tcp_start":[0.52296,-0.02086,0.02569],"tcp_to_object_dist_end":0.02116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52665,0.04314,0.01602],"object_pos_start":[0.53911,-0.02065,0.13877],"object_to_goal_dist_end":0.27877,"object_to_goal_dist_start":0.26737,"object_z_max":0.14989,"peak_contact_force":9748.89703,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10703.0,"raw_peak_contact_force":1.66892,"subtask_id":"transport_arc","tcp_end":[0.55871,0.09509,0.23795],"tcp_start":[0.51904,-0.02077,0.14547],"tcp_to_object_dist_end":0.23017,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52665,0.04314,0.01602],"object_pos_start":[0.52665,0.04314,0.01602],"object_to_goal_dist_end":0.27877,"object_to_goal_dist_start":0.27877,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8259.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.5903,0.18275,0.24842],"tcp_start":[0.55871,0.09509,0.23795],"tcp_to_object_dist_end":0.27849,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52665,0.04314,0.01602],"object_pos_start":[0.52665,0.04314,0.01602],"object_to_goal_dist_end":0.27877,"object_to_goal_dist_start":0.27877,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.58617,0.18132,0.26901],"tcp_start":[0.5903,0.18275,0.24842],"tcp_to_object_dist_end":0.29435,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```