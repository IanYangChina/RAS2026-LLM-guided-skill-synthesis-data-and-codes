## Search State

- **Seed**: 7
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.2113 | 0.24 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2167 | 0.25 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.0953 | 0.17 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.0966 | 0.24 | ✅ accepted |
| 3 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 4 | 0.1487 | 0.22 | ❌ rejected |

**Proposal policy**: task_score is 0.24 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.211) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
phases:
- id: approach_1
  type: approach
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
    - 0.0
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: approach_1
- id: descend_1
  type: descend
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
    - 0.02
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: descend_1
- id: grasp_1
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
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
  end_effector_action: force_grasp
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
      mode: keep_current
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
  guards:
  - id: lift_check
    when: after_phase
    predicate: object_lifted
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: transport_to_goal
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: generator.arc_height
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
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
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_check, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=repeat
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=lift_check, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=repeat
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.211
- **task_score** (E): 0.240
- **fitness_score**: 0.581  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1004 |
| descend_1 | 1.00 | 1.00 | 0.1499 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 1.00 | 1.00 | 0.1081 |
| transport_to_goal | 1.00 | 1.00 | 0.0029 |
| release_1 | 1.00 | 1.00 | 0.0514 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.505, 0.017, 0.206) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.505, 0.017, 0.206)→(0.506, 0.021, 0.056) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.021, 0.056)→(0.498, 0.021, 0.047) | (0.511, 0.022, 0.026)→(0.511, 0.021, 0.025) | 0.273→0.274 | 1.00 / 43.000 | 0.169 | 0.231 |
| lift_1 | lift | 1.00 / step_budget | (0.498, 0.021, 0.047)→(0.502, 0.021, 0.155) | (0.511, 0.021, 0.025)→(0.508, 0.022, 0.124) | 0.274→0.228 | 1.00 / 22.333 | 0.117 | 0.402 |
| transport_to_goal | approach | 1.00 / step_budget | (0.594, 0.196, 0.190)→(0.595, 0.198, 0.188) | (0.508, 0.022, 0.124)→(0.552, 0.086, 0.016) | 0.228→0.233 | 1.00 / 8.333 | 97491.591 | 1.643 |
| release_1 | release | 1.00 / step_budget | (0.595, 0.198, 0.188)→(0.600, 0.206, 0.238) | (0.552, 0.086, 0.016)→(0.552, 0.086, 0.016) | 0.233→0.233 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.415
- phase_score: 0.674
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.approach_1_score: 0.017
- phase_breakdown.release_1_score: 0.415
- phase_breakdown.transport_arc_score: 0.683
- phase_breakdown.descend_1_score: 0.851
- grasp_place_fitness: 0.669

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.669
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.415
- **Median Q (composite search score)**: 0.175
- **K-run variance**: 0.0039
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.472


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55932,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17654,"descend_1.grasp_z_offset":0.01109,"lift_1.lift_height":0.15058,"transport_to_goal.arc_height":0.2537,"transport_to_goal.transport_speed":0.14382},"optimized_scores":{"best_composite_score":0.29924,"best_fitness_score":0.66924,"best_task_score":0.41545},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1987.0,"contact_point_centroid":[0.60306,0.16173,-0.00247],"force_p95":0.19869,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.52405,"mean_force":0.1418,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.60948,0.15799,0.14192]},{"body_a":"world","body_b":"grasp_target","contact_count":83.0,"contact_point_centroid":[0.51078,0.03644,-0.00153],"force_p95":0.34863,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38725,"mean_force":0.07401,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49851,0.03701,0.04837]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3357.0,"contact_point_centroid":[0.54148,0.05684,0.16278],"force_p95":0.13615,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31024,"mean_force":0.09508,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53614,0.07521,0.16582]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10770.0,"contact_point_centroid":[0.50644,0.05602,0.12179],"force_p95":0.10311,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29254,"mean_force":0.07186,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5025,0.03723,0.12107]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10386.0,"contact_point_centroid":[0.50622,0.01843,0.12206],"force_p95":0.11067,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27443,"mean_force":0.07333,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50252,0.03723,0.12172]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3378.0,"contact_point_centroid":[0.54313,0.09489,0.16307],"force_p95":0.13475,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25007,"mean_force":0.09407,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53753,0.07674,0.1659]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51259,0.03957,-0.00221],"force_p95":0.18085,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24075,"mean_force":0.13782,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5007,0.03719,0.04797]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4124.0,"contact_point_centroid":[0.50011,0.01794,0.04832],"force_p95":0.0806,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14435,"mean_force":0.05159,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49956,0.0371,0.04672]},{"body_a":"world","body_b":"grasp_target","contact_count":428.0,"contact_point_centroid":[0.51251,0.03972,-0.00171],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12379,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50328,0.0122,0.26839]},{"body_a":"world","body_b":"grasp_target","contact_count":1316.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50659,0.03207,0.14404]},{"body_a":"world","body_b":"grasp_target","contact_count":2420.0,"contact_point_centroid":[0.60306,0.16172,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61775,0.16745,0.15348]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4885.0,"contact_point_centroid":[0.50037,0.05635,0.04818],"force_p95":0.0792,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08213,"mean_force":0.04561,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49957,0.0371,0.04673]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1789.0,"contact_point_centroid":[0.61012,0.15854,0.14251],"force_p95":0.01171,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01651,"mean_force":0.01062,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.60956,0.15851,0.14024]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1954.0,"contact_point_centroid":[0.61757,0.16675,0.1503],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01279,"mean_force":0.01038,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.617,0.1667,0.14805]}],"total_contact_groups":14},"final_pose_error":0.0132,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60306,0.16172,0.01602],"final_tcp_position":[0.62249,0.17054,0.163],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":9748.78973,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":108.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12237,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":428.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50697,0.02656,0.23216],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20663,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":329.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1316.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.508,0.03773,0.0564],"tcp_start":[0.50697,0.02656,0.23216],"tcp_to_object_dist_end":0.03078,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51251,0.03798,0.02525],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21374,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.17491,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10809.0,"raw_peak_contact_force":0.24075,"subtask_id":"grasp_1","tcp_end":[0.49954,0.0371,0.04669],"tcp_start":[0.508,0.03773,0.0564],"tcp_to_object_dist_end":0.02507,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":362.0,"n_steps_budget":810.0,"object_pos_end":[0.51025,0.03769,0.12013],"object_pos_start":[0.51251,0.03798,0.02525],"object_to_goal_dist_end":0.18045,"object_to_goal_dist_start":0.21374,"object_z_max":0.13046,"peak_contact_force":0.127,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":21239.0,"raw_peak_contact_force":0.38725,"tcp_end":[0.50339,0.03727,0.15088],"tcp_start":[0.49954,0.0371,0.04669],"tcp_to_object_dist_end":0.0315,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":504.0,"n_steps_budget":1000.0,"object_pos_end":[0.60306,0.16172,0.01602],"object_pos_start":[0.51025,0.03769,0.12013],"object_to_goal_dist_end":0.13176,"object_to_goal_dist_start":0.18045,"object_z_max":0.13772,"peak_contact_force":9748.78973,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10511.0,"raw_peak_contact_force":1.52405,"subtask_id":"transport_arc","tcp_end":[0.61368,0.16288,0.13623],"tcp_start":[0.61281,0.16137,0.138],"tcp_to_object_dist_end":0.12069,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.60306,0.16172,0.01602],"object_pos_start":[0.60306,0.16172,0.01602],"object_to_goal_dist_end":0.13176,"object_to_goal_dist_start":0.13176,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4374.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61928,0.16948,0.18811],"tcp_start":[0.61368,0.16288,0.13623],"tcp_to_object_dist_end":0.17302,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50222,"average_solve_count":225.0,"average_success_count":225.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10602,"descend_1.grasp_z_offset":0.01131,"lift_1.lift_height":0.17079,"transport_to_goal.arc_height":0.15335,"transport_to_goal.transport_speed":0.06318},"optimized_scores":{"best_composite_score":0.17501,"best_fitness_score":0.54501,"best_task_score":0.16786},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3778.0,"contact_point_centroid":[0.5013,0.09041,-0.0023],"force_p95":0.12689,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.88792,"mean_force":0.13681,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54607,0.17288,0.24748]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.48063,0.04514,-0.00158],"force_p95":0.37705,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42036,"mean_force":0.08569,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47025,0.0456,0.04946]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1562.0,"contact_point_centroid":[0.48077,0.06799,0.18844],"force_p95":0.19477,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31145,"mean_force":0.09868,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47455,0.05005,0.19009]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11915.0,"contact_point_centroid":[0.47688,0.06446,0.13315],"force_p95":0.10645,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28359,"mean_force":0.0685,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47357,0.04591,0.13272]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48279,0.04859,-0.00224],"force_p95":0.18911,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24872,"mean_force":0.13985,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4724,0.04582,0.04892]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1062.0,"contact_point_centroid":[0.47981,0.03115,0.18421],"force_p95":0.1724,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24763,"mean_force":0.11137,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.47424,0.04938,0.18779]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10069.0,"contact_point_centroid":[0.47628,0.02706,0.12956],"force_p95":0.13747,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24692,"mean_force":0.08115,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47352,0.0459,0.13011]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4601.0,"contact_point_centroid":[0.47054,0.02646,0.04814],"force_p95":0.07601,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13851,"mean_force":0.047,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47132,0.04572,0.04781]},{"body_a":"world","body_b":"grasp_target","contact_count":792.0,"contact_point_centroid":[0.4827,0.04873,-0.00184],"force_p95":0.13742,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12324,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49227,0.01834,0.23429]},{"body_a":"world","body_b":"grasp_target","contact_count":820.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48093,0.04245,0.1103]},{"body_a":"world","body_b":"grasp_target","contact_count":2420.0,"contact_point_centroid":[0.50132,0.09037,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57444,0.22275,0.24141]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5580.0,"contact_point_centroid":[0.47062,0.06503,0.04849],"force_p95":0.07277,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07678,"mean_force":0.04052,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47132,0.04572,0.04782]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3927.0,"contact_point_centroid":[0.54865,0.17634,0.24991],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01623,"mean_force":0.01045,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54808,0.17631,0.24769]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1963.0,"contact_point_centroid":[0.57433,0.22175,0.23845],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01287,"mean_force":0.01034,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5737,0.2217,0.23624]}],"total_contact_groups":14},"final_pose_error":0.01181,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.50132,0.09037,0.01602],"final_tcp_position":[0.57822,0.22664,0.24947],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":272977.31507,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":199.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":792.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48411,0.03864,0.16388],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13824,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":205.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":820.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47936,0.04644,0.05646],"tcp_start":[0.48411,0.03864,0.16388],"tcp_to_object_dist_end":0.0307,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48271,0.04679,0.02514],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.2918,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.18337,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11981.0,"raw_peak_contact_force":0.24872,"subtask_id":"grasp_1","tcp_end":[0.47129,0.04572,0.04778],"tcp_start":[0.47936,0.04644,0.05646],"tcp_to_object_dist_end":0.02538,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":407.0,"n_steps_budget":930.0,"object_pos_end":[0.48018,0.048,0.13878],"object_pos_start":[0.48271,0.04679,0.02514],"object_to_goal_dist_end":0.22684,"object_to_goal_dist_start":0.2918,"object_z_max":0.149,"peak_contact_force":0.12239,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":22064.0,"raw_peak_contact_force":0.42036,"tcp_end":[0.47445,0.04599,0.17144],"tcp_start":[0.47129,0.04572,0.04778],"tcp_to_object_dist_end":0.03322,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":788.0,"n_steps_budget":1000.0,"object_pos_end":[0.50132,0.09037,0.01602],"object_pos_start":[0.48018,0.048,0.13878],"object_to_goal_dist_end":0.2677,"object_to_goal_dist_start":0.22684,"object_z_max":0.17391,"peak_contact_force":272977.31507,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10329.0,"raw_peak_contact_force":1.88792,"subtask_id":"transport_arc","tcp_end":[0.57071,0.21665,0.22637],"tcp_start":[0.56992,0.21485,0.22883],"tcp_to_object_dist_end":0.25496,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.50132,0.09037,0.01602],"object_pos_start":[0.50132,0.09037,0.01602],"object_to_goal_dist_end":0.2677,"object_to_goal_dist_start":0.2677,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4383.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57621,0.22557,0.27516],"tcp_start":[0.57071,0.21665,0.22637],"tcp_to_object_dist_end":0.30173,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.52055,"average_solve_count":219.0,"average_success_count":219.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16603,"descend_1.grasp_z_offset":0.01143,"lift_1.lift_height":0.14177,"transport_to_goal.arc_height":0.22888,"transport_to_goal.transport_speed":0.07892},"optimized_scores":{"best_composite_score":0.15957,"best_fitness_score":0.52957,"best_task_score":0.13559},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":4354.0,"contact_point_centroid":[0.55024,0.00504,-0.00221],"force_p95":0.12399,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.5173,"mean_force":0.13297,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.57897,0.14509,0.22129]},{"body_a":"world","body_b":"grasp_target","contact_count":82.0,"contact_point_centroid":[0.53532,-0.02006,-0.0014],"force_p95":0.33588,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39811,"mean_force":0.0714,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52144,-0.02021,0.0473]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1132.0,"contact_point_centroid":[0.53324,0.00461,0.15476],"force_p95":0.18727,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28839,"mean_force":0.10534,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52685,-0.01401,0.1553]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9610.0,"contact_point_centroid":[0.5309,-0.00149,0.11707],"force_p95":0.10788,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26791,"mean_force":0.07732,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52622,-0.02028,0.11612]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10398.0,"contact_point_centroid":[0.53064,-0.03899,0.11522],"force_p95":0.10335,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26235,"mean_force":0.07281,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52605,-0.02027,0.11404]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1538.0,"contact_point_centroid":[0.53312,-0.0312,0.15584],"force_p95":0.13496,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22658,"mean_force":0.08132,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52706,-0.01305,0.15721]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53706,-0.02123,-0.0021],"force_p95":0.15072,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20481,"mean_force":0.13005,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52364,-0.02025,0.04724]},{"body_a":"world","body_b":"grasp_target","contact_count":488.0,"contact_point_centroid":[0.53702,-0.02132,-0.00174],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12363,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51143,-0.00687,0.26321]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4343.0,"contact_point_centroid":[0.52357,-0.00097,0.04765],"force_p95":0.07583,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12841,"mean_force":0.04972,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52246,-0.02023,0.04587]},{"body_a":"world","body_b":"grasp_target","contact_count":1228.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52682,-0.01758,0.13886]},{"body_a":"world","body_b":"grasp_target","contact_count":2420.0,"contact_point_centroid":[0.55026,0.00506,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60307,0.22092,0.21636]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5439.0,"contact_point_centroid":[0.52387,-0.03936,0.04826],"force_p95":0.06741,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06901,"mean_force":0.04061,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52246,-0.02023,0.04588]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4434.0,"contact_point_centroid":[0.58175,0.15218,0.22465],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0158,"mean_force":0.01044,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58133,0.15217,0.22238]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1967.0,"contact_point_centroid":[0.60312,0.21983,0.21349],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01269,"mean_force":0.01033,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60258,0.21979,0.2112]}],"total_contact_groups":14},"final_pose_error":0.01278,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.55026,0.00506,0.01602],"final_tcp_position":[0.60648,0.22535,0.22546],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":9748.83284,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":123.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12256,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":488.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52436,-0.01484,0.22193],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19642,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":307.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1228.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.53119,-0.02036,0.05641],"tcp_start":[0.52436,-0.01484,0.22193],"tcp_to_object_dist_end":0.03096,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53697,-0.02049,0.02564],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3163,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.149,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11582.0,"raw_peak_contact_force":0.20481,"subtask_id":"grasp_1","tcp_end":[0.52243,-0.02023,0.04584],"tcp_start":[0.53119,-0.02036,0.05641],"tcp_to_object_dist_end":0.02489,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":24.0,"n_steps":353.0,"n_steps_budget":780.0,"object_pos_end":[0.53499,-0.02037,0.11249],"object_pos_start":[0.53697,-0.02049,0.02564],"object_to_goal_dist_end":0.27613,"object_to_goal_dist_start":0.3163,"object_z_max":0.12336,"peak_contact_force":0.10112,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20090.0,"raw_peak_contact_force":0.39811,"tcp_end":[0.52727,-0.02029,0.14208],"tcp_start":[0.52243,-0.02023,0.04584],"tcp_to_object_dist_end":0.03058,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":904.0,"n_steps_budget":1000.0,"object_pos_end":[0.55026,0.00506,0.01602],"object_pos_start":[0.53499,-0.02037,0.11249],"object_to_goal_dist_end":0.29972,"object_to_goal_dist_start":0.27613,"object_z_max":0.14262,"peak_contact_force":9748.66876,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11458.0,"raw_peak_contact_force":1.5173,"subtask_id":"transport_arc","tcp_end":[0.60048,0.21379,0.2001],"tcp_start":[0.60004,0.21156,0.20228],"tcp_to_object_dist_end":0.2828,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.55026,0.00506,0.01602],"object_pos_start":[0.55026,0.00506,0.01602],"object_to_goal_dist_end":0.29972,"object_to_goal_dist_start":0.29972,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4387.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.60417,0.22424,0.25049],"tcp_start":[0.60048,0.21379,0.2001],"tcp_to_object_dist_end":0.32546,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```