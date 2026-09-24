## Search State

- **Seed**: 7
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 17 | -0.1693 | 0.71 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 17 | -0.3888 | 0.27 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 16 | -0.0055 | 0.89 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 19 | -0.3651 | 0.30 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 19 | -0.4341 | 0.17 | ✅ accepted |

**Proposal policy**: task_score is 0.71 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.169) — your mutation base

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

- **Composite score**: -0.169
- **task_score** (E): 0.711
- **fitness_score**: 0.831  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 1.000

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0548 |
| descend_1 | 1.00 | 1.00 | 0.2177 |
| grasp_1 | 1.00 | 1.00 | 0.0122 |
| lift_1 | 1.00 | 1.00 | 0.1775 |
| transport_arc | 0.00 | 0.67 | 0.1362 |
| place_1 | 1.00 | 1.00 | 0.1200 |
| hold_at_goal | 1.00 | 1.00 | 0.0153 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.017, 0.261) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 3.347 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.017, 0.261)→(0.506, 0.022, 0.043) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.022, 0.043)→(0.498, 0.021, 0.034) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.274 | 1.00 / 43.000 | 0.149 | 0.214 |
| lift_1 | lift | 1.00 / step_budget | (0.498, 0.021, 0.034)→(0.495, 0.021, 0.212) | (0.511, 0.022, 0.026)→(0.504, 0.021, 0.198) | 0.274→0.222 | 1.00 / 39.000 | 0.077 | 0.542 |
| transport_arc | approach | 0.00 / guard_failure | (0.495, 0.021, 0.212)→(0.548, 0.120, 0.285) | (0.504, 0.021, 0.198)→(0.558, 0.122, 0.260) | 0.222→0.123 | 0.67 / 23.000 | 0.022 | 0.250 |
| place_1 | descend | 1.00 / step_budget | (0.548, 0.120, 0.285)→(0.601, 0.205, 0.225) | (0.558, 0.122, 0.260)→(0.600, 0.189, 0.133) | 0.123→0.071 | 1.00 / 21.667 | 0.112 | 0.921 |
| hold_at_goal | grasp | 1.00 / step_budget | (0.601, 0.205, 0.225)→(0.595, 0.203, 0.210) | (0.600, 0.189, 0.133)→(0.595, 0.188, 0.122) | 0.071→0.079 | 1.00 / 19.333 | 0.112 | 0.207 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.218
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.261
- phase_breakdown.approach_1_score: 0.009
- phase_breakdown.transport_arc_score: 0.059
- phase_breakdown.release_1_score: 0.000
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.778
- grasp_place_fitness: 0.979

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.979
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: -0.094
- **K-run variance**: 0.0259
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41916,"average_solve_count":167.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.24555,"approach_1.approach_tol":0.02487,"approach_1.speed":0.15671,"descend_1.descend_speed":0.14318,"descend_1.descend_tol":0.02898,"descend_1.grasp_z_offset":0.01261,"grasp_1.grasp_duration":1.23211,"hold_at_goal.hold_duration":1.54159,"lift_1.lift_height":0.18049,"lift_1.lift_speed":0.04482,"lift_1.lift_tol":0.01785,"place_1.place_speed":0.25301,"place_1.place_tol":0.00766,"place_1.place_z_offset":0.03592,"transport_arc.transport_altitude":0.21508,"transport_arc.transport_speed":0.33771,"transport_arc.transport_tol":0.04254},"optimized_scores":{"best_composite_score":-0.09424,"best_fitness_score":0.90576,"best_task_score":0.86805},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":89.0,"contact_point_centroid":[0.50837,0.03777,-0.00152],"force_p95":0.46869,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48806,"mean_force":0.17795,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49838,0.0381,0.03919]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8439.0,"contact_point_centroid":[0.59192,0.11626,0.21388],"force_p95":0.11167,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39378,"mean_force":0.07299,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.58764,0.13507,0.21295]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4609.0,"contact_point_centroid":[0.61759,0.14804,0.16121],"force_p95":0.12308,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33916,"mean_force":0.08888,"phase_index":6.0,"phase_name":"hold_at_goal","phase_type":"grasp","tcp_position_centroid":[0.61469,0.16627,0.16426]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4284.0,"contact_point_centroid":[0.61766,0.18456,0.16064],"force_p95":0.12311,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33281,"mean_force":0.0955,"phase_index":6.0,"phase_name":"hold_at_goal","phase_type":"grasp","tcp_position_centroid":[0.61463,0.16625,0.16413]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8790.0,"contact_point_centroid":[0.59084,0.15222,0.2158],"force_p95":0.09677,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30618,"mean_force":0.06973,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.58607,0.13348,0.2148]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11579.0,"contact_point_centroid":[0.49575,0.05702,0.1165],"force_p95":0.07675,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29238,"mean_force":0.05203,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49586,0.03789,0.11459]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10995.0,"contact_point_centroid":[0.49591,0.01873,0.11734],"force_p95":0.07767,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28521,"mean_force":0.05371,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49587,0.03789,0.11493]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7667.0,"contact_point_centroid":[0.52216,0.0459,0.22836],"force_p95":0.10056,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27771,"mean_force":0.06278,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52018,0.06489,0.22631]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51256,0.03949,-0.00213],"force_p95":0.15991,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22489,"mean_force":0.1325,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50065,0.03829,0.03932]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8489.0,"contact_point_centroid":[0.522,0.08366,0.22738],"force_p95":0.09247,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21709,"mean_force":0.05759,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52002,0.06475,0.2261]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4077.0,"contact_point_centroid":[0.5,0.01899,0.04084],"force_p95":0.08088,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15122,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49949,0.0382,0.03804]},{"body_a":"world","body_b":"grasp_target","contact_count":736.0,"contact_point_centroid":[0.51251,0.03972,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12329,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50283,0.01533,0.28675]},{"body_a":"world","body_b":"grasp_target","contact_count":2676.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50632,0.03502,0.15982]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5003.0,"contact_point_centroid":[0.5,0.05735,0.03986],"force_p95":0.07365,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07835,"mean_force":0.04453,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49949,0.0382,0.03805]}],"total_contact_groups":14},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.6176,0.1657,0.12757],"final_tcp_position":[0.62016,0.1678,0.17617],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.48806,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":185.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":736.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50718,0.03134,0.275],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.24918,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":669.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2676.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.5076,0.03885,0.04705],"tcp_start":[0.50718,0.03134,0.275],"tcp_to_object_dist_end":0.02161,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51245,0.03841,0.02555],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21334,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15284,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10880.0,"raw_peak_contact_force":0.22489,"subtask_id":"grasp_1","tcp_end":[0.49946,0.03819,0.03801],"tcp_start":[0.5076,0.03885,0.04705],"tcp_to_object_dist_end":0.018,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.50528,0.03804,0.18244],"object_pos_start":[0.51245,0.03841,0.02555],"object_to_goal_dist_end":0.18557,"object_to_goal_dist_start":0.21334,"object_z_max":0.18216,"peak_contact_force":0.07913,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22663.0,"raw_peak_contact_force":0.48806,"tcp_end":[0.49616,0.03792,0.1989],"tcp_start":[0.49946,0.03819,0.03801],"tcp_to_object_dist_end":0.01882,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":490.0,"n_steps_budget":1000.0,"object_pos_end":[0.56205,0.09632,0.239],"object_pos_start":[0.50528,0.03804,0.18244],"object_to_goal_dist_end":0.13758,"object_to_goal_dist_start":0.18557,"object_z_max":0.2389,"peak_contact_force":0.0,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16156.0,"raw_peak_contact_force":0.27771,"subtask_id":"transport_arc","tcp_end":[0.55088,0.0963,0.26258],"tcp_start":[0.49616,0.03792,0.1989],"tcp_to_object_dist_end":0.02609,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":611.0,"n_steps_budget":1000.0,"object_pos_end":[0.62395,0.16761,0.14635],"object_pos_start":[0.56205,0.09632,0.239],"object_to_goal_dist_end":0.00624,"object_to_goal_dist_start":0.13758,"object_z_max":0.239,"peak_contact_force":0.12185,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":17229.0,"raw_peak_contact_force":0.39378,"tcp_end":[0.62016,0.1678,0.17617],"tcp_start":[0.55088,0.0963,0.26258],"tcp_to_object_dist_end":0.03007,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6176,0.1657,0.12757],"object_pos_start":[0.62395,0.16761,0.14635],"object_to_goal_dist_end":0.02123,"object_to_goal_dist_start":0.00624,"object_z_max":0.14635,"peak_contact_force":0.1146,"phase_name":"hold_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":8893.0,"raw_peak_contact_force":0.33916,"tcp_end":[0.61351,0.16591,0.16171],"tcp_start":[0.62016,0.1678,0.17617],"tcp_to_object_dist_end":0.03438,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.08361,"average_solve_count":299.0,"average_success_count":299.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.23465,"approach_1.approach_tol":0.04604,"approach_1.speed":0.03511,"descend_1.descend_speed":0.05594,"descend_1.descend_tol":0.04031,"descend_1.grasp_z_offset":0.00352,"grasp_1.grasp_duration":0.98816,"hold_at_goal.hold_duration":0.93535,"lift_1.lift_height":0.26589,"lift_1.lift_speed":0.02578,"lift_1.lift_tol":0.03412,"place_1.place_speed":0.13708,"place_1.place_tol":0.03055,"place_1.place_z_offset":0.03176,"transport_arc.transport_altitude":0.1411,"transport_arc.transport_speed":0.06819,"transport_arc.transport_tol":0.0411},"optimized_scores":{"best_composite_score":-0.02076,"best_fitness_score":0.97924,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.47853,0.04647,-0.00153],"force_p95":0.57205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59473,"mean_force":0.21867,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46949,0.04685,0.0315]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16810.0,"contact_point_centroid":[0.4673,0.06579,0.15534],"force_p95":0.07494,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2981,"mean_force":0.0512,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46726,0.04664,0.15352]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16740.0,"contact_point_centroid":[0.46723,0.02748,0.15606],"force_p95":0.07513,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25596,"mean_force":0.05077,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46727,0.04664,0.15411]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48276,0.04846,-0.00216],"force_p95":0.16805,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24893,"mean_force":0.13482,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47167,0.04708,0.03137]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12535.0,"contact_point_centroid":[0.54933,0.19944,0.28315],"force_p95":0.07038,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18338,"mean_force":0.04851,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.54893,0.18045,0.28261]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11106.0,"contact_point_centroid":[0.54746,0.1586,0.28525],"force_p95":0.08955,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18318,"mean_force":0.05551,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.54724,0.17778,0.28429]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8641.0,"contact_point_centroid":[0.57279,0.24006,0.24536],"force_p95":0.07401,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16028,"mean_force":0.05024,"phase_index":6.0,"phase_name":"hold_at_goal","phase_type":"grasp","tcp_position_centroid":[0.57201,0.22129,0.2455]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6599.0,"contact_point_centroid":[0.57203,0.20218,0.24621],"force_p95":0.09215,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15996,"mean_force":0.06426,"phase_index":6.0,"phase_name":"hold_at_goal","phase_type":"grasp","tcp_position_centroid":[0.57204,0.2213,0.24558]},{"body_a":"world","body_b":"grasp_target","contact_count":836.0,"contact_point_centroid":[0.4827,0.04873,-0.00185],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12321,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49123,0.01848,0.28274]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5013.0,"contact_point_centroid":[0.47029,0.02773,0.03295],"force_p95":0.07041,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1302,"mean_force":0.04304,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47054,0.04697,0.03023]},{"body_a":"world","body_b":"grasp_target","contact_count":3096.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47963,0.04326,0.15087]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21849.0,"contact_point_centroid":[0.49501,0.07414,0.29702],"force_p95":0.06687,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08497,"mean_force":0.04498,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49502,0.09329,0.29546]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5535.0,"contact_point_centroid":[0.4701,0.06632,0.03234],"force_p95":0.07045,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08102,"mean_force":0.04107,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47055,0.04697,0.03024]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20668.0,"contact_point_centroid":[0.49506,0.11239,0.29668],"force_p95":0.06787,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08076,"mean_force":0.0477,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49495,0.09318,0.29541]}],"total_contact_groups":14},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57234,0.22059,0.22124],"final_tcp_position":[0.576,0.22291,0.25677],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":9.79528,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":210.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":9.79528,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":836.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48331,0.03897,0.26632],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.2405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":774.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3096.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47836,0.04774,0.03824],"tcp_start":[0.48331,0.03897,0.26632],"tcp_to_object_dist_end":0.013,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48261,0.04721,0.02545],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29135,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16075,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12348.0,"raw_peak_contact_force":0.24893,"subtask_id":"grasp_1","tcp_end":[0.47052,0.04697,0.03021],"tcp_start":[0.47836,0.04774,0.03824],"tcp_to_object_dist_end":0.013,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":828.0,"n_steps_budget":1000.0,"object_pos_end":[0.4773,0.04677,0.2659],"object_pos_start":[0.48261,0.04721,0.02545],"object_to_goal_dist_end":0.21294,"object_to_goal_dist_start":0.29135,"object_z_max":0.26562,"peak_contact_force":0.07031,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33638.0,"raw_peak_contact_force":0.59473,"tcp_end":[0.46801,0.04671,0.27647],"tcp_start":[0.47052,0.04697,0.03021],"tcp_to_object_dist_end":0.01408,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52606,0.1342,0.29925],"object_pos_start":[0.4773,0.04677,0.2659],"object_to_goal_dist_end":0.12963,"object_to_goal_dist_start":0.21294,"object_z_max":0.29923,"peak_contact_force":0.06736,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":42517.0,"raw_peak_contact_force":0.08497,"subtask_id":"transport_arc","tcp_end":[0.52089,0.13433,0.31603],"tcp_start":[0.46801,0.04671,0.27647],"tcp_to_object_dist_end":0.01755,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":609.0,"n_steps_budget":1000.0,"object_pos_end":[0.57866,0.22268,0.23703],"object_pos_start":[0.52606,0.1342,0.29925],"object_to_goal_dist_end":0.00955,"object_to_goal_dist_start":0.12963,"object_z_max":0.29925,"peak_contact_force":0.0917,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":23641.0,"raw_peak_contact_force":0.18338,"tcp_end":[0.576,0.22291,0.25677],"tcp_start":[0.52089,0.13433,0.31603],"tcp_to_object_dist_end":0.01993,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57234,0.22059,0.22124],"object_pos_start":[0.57866,0.22268,0.23703],"object_to_goal_dist_end":0.01564,"object_to_goal_dist_start":0.00955,"object_z_max":0.23703,"peak_contact_force":0.09857,"phase_name":"hold_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":15240.0,"raw_peak_contact_force":0.16028,"tcp_end":[0.57124,0.22095,0.24335],"tcp_start":[0.576,0.22291,0.25677],"tcp_to_object_dist_end":0.02214,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50292,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.20798,"approach_1.approach_tol":0.01985,"approach_1.speed":0.1344,"descend_1.descend_speed":0.06189,"descend_1.descend_tol":0.02999,"descend_1.grasp_z_offset":0.0104,"grasp_1.grasp_duration":1.25232,"hold_at_goal.hold_duration":0.50885,"lift_1.lift_height":0.14479,"lift_1.lift_speed":0.06024,"lift_1.lift_tol":0.02118,"place_1.place_speed":0.19154,"place_1.place_tol":0.03768,"place_1.place_z_offset":0.04119,"transport_arc.transport_altitude":0.16101,"transport_arc.transport_speed":0.40012,"transport_arc.transport_tol":0.0309},"optimized_scores":{"best_composite_score":-0.393,"best_fitness_score":0.607,"best_task_score":0.26599},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2618.0,"contact_point_centroid":[0.59641,0.17648,-0.0025],"force_p95":0.13123,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.1857,"mean_force":0.14479,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.59234,0.18768,0.25184]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.53398,-0.02088,-0.0014],"force_p95":0.4478,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54197,"mean_force":0.1388,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52198,-0.02082,0.03603]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8281.0,"contact_point_centroid":[0.54136,0.01849,0.20485],"force_p95":0.13071,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38642,"mean_force":0.07833,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53794,0.03739,0.20345]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10170.0,"contact_point_centroid":[0.54251,0.05946,0.20715],"force_p95":0.10191,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32294,"mean_force":0.0663,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5392,0.04087,0.20627]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8104.0,"contact_point_centroid":[0.52013,-0.00164,0.10025],"force_p95":0.08213,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31562,"mean_force":0.05823,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51931,-0.02076,0.09781]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8653.0,"contact_point_centroid":[0.52014,-0.0398,0.09702],"force_p95":0.0795,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29946,"mean_force":0.05538,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51933,-0.02076,0.09495]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02117,-0.00204],"force_p95":0.13645,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16815,"mean_force":0.12649,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52439,-0.02086,0.0363]},{"body_a":"world","body_b":"grasp_target","contact_count":1016.0,"contact_point_centroid":[0.53702,-0.02132,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51308,-0.00879,0.27006]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4106.0,"contact_point_centroid":[0.52396,-0.00164,0.03764],"force_p95":0.07709,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12381,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52317,-0.02084,0.0349]},{"body_a":"world","body_b":"grasp_target","contact_count":2524.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52872,-0.01949,0.14196]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.59641,0.17643,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"hold_at_goal","phase_type":"grasp","tcp_position_centroid":[0.6019,0.22179,0.22836]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4901.0,"contact_point_centroid":[0.52397,-0.03993,0.03671],"force_p95":0.06915,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09017,"mean_force":0.04472,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52318,-0.02084,0.0349]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2662.0,"contact_point_centroid":[0.59354,0.18962,0.25339],"force_p95":0.01124,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01654,"mean_force":0.01059,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.59308,0.18961,0.25121]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1936.0,"contact_point_centroid":[0.60241,0.22182,0.2306],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01269,"mean_force":0.01037,"phase_index":6.0,"phase_name":"hold_at_goal","phase_type":"grasp","tcp_position_centroid":[0.6019,0.22179,0.22836]}],"total_contact_groups":14},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.59641,0.17643,0.01602],"final_tcp_position":[0.60614,0.22348,0.24059],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":2.1857,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":255.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1016.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52836,-0.01805,0.24127],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21545,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":631.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2524.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53165,-0.02099,0.04475],"tcp_start":[0.52836,-0.01805,0.24127],"tcp_to_object_dist_end":0.01949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53691,-0.02076,0.02583],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31642,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13371,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10807.0,"raw_peak_contact_force":0.16815,"subtask_id":"grasp_1","tcp_end":[0.52314,-0.02084,0.03486],"tcp_start":[0.53165,-0.02099,0.04475],"tcp_to_object_dist_end":0.01647,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":451.0,"n_steps_budget":1000.0,"object_pos_end":[0.5307,-0.02078,0.14693],"object_pos_start":[0.53691,-0.02076,0.02583],"object_to_goal_dist_end":0.26789,"object_to_goal_dist_start":0.31642,"object_z_max":0.14667,"peak_contact_force":0.08057,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":16843.0,"raw_peak_contact_force":0.54197,"tcp_end":[0.51941,-0.02075,0.16023],"tcp_start":[0.52314,-0.02084,0.03486],"tcp_to_object_dist_end":0.01745,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":700.0,"n_steps_budget":1000.0,"object_pos_end":[0.58549,0.13515,0.24217],"object_pos_start":[0.5307,-0.02078,0.14693],"object_to_goal_dist_end":0.10198,"object_to_goal_dist_start":0.26789,"object_z_max":0.24752,"peak_contact_force":0.0,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":18451.0,"raw_peak_contact_force":0.38642,"subtask_id":"transport_arc","tcp_end":[0.57155,0.12793,0.27781],"tcp_start":[0.51941,-0.02075,0.16023],"tcp_to_object_dist_end":0.03895,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":749.0,"n_steps_budget":1000.0,"object_pos_end":[0.59641,0.17643,0.01602],"object_pos_start":[0.58549,0.13515,0.24217],"object_to_goal_dist_end":0.19864,"object_to_goal_dist_start":0.10198,"object_z_max":0.24217,"peak_contact_force":0.12263,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5280.0,"raw_peak_contact_force":2.1857,"tcp_end":[0.60614,0.22348,0.24059],"tcp_start":[0.57155,0.12793,0.27781],"tcp_to_object_dist_end":0.22965,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59641,0.17643,0.01602],"object_pos_start":[0.59641,0.17643,0.01602],"object_to_goal_dist_end":0.19864,"object_to_goal_dist_start":0.19864,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"hold_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":3736.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60112,0.22146,0.22614],"tcp_start":[0.60614,0.22348,0.24059],"tcp_to_object_dist_end":0.21494,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```