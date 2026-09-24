## Search State

- **Seed**: 7
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 18 | -0.3990 | 0.25 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 17 | -0.3672 | 0.31 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 20 | -0.3920 | 0.26 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | pose_tolerance | 16 | -0.1848 | 0.52 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 16 | -0.0176 | 0.85 | ❌ rejected |

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

## Current Skill (Q=-0.399) — your mutation base

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

- **Composite score**: -0.399
- **task_score** (E): 0.250
- **fitness_score**: 0.601  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 1.000

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0758 |
| descend_1 | 1.00 | 1.00 | 0.0008 |
| grasp_1 | 1.00 | 1.00 | 0.0118 |
| lift_1 | 1.00 | 1.00 | 0.1396 |
| transport_arc | 0.00 | 1.00 | 0.0186 |
| place_1 | 0.33 | 1.00 | 0.1308 |
| release_object | 1.00 | 1.00 | 0.0226 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.020, 0.239) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.505, 0.022, 0.042)→(0.505, 0.022, 0.041) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.505, 0.022, 0.041)→(0.497, 0.022, 0.032) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.274 | 1.00 / 43.000 | 0.141 | 0.200 |
| lift_1 | lift | 1.00 / step_budget | (0.497, 0.022, 0.032)→(0.494, 0.021, 0.172) | (0.511, 0.022, 0.026)→(0.510, 0.021, 0.159) | 0.274→0.220 | 1.00 / 27.333 | 524.431 | 0.611 |
| transport_arc | approach | 0.00 / guard_failure | (0.494, 0.021, 0.172)→(0.492, 0.022, 0.189) | (0.510, 0.021, 0.159)→(0.507, 0.023, 0.170) | 0.220→0.217 | 1.00 / 21.000 | 0.000 | 0.186 |
| place_1 | descend | 0.33 / step_budget | (0.492, 0.022, 0.189)→(0.561, 0.124, 0.224) | (0.507, 0.023, 0.170)→(0.559, 0.098, 0.016) | 0.217→0.226 | 1.00 / 8.667 | 91002.178 | 1.918 |
| release_object | release | 1.00 / step_budget | (0.561, 0.124, 0.224)→(0.557, 0.123, 0.246) | (0.559, 0.098, 0.016)→(0.559, 0.098, 0.016) | 0.226→0.226 | 1.00 / 4.000 | 0.123 | 0.124 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.416
- phase_score: 0.283
- phase_breakdown.approach_1_score: 0.025
- phase_breakdown.transport_arc_score: 0.022
- phase_breakdown.release_1_score: 0.217
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.868
- grasp_place_fitness: 0.681

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.681
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.416
- **Median Q (composite search score)**: -0.418
- **K-run variance**: 0.0035
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at lower bound**: place_1.place_speed
- **Final σ (mean)**: 0.316


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10714,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18449,"approach_1.approach_tol":0.00306,"approach_1.speed":0.15852,"descend_1.descend_speed":0.05983,"descend_1.descend_tol":0.00618,"descend_1.grasp_z_offset":0.01556,"grasp_1.grasp_duration":1.70704,"lift_1.lift_height":0.15543,"lift_1.lift_speed":0.10761,"lift_1.lift_tol":0.0286,"place_1.place_speed":0.24001,"place_1.place_tol":0.02447,"place_1.place_z_offset":0.06382,"release_object.release_duration":0.38078,"transport_arc.transport_altitude":0.19194,"transport_arc.transport_arc_height":0.07831,"transport_arc.transport_speed":0.14233,"transport_arc.transport_tol":0.02912},"optimized_scores":{"best_composite_score":-0.31938,"best_fitness_score":0.68062,"best_task_score":0.41555},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":641.0,"contact_point_centroid":[0.61172,0.15096,-0.0035],"force_p95":0.70482,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.70627,"mean_force":0.19082,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.60266,0.14972,0.1949]},{"body_a":"world","body_b":"grasp_target","contact_count":78.0,"contact_point_centroid":[0.50996,0.03854,-0.00141],"force_p95":0.46583,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53396,"mean_force":0.11888,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49797,0.0385,0.0381]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6418.0,"contact_point_centroid":[0.49833,0.01942,0.09941],"force_p95":0.1088,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32369,"mean_force":0.07087,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49554,0.0383,0.09714]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6752.0,"contact_point_centroid":[0.49825,0.05719,0.09628],"force_p95":0.10796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31534,"mean_force":0.06834,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49556,0.0383,0.09442]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8455.0,"contact_point_centroid":[0.54408,0.10228,0.1795],"force_p95":0.12912,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29887,"mean_force":0.08442,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.53793,0.08411,0.1793]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6941.0,"contact_point_centroid":[0.54212,0.06406,0.17968],"force_p95":0.15711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23771,"mean_force":0.10008,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.53647,0.0826,0.17898]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51254,0.03952,-0.0021],"force_p95":0.15064,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21538,"mean_force":0.1301,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50041,0.03871,0.03806]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4086.0,"contact_point_centroid":[0.49987,0.01942,0.03957],"force_p95":0.07989,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14191,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49922,0.03862,0.03676]},{"body_a":"world","body_b":"grasp_target","contact_count":2140.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50323,0.01899,0.25407]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10.0,"contact_point_centroid":[0.50026,0.01972,0.17416],"force_p95":0.12113,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12951,"mean_force":0.10137,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49568,0.03831,0.17271]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.61205,0.1509,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12275,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.60835,0.15844,0.19765]},{"body_a":"world","body_b":"grasp_target","contact_count":8080.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5062,0.03862,0.08374]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13.0,"contact_point_centroid":[0.50119,0.05698,0.174],"force_p95":0.11205,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11695,"mean_force":0.08321,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49568,0.03831,0.17271]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4960.0,"contact_point_centroid":[0.49984,0.05775,0.03851],"force_p95":0.0724,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08145,"mean_force":0.04464,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49922,0.03862,0.03676]},{"body_a":"left_finger","body_b":"right_finger","contact_count":440.0,"contact_point_centroid":[0.60648,0.15301,0.19776],"force_p95":0.0137,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01513,"mean_force":0.01112,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.60591,0.153,0.19568]},{"body_a":"left_finger","body_b":"right_finger","contact_count":217.0,"contact_point_centroid":[0.6113,0.1593,0.19651],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01021,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.61085,0.15927,0.1941]}],"total_contact_groups":16},"final_pose_error":0.0233,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61205,0.1509,0.01602],"final_tcp_position":[0.61221,0.15943,0.19719],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.70627,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":536.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2140.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50832,0.03709,0.21387],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18791,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":2020.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8080.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50711,0.03927,0.04546],"tcp_start":[0.50717,0.03926,0.0455],"tcp_to_object_dist_end":0.02018,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.0387,0.02567],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2131,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14485,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10846.0,"raw_peak_contact_force":0.21538,"subtask_id":"grasp_1","tcp_end":[0.49919,0.03861,0.03673],"tcp_start":[0.50711,0.03927,0.04546],"tcp_to_object_dist_end":0.01725,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":432.0,"n_steps_budget":900.0,"object_pos_end":[0.51241,0.03847,0.15546],"object_pos_start":[0.51243,0.0387,0.02567],"object_to_goal_dist_end":0.17703,"object_to_goal_dist_start":0.2131,"object_z_max":0.1552,"peak_contact_force":0.11617,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13248.0,"raw_peak_contact_force":0.53396,"tcp_end":[0.49568,0.03831,0.17271],"tcp_start":[0.49919,0.03861,0.03673],"tcp_to_object_dist_end":0.02403,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.51249,0.03847,0.15562],"object_pos_start":[0.51241,0.03847,0.15546],"object_to_goal_dist_end":0.17699,"object_to_goal_dist_start":0.17703,"object_z_max":0.15546,"peak_contact_force":0.0,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":23.0,"raw_peak_contact_force":0.12951,"subtask_id":"transport_arc","tcp_end":[0.49575,0.03832,0.17288],"tcp_start":[0.49568,0.03831,0.17271],"tcp_to_object_dist_end":0.02405,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61205,0.15091,0.01601],"object_pos_start":[0.51249,0.03847,0.15562],"object_to_goal_dist_end":0.13173,"object_to_goal_dist_start":0.17699,"object_z_max":0.15894,"peak_contact_force":0.12276,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16477.0,"raw_peak_contact_force":1.70627,"tcp_end":[0.61221,0.15943,0.19719],"tcp_start":[0.49575,0.03832,0.17288],"tcp_to_object_dist_end":0.18139,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61205,0.1509,0.01602],"object_pos_start":[0.61205,0.15091,0.01601],"object_to_goal_dist_end":0.13172,"object_to_goal_dist_start":0.13173,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12275,"subtask_id":"release_1","tcp_end":[0.60693,0.15796,0.21714],"tcp_start":[0.61221,0.15943,0.19719],"tcp_to_object_dist_end":0.20131,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23834,"average_solve_count":193.0,"average_success_count":193.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19775,"approach_1.approach_tol":0.00554,"approach_1.speed":0.26652,"descend_1.descend_speed":0.1586,"descend_1.descend_tol":0.00479,"descend_1.grasp_z_offset":0.00913,"grasp_1.grasp_duration":1.44067,"lift_1.lift_height":0.15644,"lift_1.lift_speed":0.03975,"lift_1.lift_tol":0.02761,"place_1.place_speed":0.14634,"place_1.place_tol":0.03234,"place_1.place_z_offset":0.06654,"release_object.release_duration":0.68384,"transport_arc.transport_altitude":0.16336,"transport_arc.transport_arc_height":0.0927,"transport_arc.transport_speed":0.1345,"transport_arc.transport_tol":0.03808},"optimized_scores":{"best_composite_score":-0.41813,"best_fitness_score":0.58187,"best_task_score":0.20901},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":402.0,"contact_point_centroid":[0.52962,0.14894,-0.00508],"force_p95":0.98775,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.14232,"mean_force":0.2442,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.52139,0.1399,0.24264]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.47846,0.04706,-0.00153],"force_p95":0.53314,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5532,"mean_force":0.21993,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46877,0.04732,0.03282]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10029.0,"contact_point_centroid":[0.46589,0.06626,0.09993],"force_p95":0.07406,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.291,"mean_force":0.04954,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46628,0.04707,0.09832]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8262.0,"contact_point_centroid":[0.4865,0.06141,0.21183],"force_p95":0.14971,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2852,"mean_force":0.09008,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.48206,0.07999,0.21119]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9385.0,"contact_point_centroid":[0.4885,0.10058,0.21233],"force_p95":0.12711,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26738,"mean_force":0.08164,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.48342,0.08216,0.21226]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9582.0,"contact_point_centroid":[0.46607,0.02787,0.09883],"force_p95":0.07344,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2543,"mean_force":0.0507,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46628,0.04707,0.09665]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48273,0.04852,-0.00211],"force_p95":0.15462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22779,"mean_force":0.13125,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47095,0.04755,0.03297]},{"body_a":"world","body_b":"grasp_target","contact_count":1712.0,"contact_point_centroid":[0.4827,0.04873,-0.00192],"force_p95":0.13411,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12291,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4896,0.02167,0.26324]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52962,0.14881,-0.00198],"force_p95":0.12465,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12581,"mean_force":0.12295,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.52165,0.14406,0.2481]},{"body_a":"world","body_b":"grasp_target","contact_count":7828.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47722,0.04718,0.07859]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3014.0,"contact_point_centroid":[0.46267,0.0244,0.18445],"force_p95":0.0808,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12161,"mean_force":0.05557,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46168,0.04346,0.18204]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3113.0,"contact_point_centroid":[0.46285,0.06275,0.18294],"force_p95":0.07961,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11815,"mean_force":0.05452,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46192,0.04369,0.18102]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5037.0,"contact_point_centroid":[0.46981,0.0282,0.03497],"force_p95":0.07001,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11091,"mean_force":0.04294,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4698,0.04744,0.03181]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5475.0,"contact_point_centroid":[0.46962,0.06675,0.03429],"force_p95":0.06917,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08019,"mean_force":0.04117,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46981,0.04744,0.03181]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.52333,0.14212,0.24604],"force_p95":0.01482,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01616,"mean_force":0.01173,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.52284,0.1421,0.2438]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.52432,0.14477,0.24511],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01098,"mean_force":0.00999,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.5237,0.14475,0.24313]}],"total_contact_groups":16},"final_pose_error":0.11406,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.52962,0.14881,0.01602],"final_tcp_position":[0.5247,0.1448,0.24528],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":2.14232,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":429.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1712.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48104,0.0442,0.22879],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20283,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1957.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7828.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47738,0.04819,0.03954],"tcp_start":[0.4777,0.04821,0.03959],"tcp_to_object_dist_end":0.01453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.04763,0.02561],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29098,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.14922,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12312.0,"raw_peak_contact_force":0.22779,"subtask_id":"grasp_1","tcp_end":[0.46977,0.04743,0.03178],"tcp_start":[0.47738,0.04819,0.03954],"tcp_to_object_dist_end":0.01424,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":463.0,"n_steps_budget":1000.0,"object_pos_end":[0.47689,0.04697,0.1596],"object_pos_start":[0.48261,0.04763,0.02561],"object_to_goal_dist_end":0.22165,"object_to_goal_dist_start":0.29098,"object_z_max":0.15932,"peak_contact_force":0.08231,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19697.0,"raw_peak_contact_force":0.5532,"tcp_end":[0.46636,0.04708,0.16877],"tcp_start":[0.46977,0.04743,0.03178],"tcp_to_object_dist_end":0.01396,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":166.0,"n_steps_budget":1000.0,"object_pos_end":[0.47299,0.04141,0.18343],"object_pos_start":[0.47689,0.04697,0.1596],"object_to_goal_dist_end":0.22183,"object_to_goal_dist_start":0.22165,"object_z_max":0.18326,"peak_contact_force":0.0,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6127.0,"raw_peak_contact_force":0.12161,"subtask_id":"transport_arc","tcp_end":[0.4594,0.04114,0.19465],"tcp_start":[0.46636,0.04708,0.16877],"tcp_to_object_dist_end":0.01763,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52962,0.14886,0.01633],"object_pos_start":[0.47299,0.04141,0.18343],"object_to_goal_dist_end":0.23451,"object_to_goal_dist_start":0.22183,"object_z_max":0.20957,"peak_contact_force":0.1256,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":18272.0,"raw_peak_contact_force":2.14232,"tcp_end":[0.5247,0.1448,0.24528],"tcp_start":[0.4594,0.04114,0.19465],"tcp_to_object_dist_end":0.22905,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52962,0.14881,0.01602],"object_pos_start":[0.52962,0.14886,0.01633],"object_to_goal_dist_end":0.2348,"object_to_goal_dist_start":0.23451,"object_z_max":0.01633,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12581,"subtask_id":"release_1","tcp_end":[0.52052,0.14368,0.26858],"tcp_start":[0.5247,0.1448,0.24528],"tcp_to_object_dist_end":0.25278,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22159,"average_solve_count":176.0,"average_success_count":176.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.25054,"approach_1.approach_tol":0.00543,"approach_1.speed":0.11124,"descend_1.descend_speed":0.09157,"descend_1.descend_tol":0.00509,"descend_1.grasp_z_offset":0.00821,"grasp_1.grasp_duration":1.61476,"lift_1.lift_height":0.16521,"lift_1.lift_speed":0.1707,"lift_1.lift_tol":0.0292,"place_1.place_speed":0.01,"place_1.place_tol":0.0294,"place_1.place_z_offset":0.09839,"release_object.release_duration":0.44512,"transport_arc.transport_altitude":0.18993,"transport_arc.transport_arc_height":0.05869,"transport_arc.transport_speed":0.25967,"transport_arc.transport_tol":0.01464},"optimized_scores":{"best_composite_score":-0.45948,"best_fitness_score":0.54052,"best_task_score":0.12607},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3697.0,"contact_point_centroid":[0.53649,-0.0055,-0.00227],"force_p95":0.12625,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.90609,"mean_force":0.13586,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.534,0.0349,0.21476]},{"body_a":"world","body_b":"grasp_target","contact_count":73.0,"contact_point_centroid":[0.53375,-0.02066,-0.00131],"force_p95":0.70127,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74637,"mean_force":0.14466,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52162,-0.02102,0.02953]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5891.0,"contact_point_centroid":[0.5226,-0.00209,0.09478],"force_p95":0.11374,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37686,"mean_force":0.07622,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51923,-0.02097,0.09256]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6359.0,"contact_point_centroid":[0.52261,-0.03975,0.09188],"force_p95":0.1108,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34947,"mean_force":0.07166,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51925,-0.02097,0.09029]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1276.0,"contact_point_centroid":[0.52457,-0.03644,0.18107],"force_p95":0.21081,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30687,"mean_force":0.10969,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.51852,-0.01802,0.18221]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1376.0,"contact_point_centroid":[0.5245,0.00086,0.18263],"force_p95":0.18298,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28748,"mean_force":0.10564,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.51852,-0.01736,0.18414]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.02118,-0.00203],"force_p95":0.13246,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15807,"mean_force":0.12552,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5242,-0.02107,0.02959]},{"body_a":"world","body_b":"grasp_target","contact_count":3996.0,"contact_point_centroid":[0.53702,-0.02132,-0.00196],"force_p95":0.12459,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12275,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51589,-0.0107,0.28486]},{"body_a":"world","body_b":"grasp_target","contact_count":7856.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53053,-0.02086,0.1044]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53643,-0.0055,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54358,0.06831,0.23188]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4112.0,"contact_point_centroid":[0.52386,-0.00184,0.03088],"force_p95":0.07609,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11551,"mean_force":0.05178,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52295,-0.02105,0.02817]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2.0,"contact_point_centroid":[0.52686,0.00071,0.1928],"force_p95":0.0968,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10127,"mean_force":0.05656,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.51954,-0.0121,0.20035]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4884.0,"contact_point_centroid":[0.52384,-0.04012,0.02994],"force_p95":0.06842,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09117,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52295,-0.02105,0.02817]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3732.0,"contact_point_centroid":[0.53527,0.03707,0.21804],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0158,"mean_force":0.01046,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.53481,0.03708,0.21566]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.54596,0.06868,0.22918],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.011,"mean_force":0.01,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54584,0.06868,0.22703]}],"total_contact_groups":15},"final_pose_error":0.18752,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.53643,-0.0055,0.01602],"final_tcp_position":[0.54697,0.0687,0.22929],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273006.28612,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3996.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53219,-0.02014,0.27524],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.24927,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1964.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7856.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53127,-0.0212,0.03767],"tcp_start":[0.53161,-0.0212,0.03964],"tcp_to_object_dist_end":0.013,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53689,-0.02092,0.02587],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31652,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13021,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10796.0,"raw_peak_contact_force":0.15807,"subtask_id":"grasp_1","tcp_end":[0.52292,-0.02104,0.02813],"tcp_start":[0.53127,-0.0212,0.03767],"tcp_to_object_dist_end":0.01415,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":430.0,"n_steps_budget":630.0,"object_pos_end":[0.53959,-0.02101,0.16135],"object_pos_start":[0.53689,-0.02092,0.02587],"object_to_goal_dist_end":0.26269,"object_to_goal_dist_start":0.31652,"object_z_max":0.1611,"peak_contact_force":1573.09317,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12323.0,"raw_peak_contact_force":0.74637,"tcp_end":[0.51952,-0.02096,0.17372],"tcp_start":[0.52292,-0.02104,0.02813],"tcp_to_object_dist_end":0.02358,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":152.0,"n_steps_budget":1000.0,"object_pos_end":[0.53668,-0.00942,0.17034],"object_pos_start":[0.53959,-0.02101,0.16135],"object_to_goal_dist_end":0.25109,"object_to_goal_dist_start":0.26269,"object_z_max":0.17624,"peak_contact_force":0.0,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2652.0,"raw_peak_contact_force":0.30687,"subtask_id":"transport_arc","tcp_end":[0.51951,-0.01211,0.20032],"tcp_start":[0.51952,-0.02096,0.17372],"tcp_to_object_dist_end":0.03465,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53643,-0.0055,0.01602],"object_pos_start":[0.53668,-0.00942,0.17034],"object_to_goal_dist_end":0.31064,"object_to_goal_dist_start":0.25109,"object_z_max":0.17034,"peak_contact_force":273006.28612,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7431.0,"raw_peak_contact_force":1.90609,"tcp_end":[0.54697,0.0687,0.22929],"tcp_start":[0.51951,-0.01211,0.20032],"tcp_to_object_dist_end":0.22606,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53643,-0.0055,0.01602],"object_pos_start":[0.53643,-0.0055,0.01602],"object_to_goal_dist_end":0.31064,"object_to_goal_dist_start":0.31064,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.54232,0.06811,0.25227],"tcp_start":[0.54697,0.0687,0.22929],"tcp_to_object_dist_end":0.24752,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```