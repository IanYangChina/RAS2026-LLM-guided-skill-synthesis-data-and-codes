## Search State

- **Seed**: 7
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2290 | 0.31 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.4846 | 0.76 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.4842 | 0.76 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2327 | 0.31 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.4847 | 0.76 | ✅ accepted |

**Proposal policy**: task_score is 0.31 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.229) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_1
  anchor: object
- id: descend_1
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.02
- id: grasp_1
  anchor: object
  metric: contact
  offset:
  - 0.0
  - 0.0
  - 0.02
- id: transport_arc
- id: release_1
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
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
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: none
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: descend_1
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: none
  guards:
  - id: grasp_check
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
  subtask_id: grasp_1
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: transport_arc
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: generator.arc_height
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
- id: descend_to_goal
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: object_held
    when: after_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
  subtask_id: transport_arc

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings: none
  - retries: max_attempts=0, strategy=repeat
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=repeat
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.12], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=2, strategy=repeat
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_to_goal** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=object_held, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=2, strategy=repeat

## Design Metrics

- **Composite score**: 0.229
- **task_score** (E): 0.306
- **fitness_score**: 0.629  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2571 |
| descend_1 | 1.00 | 1.00 | 0.0153 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 1.00 | 1.00 | 0.1033 |
| transport_arc | 0.33 | 1.00 | 0.2655 |
| descend_to_place | 1.00 | 1.00 | 0.1462 |
| release_1 | 1.00 | 1.00 | 0.0209 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.505, 0.028, 0.048) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.505, 0.028, 0.048)→(0.504, 0.025, 0.033) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.504, 0.025, 0.033)→(0.496, 0.024, 0.024) | (0.511, 0.022, 0.026)→(0.511, 0.024, 0.025) | 0.273→0.272 | 1.00 / 41.333 | 0.158 | 0.229 |
| lift_1 | lift | 1.00 / step_budget | (0.496, 0.024, 0.024)→(0.505, 0.024, 0.126) | (0.511, 0.024, 0.025)→(0.520, 0.024, 0.126) | 0.272→0.221 | 1.00 / 38.667 | 0.097 | 0.509 |
| transport_arc | approach | 0.33 / step_budget | (0.505, 0.024, 0.126)→(0.570, 0.144, 0.342) | (0.520, 0.024, 0.126)→(0.585, 0.147, 0.331) | 0.221→0.159 | 1.00 / 28.333 | 0.128 | 0.167 |
| descend_to_place | descend | 1.00 / step_budget | (0.570, 0.144, 0.342)→(0.601, 0.204, 0.218) | (0.585, 0.147, 0.331)→(0.612, 0.196, 0.134) | 0.159→0.070 | 1.00 / 18.667 | 3267.748 | 1.006 |
| release_1 | release | 1.00 / step_budget | (0.601, 0.204, 0.218)→(0.596, 0.202, 0.238) | (0.612, 0.196, 0.134)→(0.611, 0.192, 0.013) | 0.070→0.183 | 1.00 / 4.000 | 0.117 | 1.205 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.423
- phase_score: 0.338
- phase_breakdown.approach_1_score: 0.676
- phase_breakdown.descend_1_score: 0.698
- phase_breakdown.transport_arc_score: 0.052
- phase_breakdown.release_1_score: 0.376
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.687

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.687
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.423
- **Median Q (composite search score)**: 0.209
- **K-run variance**: 0.0017
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.84578,"average_solve_count":415.0,"average_success_count":415.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0841,"descend_to_place.speed":0.01889,"lift_1.speed":0.02829,"transport_arc.arc_height":0.07908,"transport_arc.speed":0.02658},"optimized_scores":{"best_composite_score":0.28723,"best_fitness_score":0.68723,"best_task_score":0.42278},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":482.0,"contact_point_centroid":[0.63019,0.1668,-0.00405],"force_p95":0.77448,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.71627,"mean_force":0.21082,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61639,0.16815,0.17611]},{"body_a":"world","body_b":"grasp_target","contact_count":103.0,"contact_point_centroid":[0.50941,0.04096,-0.00151],"force_p95":0.42727,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.46796,"mean_force":0.18007,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49631,0.04048,0.0247]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3488.0,"contact_point_centroid":[0.61566,0.18251,0.23769],"force_p95":0.16258,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42928,"mean_force":0.09945,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61602,0.16325,0.23823]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":157.0,"contact_point_centroid":[0.62684,0.15451,0.16588],"force_p95":0.20763,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27659,"mean_force":0.05261,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6213,0.1696,0.17099]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4720.0,"contact_point_centroid":[0.62326,0.14668,0.23478],"force_p95":0.12285,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26859,"mean_force":0.07876,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61618,0.16343,0.23637]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":33.0,"contact_point_centroid":[0.62502,0.18914,0.1684],"force_p95":0.23927,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2647,"mean_force":0.16465,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62174,0.16971,0.17193]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6996.0,"contact_point_centroid":[0.50044,0.05968,0.07511],"force_p95":0.1022,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24852,"mean_force":0.06243,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49995,0.04044,0.07241]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8517.0,"contact_point_centroid":[0.50163,0.02166,0.07541],"force_p95":0.08749,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20974,"mean_force":0.04948,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50008,0.04044,0.07362]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51251,0.04013,-0.00207],"force_p95":0.14746,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19996,"mean_force":0.12898,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49858,0.04069,0.02529]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3615.0,"contact_point_centroid":[0.49886,0.0599,0.02697],"force_p95":0.10489,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16459,"mean_force":0.05962,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49732,0.04059,0.02396]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14098.0,"contact_point_centroid":[0.52921,0.08666,0.23169],"force_p95":0.11479,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15769,"mean_force":0.07054,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52881,0.06742,0.22958]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17941.0,"contact_point_centroid":[0.53416,0.05116,0.23444],"force_p95":0.0926,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14175,"mean_force":0.05535,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53072,0.06946,0.23331]},{"body_a":"world","body_b":"grasp_target","contact_count":2004.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50244,0.03545,0.17824]},{"body_a":"world","body_b":"grasp_target","contact_count":216.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50573,0.04254,0.04071]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5410.0,"contact_point_centroid":[0.49897,0.0217,0.02575],"force_p95":0.07864,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0997,"mean_force":0.04118,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49732,0.04059,0.02396]},{"body_a":"grasp_target","body_b":"hand","contact_count":67.0,"contact_point_centroid":[0.52288,0.02057,0.06503],"force_p95":0.05699,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07713,"mean_force":0.03409,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49571,0.04036,0.03209]}],"total_contact_groups":16},"final_pose_error":0.00984,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.63013,0.16683,0.01604],"final_tcp_position":[0.62204,0.16976,0.17269],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":54.33231,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":502.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2004.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50701,0.04369,0.04835],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02334,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":54.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":216.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50598,0.04141,0.0333],"tcp_start":[0.50701,0.04369,0.04835],"tcp_to_object_dist_end":0.00993,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51242,0.04103,0.02575],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2116,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.13704,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10825.0,"raw_peak_contact_force":0.19996,"subtask_id":"grasp_1","tcp_end":[0.49729,0.04059,0.02392],"tcp_start":[0.50598,0.04141,0.0333],"tcp_to_object_dist_end":0.01525,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":396.0,"n_steps_budget":1000.0,"object_pos_end":[0.52139,0.04108,0.12622],"object_pos_start":[0.51242,0.04103,0.02575],"object_to_goal_dist_end":0.17002,"object_to_goal_dist_start":0.2116,"object_z_max":0.12597,"peak_contact_force":0.10046,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15683.0,"raw_peak_contact_force":0.46796,"tcp_end":[0.50668,0.04063,0.12663],"tcp_start":[0.49729,0.04059,0.02392],"tcp_to_object_dist_end":0.01472,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":960.0,"n_steps_budget":1000.0,"object_pos_end":[0.62998,0.16272,0.2834],"object_pos_start":[0.52139,0.04108,0.12622],"object_to_goal_dist_end":0.13874,"object_to_goal_dist_start":0.17002,"object_z_max":0.28927,"peak_contact_force":0.12052,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32039.0,"raw_peak_contact_force":0.15769,"subtask_id":"transport_arc","tcp_end":[0.6134,0.15879,0.29178],"tcp_start":[0.50668,0.04063,0.12663],"tcp_to_object_dist_end":0.01899,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":364.0,"n_steps_budget":1000.0,"object_pos_end":[0.63344,0.17277,0.15294],"object_pos_start":[0.62998,0.16272,0.2834],"object_to_goal_dist_end":0.00985,"object_to_goal_dist_start":0.13874,"object_z_max":0.2834,"peak_contact_force":54.33231,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8208.0,"raw_peak_contact_force":0.42928,"tcp_end":[0.62204,0.16976,0.17269],"tcp_start":[0.6134,0.15879,0.29178],"tcp_to_object_dist_end":0.023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.63013,0.16683,0.01604],"object_pos_start":[0.63344,0.17277,0.15294],"object_to_goal_dist_end":0.12913,"object_to_goal_dist_start":0.00985,"object_z_max":0.15294,"peak_contact_force":0.12414,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":672.0,"raw_peak_contact_force":1.71627,"subtask_id":"release_1","tcp_end":[0.61609,0.16806,0.19239],"tcp_start":[0.62204,0.16976,0.17269],"tcp_to_object_dist_end":0.17691,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13613,"average_solve_count":382.0,"average_success_count":382.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05039,"descend_to_place.speed":0.0153,"lift_1.speed":0.04341,"transport_arc.arc_height":0.15778,"transport_arc.speed":0.06514},"optimized_scores":{"best_composite_score":0.19113,"best_fitness_score":0.59113,"best_task_score":0.22443},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.581,0.22125,-0.00938],"force_p95":1.56399,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.77646,"mean_force":0.56532,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57106,0.2198,0.26532]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.47928,0.04892,-0.00139],"force_p95":0.48794,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5164,"mean_force":0.18466,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46846,0.049,0.02684]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":824.0,"contact_point_centroid":[0.57027,0.23994,0.24884],"force_p95":0.09447,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28426,"mean_force":0.06253,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57382,0.22106,0.24637]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11741.0,"contact_point_centroid":[0.5365,0.17849,0.32588],"force_p95":0.09339,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26296,"mean_force":0.07108,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.53936,0.15962,0.32301]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7074.0,"contact_point_centroid":[0.47085,0.06804,0.07994],"force_p95":0.08335,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23795,"mean_force":0.05274,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47161,0.04887,0.07716]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7867.0,"contact_point_centroid":[0.47289,0.02978,0.07617],"force_p95":0.08241,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22584,"mean_force":0.04871,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47139,0.04886,0.07491]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1179.0,"contact_point_centroid":[0.58136,0.20378,0.24543],"force_p95":0.0752,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21324,"mean_force":0.04502,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57385,0.22108,0.24643]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17037.0,"contact_point_centroid":[0.5455,0.14253,0.32191],"force_p95":0.079,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20458,"mean_force":0.05252,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.53978,0.16036,0.32209]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19268.0,"contact_point_centroid":[0.46434,0.00845,0.26947],"force_p95":0.08658,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15788,"mean_force":0.05395,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46207,0.02714,0.26807]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16057.0,"contact_point_centroid":[0.46275,0.04567,0.26576],"force_p95":0.10827,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15676,"mean_force":0.06438,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46168,0.0265,0.26368]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48266,0.04895,-0.00203],"force_p95":0.13195,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15408,"mean_force":0.12568,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47052,0.04924,0.0271]},{"body_a":"world","body_b":"grasp_target","contact_count":2084.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48953,0.03935,0.17939]},{"body_a":"world","body_b":"grasp_target","contact_count":208.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47816,0.05097,0.04176]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4726.0,"contact_point_centroid":[0.46889,0.06834,0.0288],"force_p95":0.08191,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11916,"mean_force":0.04525,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46931,0.04912,0.02589]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5093.0,"contact_point_centroid":[0.47137,0.02993,0.02706],"force_p95":0.08321,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10703,"mean_force":0.04422,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46931,0.04912,0.02589]},{"body_a":"grasp_target","body_b":"hand","contact_count":39.0,"contact_point_centroid":[0.49908,0.02937,0.06316],"force_p95":0.02042,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.02318,"mean_force":0.01417,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46779,0.04887,0.03201]}],"total_contact_groups":16},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58251,0.22072,0.00651],"final_tcp_position":[0.57526,0.22142,0.24998],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.77646,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":522.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2084.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47994,0.05194,0.04906],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02343,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":52.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":208.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47772,0.05004,0.03443],"tcp_start":[0.47994,0.05194,0.04906],"tcp_to_object_dist_end":0.00986,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48249,0.04944,0.02588],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28971,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.13256,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11619.0,"raw_peak_contact_force":0.15408,"subtask_id":"grasp_1","tcp_end":[0.46928,0.04911,0.02586],"tcp_start":[0.47772,0.05004,0.03443],"tcp_to_object_dist_end":0.01322,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":360.0,"n_steps_budget":1000.0,"object_pos_end":[0.48948,0.04958,0.12524],"object_pos_start":[0.48249,0.04944,0.02588],"object_to_goal_dist_end":0.2275,"object_to_goal_dist_start":0.28971,"object_z_max":0.12497,"peak_contact_force":0.07989,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15064.0,"raw_peak_contact_force":0.5164,"tcp_end":[0.47702,0.04899,0.12671],"tcp_start":[0.46928,0.04911,0.02586],"tcp_to_object_dist_end":0.01256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51813,0.10168,0.38923],"object_pos_start":[0.48948,0.04958,0.12524],"object_to_goal_dist_end":0.21316,"object_to_goal_dist_start":0.2275,"object_z_max":0.38914,"peak_contact_force":0.09677,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35325.0,"raw_peak_contact_force":0.15788,"subtask_id":"transport_arc","tcp_end":[0.50568,0.09963,0.39907],"tcp_start":[0.47702,0.04899,0.12671],"tcp_to_object_dist_end":0.016,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":876.0,"n_steps_budget":1000.0,"object_pos_end":[0.58143,0.22518,0.23241],"object_pos_start":[0.51813,0.10168,0.38923],"object_to_goal_dist_end":0.00417,"object_to_goal_dist_start":0.21316,"object_z_max":0.38923,"peak_contact_force":0.0939,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":28778.0,"raw_peak_contact_force":0.26296,"tcp_end":[0.57526,0.22142,0.24998],"tcp_start":[0.50568,0.09963,0.39907],"tcp_to_object_dist_end":0.019,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58251,0.22072,0.00651],"object_pos_start":[0.58143,0.22518,0.23241],"object_to_goal_dist_end":0.22413,"object_to_goal_dist_start":0.00417,"object_z_max":0.23241,"peak_contact_force":0.10465,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2145.0,"raw_peak_contact_force":1.77646,"subtask_id":"release_1","tcp_end":[0.57103,0.21979,0.27095],"tcp_start":[0.57526,0.22142,0.24998],"tcp_to_object_dist_end":0.2647,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.86425,"average_solve_count":442.0,"average_success_count":442.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.01806,"descend_to_place.speed":0.02411,"lift_1.speed":0.02265,"transport_arc.arc_height":0.05025,"transport_arc.speed":0.07124},"optimized_scores":{"best_composite_score":0.20864,"best_fitness_score":0.60864,"best_task_score":0.27133},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":636.0,"contact_point_centroid":[0.62192,0.18849,-0.00419],"force_p95":0.94136,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32472,"mean_force":0.22149,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6018,0.21041,0.25131]},{"body_a":"world","body_b":"grasp_target","contact_count":133.0,"contact_point_centroid":[0.53415,-0.01637,-0.00188],"force_p95":0.43942,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54146,"mean_force":0.17713,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51936,-0.01694,0.02185]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":995.0,"contact_point_centroid":[0.5908,0.19851,0.31524],"force_p95":0.18775,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45523,"mean_force":0.122,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59202,0.17938,0.3174]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5373,-0.02028,-0.00239],"force_p95":0.22926,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33291,"mean_force":0.15489,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52187,-0.01697,0.02221]},{"body_a":"grasp_target","body_b":"hand","contact_count":131.0,"contact_point_centroid":[0.54233,-0.03609,0.06864],"force_p95":0.2047,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2706,"mean_force":0.07463,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5194,-0.01696,0.03359]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1671.0,"contact_point_centroid":[0.59877,0.16363,0.31307],"force_p95":0.1386,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26366,"mean_force":0.08083,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59214,0.17978,0.31651]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7770.0,"contact_point_centroid":[0.52562,-0.03584,0.07395],"force_p95":0.09275,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23152,"mean_force":0.06095,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52396,-0.01704,0.0718]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7191.0,"contact_point_centroid":[0.52689,0.00191,0.0764],"force_p95":0.10452,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2234,"mean_force":0.06444,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52429,-0.01704,0.07426]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13160.0,"contact_point_centroid":[0.55263,0.07166,0.234],"force_p95":0.12037,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18603,"mean_force":0.07998,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55112,0.05249,0.23291]},{"body_a":"grasp_target","body_b":"hand","contact_count":322.0,"contact_point_centroid":[0.54388,-0.02909,0.05556],"force_p95":0.17537,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17801,"mean_force":0.03999,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52069,-0.01696,0.02089]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16537.0,"contact_point_centroid":[0.55608,0.03739,0.23732],"force_p95":0.0943,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16781,"mean_force":0.06221,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55206,0.05541,0.2368]},{"body_a":"world","body_b":"grasp_target","contact_count":2132.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51359,0.00863,0.17318]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3351.0,"contact_point_centroid":[0.52384,0.00197,0.02327],"force_p95":0.09849,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13348,"mean_force":0.05874,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52057,-0.01696,0.02076]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.62181,0.18875,-0.00199],"force_p95":0.12281,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12315,"mean_force":0.12261,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60169,0.21924,0.23165]},{"body_a":"world","body_b":"grasp_target","contact_count":240.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52867,-0.01428,0.03794]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4426.0,"contact_point_centroid":[0.52285,-0.03653,0.02323],"force_p95":0.0918,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09826,"mean_force":0.05506,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5206,-0.01696,0.02079]}],"total_contact_groups":18},"final_pose_error":0.00979,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.62181,0.18875,0.01602],"final_tcp_position":[0.60515,0.22042,0.23133],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":9748.81703,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":534.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2132.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52948,-0.01188,0.04562],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":60.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":240.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52946,-0.01686,0.03075],"tcp_start":[0.52948,-0.01188,0.04562],"tcp_to_object_dist_end":0.00998,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53723,-0.01723,0.02476],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31419,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.20299,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9899.0,"raw_peak_contact_force":0.33291,"subtask_id":"grasp_1","tcp_end":[0.52055,-0.01695,0.02073],"tcp_start":[0.52946,-0.01686,0.03075],"tcp_to_object_dist_end":0.01716,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":431.0,"n_steps_budget":1000.0,"object_pos_end":[0.54809,-0.01751,0.12578],"object_pos_start":[0.53723,-0.01723,0.02476],"object_to_goal_dist_end":0.26588,"object_to_goal_dist_start":0.31419,"object_z_max":0.12555,"peak_contact_force":0.10982,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15225.0,"raw_peak_contact_force":0.54146,"tcp_end":[0.53131,-0.01715,0.12582],"tcp_start":[0.52055,-0.01695,0.02073],"tcp_to_object_dist_end":0.01678,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60722,0.17777,0.32149],"object_pos_start":[0.54809,-0.01751,0.12578],"object_to_goal_dist_end":0.12459,"object_to_goal_dist_start":0.26588,"object_z_max":0.3214,"peak_contact_force":0.16765,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29697.0,"raw_peak_contact_force":0.18603,"subtask_id":"transport_arc","tcp_end":[0.59112,0.17326,0.33423],"tcp_start":[0.53131,-0.01715,0.12582],"tcp_to_object_dist_end":0.02102,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":394.0,"n_steps_budget":1000.0,"object_pos_end":[0.62181,0.18874,0.016],"object_pos_start":[0.60722,0.17777,0.32149],"object_to_goal_dist_end":0.19568,"object_to_goal_dist_start":0.12459,"object_z_max":0.32149,"peak_contact_force":9748.81703,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3810.0,"raw_peak_contact_force":2.32472,"tcp_end":[0.60515,0.22042,0.23133],"tcp_start":[0.59112,0.17326,0.33423],"tcp_to_object_dist_end":0.21829,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62181,0.18875,0.01602],"object_pos_start":[0.62181,0.18874,0.016],"object_to_goal_dist_end":0.19566,"object_to_goal_dist_start":0.19568,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12315,"subtask_id":"release_1","tcp_end":[0.6005,0.21872,0.25127],"tcp_start":[0.60515,0.22042,0.23133],"tcp_to_object_dist_end":0.23811,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```