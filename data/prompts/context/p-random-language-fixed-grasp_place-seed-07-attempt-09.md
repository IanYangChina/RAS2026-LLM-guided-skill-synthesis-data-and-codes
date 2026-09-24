## Search State

- **Seed**: 7
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 16 | -0.0176 | 0.85 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 17 | -0.3643 | 0.33 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → grasp | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 17 | -0.1693 | 0.71 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 17 | -0.3888 | 0.27 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 16 | -0.0055 | 0.89 | ✅ accepted |

**Proposal policy**: task_score is 0.85 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.018) — your mutation base

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

- **Composite score**: -0.018
- **task_score** (E): 0.850
- **fitness_score**: 0.902  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.920

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0579 |
| descend_1 | 1.00 | 1.00 | 0.2185 |
| grasp_1 | 1.00 | 1.00 | 0.0122 |
| lift_1 | 1.00 | 1.00 | 0.1850 |
| transport_arc | 0.00 | 1.00 | 0.0904 |
| place_1 | 1.00 | 1.00 | 0.1384 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.018, 0.257) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.018, 0.257)→(0.506, 0.022, 0.039) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 9.469 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.022, 0.039)→(0.498, 0.021, 0.030) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.274 | 1.00 / 43.000 | 0.149 | 0.221 |
| lift_1 | lift | 1.00 / step_budget | (0.498, 0.021, 0.030)→(0.494, 0.021, 0.215) | (0.511, 0.022, 0.026)→(0.505, 0.021, 0.205) | 0.274→0.219 | 1.00 / 37.000 | 0.080 | 0.604 |
| transport_arc | approach | 0.00 / guard_failure | (0.494, 0.021, 0.215)→(0.533, 0.092, 0.247) | (0.505, 0.021, 0.205)→(0.542, 0.092, 0.230) | 0.219→0.147 | 1.00 / 33.667 | 0.031 | 0.115 |
| place_1 | descend | 1.00 / step_budget | (0.533, 0.092, 0.247)→(0.597, 0.198, 0.205) | (0.542, 0.092, 0.230)→(0.600, 0.199, 0.179) | 0.147→0.031 | 1.00 / 27.667 | 0.132 | 0.196 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.180
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.279
- phase_breakdown.approach_1_score: 0.006
- phase_breakdown.transport_arc_score: 0.103
- phase_breakdown.release_1_score: 0.000
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.724
- grasp_place_fitness: 0.979

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.979
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: -0.053
- **K-run variance**: 0.0029
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.351


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56863,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.255,"approach_1.approach_tol":0.02806,"approach_1.speed":0.14574,"descend_1.descend_speed":0.13482,"descend_1.descend_tol":0.01059,"descend_1.grasp_z_offset":0.00012,"grasp_1.grasp_duration":1.97026,"lift_1.lift_height":0.14954,"lift_1.lift_speed":0.06096,"lift_1.lift_tol":0.01334,"place_1.place_speed":0.07943,"place_1.place_tol":0.04625,"place_1.place_z_offset":0.05159,"transport_arc.transport_altitude":0.137,"transport_arc.transport_speed":0.15794,"transport_arc.transport_tol":0.02369},"optimized_scores":{"best_composite_score":0.05906,"best_fitness_score":0.97906,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.50911,0.03752,-0.00149],"force_p95":0.57138,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69344,"mean_force":0.18244,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49813,0.03812,0.02694]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8890.0,"contact_point_centroid":[0.49603,0.05698,0.08928],"force_p95":0.07915,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32294,"mean_force":0.05347,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49557,0.03791,0.08722]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8179.0,"contact_point_centroid":[0.49616,0.01877,0.09199],"force_p95":0.08295,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31002,"mean_force":0.05673,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49558,0.03791,0.08937]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51256,0.03937,-0.00214],"force_p95":0.16272,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24725,"mean_force":0.13343,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50049,0.03832,0.02696]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12138.0,"contact_point_centroid":[0.599,0.1616,0.19882],"force_p95":0.12101,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22695,"mean_force":0.0698,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.59508,0.14315,0.19944]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9949.0,"contact_point_centroid":[0.59803,0.12387,0.19869],"force_p95":0.14769,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21887,"mean_force":0.08543,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.59456,0.14264,0.19966]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4051.0,"contact_point_centroid":[0.4999,0.01903,0.02849],"force_p95":0.08117,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14666,"mean_force":0.05189,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4993,0.03823,0.02569]},{"body_a":"world","body_b":"grasp_target","contact_count":748.0,"contact_point_centroid":[0.51251,0.03972,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12328,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50297,0.01578,0.2902]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13798.0,"contact_point_centroid":[0.5301,0.05494,0.18575],"force_p95":0.09495,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12417,"mean_force":0.06539,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5281,0.07396,0.18413]},{"body_a":"world","body_b":"grasp_target","contact_count":2928.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5064,0.03524,0.15715]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15917.0,"contact_point_centroid":[0.53152,0.09413,0.18608],"force_p95":0.08353,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11864,"mean_force":0.05788,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52938,0.0753,0.1853]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5009.0,"contact_point_centroid":[0.49986,0.0574,0.02751],"force_p95":0.0736,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08841,"mean_force":0.04482,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4993,0.03823,0.0257]}],"total_contact_groups":12},"final_pose_error":0.01026,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62682,0.17046,0.16128],"final_tcp_position":[0.62231,0.16993,0.18819],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.69344,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":188.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":748.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50735,0.03173,0.28233],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25649,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":732.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2928.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50757,0.0389,0.03467],"tcp_start":[0.50735,0.03173,0.28233],"tcp_to_object_dist_end":0.01,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51239,0.03821,0.02555],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2135,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15377,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10860.0,"raw_peak_contact_force":0.24725,"subtask_id":"grasp_1","tcp_end":[0.49927,0.03822,0.02566],"tcp_start":[0.50757,0.0389,0.03467],"tcp_to_object_dist_end":0.01312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":448.0,"n_steps_budget":1000.0,"object_pos_end":[0.50843,0.03803,0.15117],"object_pos_start":[0.51239,0.03821,0.02555],"object_to_goal_dist_end":0.17977,"object_to_goal_dist_start":0.2135,"object_z_max":0.1509,"peak_contact_force":0.07955,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17154.0,"raw_peak_contact_force":0.69344,"tcp_end":[0.49562,0.03792,0.15557],"tcp_start":[0.49927,0.03822,0.02566],"tcp_to_object_dist_end":0.01354,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":915.0,"n_steps_budget":1000.0,"object_pos_end":[0.57369,0.11186,0.20015],"object_pos_start":[0.50843,0.03803,0.15117],"object_to_goal_dist_end":0.09809,"object_to_goal_dist_start":0.17977,"object_z_max":0.20009,"peak_contact_force":0.0,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29715.0,"raw_peak_contact_force":0.12417,"subtask_id":"transport_arc","tcp_end":[0.56565,0.11202,0.21872],"tcp_start":[0.49562,0.03792,0.15557],"tcp_to_object_dist_end":0.02023,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":12.0,"n_steps":913.0,"n_steps_budget":1000.0,"object_pos_end":[0.62682,0.17046,0.16128],"object_pos_start":[0.57369,0.11186,0.20015],"object_to_goal_dist_end":0.0164,"object_to_goal_dist_start":0.09809,"object_z_max":0.20015,"peak_contact_force":0.20699,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":22087.0,"raw_peak_contact_force":0.22695,"tcp_end":[0.62231,0.16993,0.18819],"tcp_start":[0.56565,0.11202,0.21872],"tcp_to_object_dist_end":0.02729,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23767,"average_solve_count":223.0,"average_success_count":223.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.20827,"approach_1.approach_tol":0.02701,"approach_1.speed":0.10311,"descend_1.descend_speed":0.04375,"descend_1.descend_tol":0.01317,"descend_1.grasp_z_offset":0.00417,"grasp_1.grasp_duration":2.50413,"lift_1.lift_height":0.20942,"lift_1.lift_speed":0.05592,"lift_1.lift_tol":0.03049,"place_1.place_speed":0.19596,"place_1.place_tol":0.02745,"place_1.place_z_offset":0.00767,"transport_arc.transport_altitude":0.26932,"transport_arc.transport_speed":0.07445,"transport_arc.transport_tol":0.00854},"optimized_scores":{"best_composite_score":-0.0589,"best_fitness_score":0.8611,"best_task_score":0.76493},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.47969,0.04647,-0.00152],"force_p95":0.51461,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60724,"mean_force":0.1594,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46933,0.04686,0.03227]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12403.0,"contact_point_centroid":[0.46709,0.06576,0.12291],"force_p95":0.07918,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31336,"mean_force":0.05343,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46697,0.04663,0.12077]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12180.0,"contact_point_centroid":[0.46724,0.02751,0.12645],"force_p95":0.07764,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2732,"mean_force":0.05369,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46698,0.04663,0.124]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48276,0.04847,-0.00216],"force_p95":0.16736,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24741,"mean_force":0.13464,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47152,0.04709,0.03206]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16498.0,"contact_point_centroid":[0.5195,0.11402,0.23007],"force_p95":0.09483,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20373,"mean_force":0.06263,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.5178,0.13321,0.22834]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21484.0,"contact_point_centroid":[0.51986,0.15448,0.2296],"force_p95":0.07601,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14822,"mean_force":0.04616,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.51935,0.13567,0.22833]},{"body_a":"world","body_b":"grasp_target","contact_count":932.0,"contact_point_centroid":[0.4827,0.04873,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12315,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49097,0.01913,0.27175]},{"body_a":"world","body_b":"grasp_target","contact_count":2808.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47921,0.04392,0.14002]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5014.0,"contact_point_centroid":[0.47018,0.02773,0.03377],"force_p95":0.0703,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12124,"mean_force":0.04305,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4704,0.04698,0.03092]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2560.0,"contact_point_centroid":[0.46981,0.03278,0.22771],"force_p95":0.0751,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10395,"mean_force":0.0505,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.4687,0.05173,0.22584]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2167.0,"contact_point_centroid":[0.46985,0.0709,0.22834],"force_p95":0.08009,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09652,"mean_force":0.05845,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46869,0.05171,0.22582]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5535.0,"contact_point_centroid":[0.47,0.06632,0.03315],"force_p95":0.07058,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08038,"mean_force":0.04105,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4704,0.04698,0.03093]}],"total_contact_groups":12},"final_pose_error":0.0322,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.56482,0.20403,0.20386],"final_tcp_position":[0.56349,0.20382,0.22963],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":28.16248,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":234.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":932.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48269,0.04031,0.24339],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21753,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":702.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":28.16248,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2808.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47825,0.04775,0.03894],"tcp_start":[0.48269,0.04031,0.24339],"tcp_to_object_dist_end":0.0137,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48262,0.04723,0.02545],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29133,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.1602,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12349.0,"raw_peak_contact_force":0.24741,"subtask_id":"grasp_1","tcp_end":[0.47037,0.04698,0.0309],"tcp_start":[0.47825,0.04775,0.03894],"tcp_to_object_dist_end":0.0134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":632.0,"n_steps_budget":1000.0,"object_pos_end":[0.47766,0.04682,0.20999],"object_pos_start":[0.48262,0.04723,0.02545],"object_to_goal_dist_end":0.21076,"object_to_goal_dist_start":0.29133,"object_z_max":0.20971,"peak_contact_force":0.08128,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24667.0,"raw_peak_contact_force":0.60724,"tcp_end":[0.46738,0.04667,0.22081],"tcp_start":[0.47037,0.04698,0.0309],"tcp_to_object_dist_end":0.01492,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":128.0,"n_steps_budget":1000.0,"object_pos_end":[0.48242,0.05647,0.21897],"object_pos_start":[0.47766,0.04682,0.20999],"object_to_goal_dist_end":0.19935,"object_to_goal_dist_start":0.21076,"object_z_max":0.21888,"peak_contact_force":0.0,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4727.0,"raw_peak_contact_force":0.10395,"subtask_id":"transport_arc","tcp_end":[0.47053,0.05621,0.23108],"tcp_start":[0.46738,0.04667,0.22081],"tcp_to_object_dist_end":0.01697,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56482,0.20403,0.20386],"object_pos_start":[0.48242,0.05647,0.21897],"object_to_goal_dist_end":0.04019,"object_to_goal_dist_start":0.19935,"object_z_max":0.21898,"peak_contact_force":0.10023,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":37982.0,"raw_peak_contact_force":0.20373,"tcp_end":[0.56349,0.20382,0.22963],"tcp_start":[0.47053,0.05621,0.23108],"tcp_to_object_dist_end":0.0258,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38521,"average_solve_count":257.0,"average_success_count":257.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.21367,"approach_1.approach_tol":0.02359,"approach_1.speed":0.11792,"descend_1.descend_speed":0.09081,"descend_1.descend_tol":0.03792,"descend_1.grasp_z_offset":0.00927,"grasp_1.grasp_duration":1.39498,"lift_1.lift_height":0.25479,"lift_1.lift_speed":0.02525,"lift_1.lift_tol":0.02244,"place_1.place_speed":0.06975,"place_1.place_tol":0.04418,"place_1.place_z_offset":-0.00572,"transport_arc.transport_altitude":0.12132,"transport_arc.transport_speed":0.14224,"transport_arc.transport_tol":0.02729},"optimized_scores":{"best_composite_score":-0.05307,"best_fitness_score":0.86693,"best_task_score":0.78424},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":89.0,"contact_point_centroid":[0.53268,-0.02063,-0.00145],"force_p95":0.48739,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51131,"mean_force":0.19159,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52196,-0.02082,0.03473]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15884.0,"contact_point_centroid":[0.52001,-0.00164,0.15114],"force_p95":0.07833,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28743,"mean_force":0.05504,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51952,-0.02075,0.14869]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16511.0,"contact_point_centroid":[0.51998,-0.03983,0.1488],"force_p95":0.07696,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27155,"mean_force":0.05344,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5195,-0.02075,0.14663]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53703,-0.02116,-0.00204],"force_p95":0.13651,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16831,"mean_force":0.12651,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52432,-0.02086,0.03514]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10377.0,"contact_point_centroid":[0.58768,0.1488,0.23919],"force_p95":0.10431,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15794,"mean_force":0.07372,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.58498,0.16782,0.23841]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13148.0,"contact_point_centroid":[0.58764,0.18604,0.23935],"force_p95":0.0852,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14626,"mean_force":0.05828,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.58481,0.16734,0.23879]},{"body_a":"world","body_b":"grasp_target","contact_count":972.0,"contact_point_centroid":[0.53702,-0.02132,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12313,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51298,-0.00872,0.27266]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4104.0,"contact_point_centroid":[0.52391,-0.00163,0.03648],"force_p95":0.0771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12297,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5231,-0.02084,0.03375]},{"body_a":"world","body_b":"grasp_target","contact_count":2464.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52874,-0.01941,0.14397]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16068.0,"contact_point_centroid":[0.54344,0.02614,0.28039],"force_p95":0.09057,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1155,"mean_force":0.06056,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54184,0.04533,0.27844]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4902.0,"contact_point_centroid":[0.52392,-0.03992,0.03555],"force_p95":0.06915,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0907,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5231,-0.02084,0.03375]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20863.0,"contact_point_centroid":[0.54308,0.06646,0.27989],"force_p95":0.07275,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08699,"mean_force":0.0466,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54265,0.04761,0.27892]}],"total_contact_groups":12},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.6091,0.22126,0.17156],"final_tcp_position":[0.60479,0.22102,0.19687],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":0.51131,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":244.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":972.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52814,-0.01788,0.24657],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22076,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":616.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2464.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53161,-0.02099,0.04361],"tcp_start":[0.52814,-0.01788,0.24657],"tcp_to_object_dist_end":0.01841,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53691,-0.02075,0.02583],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31641,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.13371,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10806.0,"raw_peak_contact_force":0.16831,"subtask_id":"grasp_1","tcp_end":[0.52307,-0.02083,0.03371],"tcp_start":[0.53161,-0.02099,0.04361],"tcp_to_object_dist_end":0.01593,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":851.0,"n_steps_budget":1000.0,"object_pos_end":[0.52925,-0.02075,0.25396],"object_pos_start":[0.53691,-0.02075,0.02583],"object_to_goal_dist_end":0.26551,"object_to_goal_dist_start":0.31641,"object_z_max":0.2537,"peak_contact_force":0.08028,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32484.0,"raw_peak_contact_force":0.51131,"tcp_end":[0.52039,-0.02077,0.26872],"tcp_start":[0.52307,-0.02083,0.03371],"tcp_to_object_dist_end":0.01722,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56844,0.10695,0.27136],"object_pos_start":[0.52925,-0.02075,0.25396],"object_to_goal_dist_end":0.14296,"object_to_goal_dist_start":0.26551,"object_z_max":0.27135,"peak_contact_force":0.09281,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36931.0,"raw_peak_contact_force":0.1155,"subtask_id":"transport_arc","tcp_end":[0.56423,0.10687,0.29237],"tcp_start":[0.52039,-0.02077,0.26872],"tcp_to_object_dist_end":0.02142,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":783.0,"n_steps_budget":1000.0,"object_pos_end":[0.6091,0.22126,0.17156],"object_pos_start":[0.56844,0.10695,0.27136],"object_to_goal_dist_end":0.03646,"object_to_goal_dist_start":0.14296,"object_z_max":0.27136,"peak_contact_force":0.08991,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":23525.0,"raw_peak_contact_force":0.15794,"tcp_end":[0.60479,0.22102,0.19687],"tcp_start":[0.56423,0.10687,0.29237],"tcp_to_object_dist_end":0.02568,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```