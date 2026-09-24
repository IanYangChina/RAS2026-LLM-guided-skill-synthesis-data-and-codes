## Search State

- **Seed**: 7
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 17 | -0.3643 | 0.33 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 17 | -0.1693 | 0.71 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 17 | -0.3888 | 0.27 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 16 | -0.0055 | 0.89 | ✅ accepted |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 19 | -0.3651 | 0.30 | ✅ accepted |

**Proposal policy**: task_score is 0.33 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.364) — your mutation base

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

- **Composite score**: -0.364
- **task_score** (E): 0.326
- **fitness_score**: 0.636  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 1.000

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0399 |
| descend_1 | 1.00 | 1.00 | 0.2611 |
| grasp_1 | 1.00 | 1.00 | 0.0122 |
| lift_1 | 1.00 | 1.00 | 0.1820 |
| transport_arc | 0.00 | 1.00 | 0.0978 |
| place_1 | 1.00 | 0.67 | 0.1461 |
| release_1 | 1.00 | 1.00 | 0.0209 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.019, 0.307) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.507, 0.019, 0.307)→(0.506, 0.022, 0.046) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.022, 0.046)→(0.498, 0.022, 0.037) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.274 | 1.00 / 43.667 | 0.146 | 0.206 |
| lift_1 | lift | 1.00 / step_budget | (0.498, 0.022, 0.037)→(0.495, 0.021, 0.219) | (0.511, 0.022, 0.026)→(0.503, 0.021, 0.203) | 0.274→0.226 | 1.00 / 39.000 | 0.076 | 0.482 |
| transport_arc | approach | 0.00 / step_budget | (0.495, 0.021, 0.219)→(0.534, 0.086, 0.274) | (0.503, 0.021, 0.203)→(0.541, 0.086, 0.251) | 0.226→0.162 | 1.00 / 29.333 | 0.094 | 0.138 |
| place_1 | descend | 1.00 / step_budget | (0.534, 0.086, 0.274)→(0.593, 0.193, 0.216) | (0.541, 0.086, 0.251)→(0.600, 0.196, 0.159) | 0.162→0.039 | 0.67 / 15.667 | 0.073 | 0.254 |
| release_1 | release | 1.00 / step_budget | (0.593, 0.193, 0.216)→(0.589, 0.191, 0.236) | (0.600, 0.196, 0.159)→(0.594, 0.199, 0.021) | 0.039→0.174 | 1.00 / 3.000 | 0.157 | 1.693 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.452
- phase_score: 0.317
- phase_breakdown.approach_1_score: 0.004
- phase_breakdown.transport_arc_score: 0.038
- phase_breakdown.release_1_score: 0.364
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.908
- grasp_place_fitness: 0.694

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.694
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.452
- **Median Q (composite search score)**: -0.384
- **K-run variance**: 0.0018
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43333,"average_solve_count":210.0,"average_success_count":210.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.278,"approach_1.approach_tol":0.01684,"approach_1.speed":0.14215,"descend_1.descend_speed":0.11401,"descend_1.descend_tol":0.03493,"descend_1.grasp_z_offset":0.016,"grasp_1.grasp_duration":0.67129,"lift_1.lift_height":0.21841,"lift_1.lift_speed":0.05206,"lift_1.lift_tol":0.02207,"place_1.place_speed":0.08098,"place_1.place_tol":0.02262,"place_1.place_z_offset":0.03038,"release_1.release_duration":1.03963,"transport_arc.transport_altitude":0.18465,"transport_arc.transport_speed":0.11196,"transport_arc.transport_tol":0.03328},"optimized_scores":{"best_composite_score":-0.30599,"best_fitness_score":0.69401,"best_task_score":0.45172},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":191.0,"contact_point_centroid":[0.60627,0.16563,-0.00681],"force_p95":1.19287,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.5248,"mean_force":0.36331,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61365,0.1654,0.18275]},{"body_a":"world","body_b":"grasp_target","contact_count":87.0,"contact_point_centroid":[0.50939,0.03796,-0.00148],"force_p95":0.44505,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48163,"mean_force":0.13552,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49853,0.03828,0.04277]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":553.0,"contact_point_centroid":[0.62179,0.18494,0.16564],"force_p95":0.12592,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4353,"mean_force":0.09219,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61747,0.16669,0.1694]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":543.0,"contact_point_centroid":[0.62198,0.14841,0.16593],"force_p95":0.12365,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39371,"mean_force":0.09114,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61748,0.16669,0.16939]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13624.0,"contact_point_centroid":[0.49641,0.05719,0.13833],"force_p95":0.07935,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30248,"mean_force":0.0541,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49616,0.03809,0.13621]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13208.0,"contact_point_centroid":[0.49659,0.01897,0.14171],"force_p95":0.07968,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29238,"mean_force":0.055,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49618,0.03809,0.13919]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6846.0,"contact_point_centroid":[0.59246,0.11671,0.22672],"force_p95":0.12564,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2398,"mean_force":0.07883,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.58809,0.13529,0.22753]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6789.0,"contact_point_centroid":[0.59298,0.15442,0.22557],"force_p95":0.12551,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23236,"mean_force":0.07981,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.58859,0.13581,0.22661]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51255,0.03954,-0.00211],"force_p95":0.15562,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21634,"mean_force":0.13123,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50085,0.03848,0.04285]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17916.0,"contact_point_centroid":[0.53095,0.092,0.25907],"force_p95":0.09179,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17935,"mean_force":0.05546,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52825,0.073,0.25769]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17071.0,"contact_point_centroid":[0.53161,0.05452,0.25966],"force_p95":0.09217,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17925,"mean_force":0.05824,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52879,0.07353,0.25806]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4090.0,"contact_point_centroid":[0.50013,0.01911,0.04438],"force_p95":0.08153,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15189,"mean_force":0.05212,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49969,0.03838,0.04157]},{"body_a":"world","body_b":"grasp_target","contact_count":1020.0,"contact_point_centroid":[0.51251,0.03972,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50352,0.01795,0.29938]},{"body_a":"world","body_b":"grasp_target","contact_count":2996.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50701,0.03645,0.17462]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5468.0,"contact_point_centroid":[0.49944,0.05749,0.0442],"force_p95":0.06868,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07698,"mean_force":0.04066,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49969,0.03838,0.04158]}],"total_contact_groups":15},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61218,0.1645,0.02709],"final_tcp_position":[0.61942,0.1671,0.1736],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.5248,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":256.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50821,0.03401,0.30109],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27516,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":749.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2996.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50777,0.03904,0.05061],"tcp_start":[0.50821,0.03401,0.30109],"tcp_to_object_dist_end":0.02505,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51246,0.03858,0.0256],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2132,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15047,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11358.0,"raw_peak_contact_force":0.21634,"subtask_id":"grasp_1","tcp_end":[0.49966,0.03838,0.04154],"tcp_start":[0.50777,0.03904,0.05061],"tcp_to_object_dist_end":0.02044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":694.0,"n_steps_budget":1000.0,"object_pos_end":[0.50459,0.03821,0.21918],"object_pos_start":[0.51246,0.03858,0.0256],"object_to_goal_dist_end":0.19663,"object_to_goal_dist_start":0.2132,"object_z_max":0.21891,"peak_contact_force":0.07301,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":26919.0,"raw_peak_contact_force":0.48163,"tcp_end":[0.49675,0.03813,0.24027],"tcp_start":[0.49966,0.03838,0.04154],"tcp_to_object_dist_end":0.0225,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56885,0.10795,0.25155],"object_pos_start":[0.50459,0.03821,0.21918],"object_to_goal_dist_end":0.13771,"object_to_goal_dist_start":0.19663,"object_z_max":0.25152,"peak_contact_force":0.09728,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34987.0,"raw_peak_contact_force":0.17935,"subtask_id":"transport_arc","tcp_end":[0.56268,0.10796,0.28007],"tcp_start":[0.49675,0.03813,0.24027],"tcp_to_object_dist_end":0.02917,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":554.0,"n_steps_budget":1000.0,"object_pos_end":[0.62436,0.16697,0.14073],"object_pos_start":[0.56885,0.10795,0.25155],"object_to_goal_dist_end":0.00772,"object_to_goal_dist_start":0.13771,"object_z_max":0.25155,"peak_contact_force":0.12498,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":13635.0,"raw_peak_contact_force":0.2398,"subtask_id":"release_1","tcp_end":[0.61942,0.1671,0.1736],"tcp_start":[0.56268,0.10796,0.28007],"tcp_to_object_dist_end":0.03324,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61218,0.1645,0.02709],"object_pos_start":[0.62436,0.16697,0.14073],"object_to_goal_dist_end":0.1192,"object_to_goal_dist_start":0.00772,"object_z_max":0.14073,"peak_contact_force":0.18289,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1287.0,"raw_peak_contact_force":1.5248,"tcp_end":[0.6136,0.16539,0.19309],"tcp_start":[0.61942,0.1671,0.1736],"tcp_to_object_dist_end":0.16601,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.06148,"average_solve_count":244.0,"average_success_count":244.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.28938,"approach_1.approach_tol":0.01836,"approach_1.speed":0.11725,"descend_1.descend_speed":0.13003,"descend_1.descend_tol":0.03287,"descend_1.grasp_z_offset":0.00567,"grasp_1.grasp_duration":1.85575,"lift_1.lift_height":0.16232,"lift_1.lift_speed":0.0104,"lift_1.lift_tol":0.04298,"place_1.place_speed":0.10074,"place_1.place_tol":0.034,"place_1.place_z_offset":0.03573,"release_1.release_duration":0.72887,"transport_arc.transport_altitude":0.27726,"transport_arc.transport_speed":0.04301,"transport_arc.transport_tol":0.02985},"optimized_scores":{"best_composite_score":-0.40288,"best_fitness_score":0.59712,"best_task_score":0.23893},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":642.0,"contact_point_centroid":[0.57661,0.2199,-0.00406],"force_p95":0.8804,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.72536,"mean_force":0.20352,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55428,0.19373,0.25802]},{"body_a":"world","body_b":"grasp_target","contact_count":100.0,"contact_point_centroid":[0.47892,0.04677,-0.00162],"force_p95":0.45135,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48863,"mean_force":0.22017,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46931,0.04709,0.03337]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9512.0,"contact_point_centroid":[0.52512,0.12017,0.25072],"force_p95":0.14879,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26492,"mean_force":0.09126,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.52102,0.13876,0.25125]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10028.0,"contact_point_centroid":[0.4671,0.06601,0.1039],"force_p95":0.07772,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25255,"mean_force":0.05238,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46692,0.04685,0.10209]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48274,0.04852,-0.00214],"force_p95":0.1613,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23896,"mean_force":0.13301,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47156,0.04732,0.03365]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10020.0,"contact_point_centroid":[0.46713,0.02771,0.10412],"force_p95":0.0756,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21951,"mean_force":0.05162,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46692,0.04685,0.10215]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11159.0,"contact_point_centroid":[0.52684,0.15854,0.25093],"force_p95":0.12779,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20186,"mean_force":0.07816,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.52194,0.1402,0.25132]},{"body_a":"world","body_b":"grasp_target","contact_count":1244.0,"contact_point_centroid":[0.4827,0.04873,-0.00189],"force_p95":0.13606,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12302,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48989,0.02204,0.30452]},{"body_a":"world","body_b":"grasp_target","contact_count":3272.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47938,0.04519,0.17445]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17127.0,"contact_point_centroid":[0.48,0.05055,0.21424],"force_p95":0.08505,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12209,"mean_force":0.05732,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.47843,0.06953,0.21251]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5031.0,"contact_point_centroid":[0.47022,0.02797,0.0353],"force_p95":0.06954,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11921,"mean_force":0.04298,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47045,0.04721,0.03252]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17100.0,"contact_point_centroid":[0.48025,0.08885,0.21452],"force_p95":0.0828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11212,"mean_force":0.05767,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.47862,0.06984,0.21305]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5505.0,"contact_point_centroid":[0.47003,0.06653,0.0347],"force_p95":0.06958,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07809,"mean_force":0.04104,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47045,0.04721,0.03252]}],"total_contact_groups":13},"final_pose_error":0.04294,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.57669,0.2197,0.016],"final_tcp_position":[0.55772,0.19503,0.25543],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.72536,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":312.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1244.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48239,0.04255,0.31157],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.28561,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":818.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3272.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47829,0.04798,0.04055],"tcp_start":[0.48239,0.04255,0.31157],"tcp_to_object_dist_end":0.0152,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48262,0.04746,0.02552],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29114,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15532,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12336.0,"raw_peak_contact_force":0.23896,"subtask_id":"grasp_1","tcp_end":[0.47042,0.04721,0.03249],"tcp_start":[0.47829,0.04798,0.04055],"tcp_to_object_dist_end":0.01405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":500.0,"n_steps_budget":1000.0,"object_pos_end":[0.47677,0.04695,0.16567],"object_pos_start":[0.48262,0.04746,0.02552],"object_to_goal_dist_end":0.21985,"object_to_goal_dist_start":0.29114,"object_z_max":0.1654,"peak_contact_force":0.07523,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20148.0,"raw_peak_contact_force":0.48863,"tcp_end":[0.46705,0.04687,0.17538],"tcp_start":[0.47042,0.04721,0.03249],"tcp_to_object_dist_end":0.01374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50218,0.09169,0.23415],"object_pos_start":[0.47677,0.04695,0.16567],"object_to_goal_dist_end":0.15867,"object_to_goal_dist_start":0.21985,"object_z_max":0.2341,"peak_contact_force":0.09562,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34227.0,"raw_peak_contact_force":0.12209,"subtask_id":"transport_arc","tcp_end":[0.49266,0.09174,0.25253],"tcp_start":[0.46705,0.04687,0.17538],"tcp_to_object_dist_end":0.0207,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56954,0.20621,0.146],"object_pos_start":[0.50218,0.09169,0.23415],"object_to_goal_dist_end":0.08833,"object_to_goal_dist_start":0.15867,"object_z_max":0.23415,"peak_contact_force":0.0,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":20671.0,"raw_peak_contact_force":0.26492,"subtask_id":"release_1","tcp_end":[0.55772,0.19503,0.25543],"tcp_start":[0.49266,0.09174,0.25253],"tcp_to_object_dist_end":0.11063,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57669,0.2197,0.016],"object_pos_start":[0.56954,0.20621,0.146],"object_to_goal_dist_end":0.21474,"object_to_goal_dist_start":0.08833,"object_z_max":0.146,"peak_contact_force":0.12293,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":642.0,"raw_peak_contact_force":1.72536,"tcp_end":[0.55377,0.19348,0.2771],"tcp_start":[0.55772,0.19503,0.25543],"tcp_to_object_dist_end":0.26341,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48276,"average_solve_count":232.0,"average_success_count":232.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.28556,"approach_1.approach_tol":0.01803,"approach_1.speed":0.10788,"descend_1.descend_speed":0.16709,"descend_1.descend_tol":0.01649,"descend_1.grasp_z_offset":0.01183,"grasp_1.grasp_duration":1.98163,"lift_1.lift_height":0.22389,"lift_1.lift_speed":0.01353,"lift_1.lift_tol":0.02831,"place_1.place_speed":0.15027,"place_1.place_tol":0.02536,"place_1.place_z_offset":0.01556,"release_1.release_duration":1.72448,"transport_arc.transport_altitude":0.20717,"transport_arc.transport_speed":0.07009,"transport_arc.transport_tol":0.02513},"optimized_scores":{"best_composite_score":-0.38401,"best_fitness_score":0.61599,"best_task_score":0.28588},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":164.0,"contact_point_centroid":[0.58674,0.21458,-0.00912],"force_p95":1.46298,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.8283,"mean_force":0.46183,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.59834,0.21399,0.23107]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.53301,-0.02051,-0.00147],"force_p95":0.44684,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47427,"mean_force":0.18733,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52224,-0.02093,0.03719]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14100.0,"contact_point_centroid":[0.52001,-0.00174,0.13752],"force_p95":0.07768,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27917,"mean_force":0.05445,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51972,-0.02087,0.13504]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14701.0,"contact_point_centroid":[0.51997,-0.03996,0.13595],"force_p95":0.07641,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26271,"mean_force":0.05273,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51971,-0.02087,0.1338]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17103.0,"contact_point_centroid":[0.5796,0.12501,0.24967],"force_p95":0.08531,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25843,"mean_force":0.05709,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.57626,0.14394,0.24817]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16087.0,"contact_point_centroid":[0.57801,0.16068,0.24928],"force_p95":0.08615,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21052,"mean_force":0.06122,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.57543,0.14169,0.24912]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53702,-0.0212,-0.00204],"force_p95":0.13476,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16331,"mean_force":0.12605,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52462,-0.02098,0.03774]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":902.0,"contact_point_centroid":[0.60386,0.2344,0.21285],"force_p95":0.09253,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14512,"mean_force":0.05687,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60152,0.21544,0.21461]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":902.0,"contact_point_centroid":[0.60433,0.19655,0.21377],"force_p95":0.09397,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14397,"mean_force":0.05572,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60155,0.21545,0.21467]},{"body_a":"world","body_b":"grasp_target","contact_count":1488.0,"contact_point_centroid":[0.53702,-0.02132,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51622,-0.01062,0.30293]},{"body_a":"world","body_b":"grasp_target","contact_count":2812.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53058,-0.02017,0.17562]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4112.0,"contact_point_centroid":[0.5241,-0.00175,0.03908],"force_p95":0.07654,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12235,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52341,-0.02095,0.03634]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17326.0,"contact_point_centroid":[0.53414,0.00198,0.26607],"force_p95":0.08285,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11175,"mean_force":0.05619,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53287,0.02106,0.26402]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18533.0,"contact_point_centroid":[0.53407,0.03995,0.26551],"force_p95":0.07699,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09267,"mean_force":0.05236,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53281,0.02096,0.26392]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4888.0,"contact_point_centroid":[0.52413,-0.04003,0.03816],"force_p95":0.06883,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08983,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52341,-0.02095,0.03634]}],"total_contact_groups":15},"final_pose_error":0.01471,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.59443,0.21324,0.02082],"final_tcp_position":[0.603,0.21584,0.21837],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.8283,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":373.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1488.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53104,-0.01928,0.30782],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.28188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":703.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2812.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53193,-0.02111,0.04625],"tcp_start":[0.53104,-0.01928,0.30782],"tcp_to_object_dist_end":0.02086,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53691,-0.02086,0.02584],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31649,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13241,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10800.0,"raw_peak_contact_force":0.16331,"subtask_id":"grasp_1","tcp_end":[0.52338,-0.02095,0.03631],"tcp_start":[0.53193,-0.02111,0.04625],"tcp_to_object_dist_end":0.01711,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":745.0,"n_steps_budget":1000.0,"object_pos_end":[0.52908,-0.02087,0.22475],"object_pos_start":[0.53691,-0.02086,0.02584],"object_to_goal_dist_end":0.26213,"object_to_goal_dist_start":0.31649,"object_z_max":0.22449,"peak_contact_force":0.08006,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":28893.0,"raw_peak_contact_force":0.47427,"tcp_end":[0.5204,-0.02088,0.24067],"tcp_start":[0.52338,-0.02095,0.03631],"tcp_to_object_dist_end":0.01813,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55073,0.05815,0.26728],"object_pos_start":[0.52908,-0.02087,0.22475],"object_to_goal_dist_end":0.18947,"object_to_goal_dist_start":0.26213,"object_z_max":0.26722,"peak_contact_force":0.08892,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35859.0,"raw_peak_contact_force":0.11175,"subtask_id":"transport_arc","tcp_end":[0.5465,0.05829,0.28946],"tcp_start":[0.5204,-0.02088,0.24067],"tcp_to_object_dist_end":0.02258,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60527,0.2156,0.19097],"object_pos_start":[0.55073,0.05815,0.26728],"object_to_goal_dist_end":0.02106,"object_to_goal_dist_start":0.18947,"object_z_max":0.26728,"peak_contact_force":0.09309,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":33190.0,"raw_peak_contact_force":0.25843,"subtask_id":"release_1","tcp_end":[0.603,0.21584,0.21837],"tcp_start":[0.5465,0.05829,0.28946],"tcp_to_object_dist_end":0.0275,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59443,0.21324,0.02082],"object_pos_start":[0.60527,0.2156,0.19097],"object_to_goal_dist_end":0.18783,"object_to_goal_dist_start":0.02106,"object_z_max":0.19097,"peak_contact_force":0.16455,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1968.0,"raw_peak_contact_force":1.8283,"tcp_end":[0.59832,0.21398,0.23804],"tcp_start":[0.603,0.21584,0.21837],"tcp_to_object_dist_end":0.21726,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```