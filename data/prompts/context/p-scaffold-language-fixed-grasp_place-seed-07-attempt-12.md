## Search State

- **Seed**: 7
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.4842 | 0.76 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2327 | 0.31 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.4847 | 0.76 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.2543 | 0.32 | ✅ accepted |
| 8 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 3 | 0.3763 | 0.31 | ❌ rejected |

**Proposal policy**: task_score is 0.76 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.484) — your mutation base

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

- **Composite score**: 0.484
- **task_score** (E): 0.757
- **fitness_score**: 0.854  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2569 |
| descend_1 | 1.00 | 1.00 | 0.0155 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 1.00 | 1.00 | 0.1034 |
| transport_arc | 0.33 | 1.00 | 0.2634 |
| descend_to_goal | 1.00 | 1.00 | 0.1136 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.505, 0.028, 0.048) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.505, 0.028, 0.048)→(0.504, 0.025, 0.033) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.504, 0.025, 0.033)→(0.496, 0.024, 0.024) | (0.511, 0.022, 0.026)→(0.511, 0.024, 0.025) | 0.273→0.272 | 1.00 / 40.000 | 0.157 | 0.231 |
| lift_1 | lift | 1.00 / step_budget | (0.496, 0.024, 0.024)→(0.505, 0.024, 0.126) | (0.511, 0.024, 0.025)→(0.520, 0.024, 0.126) | 0.272→0.221 | 1.00 / 39.000 | 0.097 | 0.682 |
| transport_arc | approach | 0.33 / step_budget | (0.505, 0.024, 0.126)→(0.574, 0.149, 0.340) | (0.520, 0.024, 0.126)→(0.585, 0.152, 0.326) | 0.221→0.150 | 1.00 / 31.000 | 0.111 | 0.189 |
| descend_to_goal | descend | 1.00 / step_budget | (0.580, 0.169, 0.299)→(0.601, 0.204, 0.197) | (0.585, 0.152, 0.326)→(0.606, 0.193, 0.122) | 0.150→0.074 | 1.00 / 25.667 | 91011.948 | 0.952 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.118
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.266
- phase_breakdown.approach_1_score: 0.672
- phase_breakdown.descend_1_score: 0.721
- phase_breakdown.transport_arc_score: 0.018
- phase_breakdown.release_1_score: 0.000
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.979

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.979
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.606
- **K-run variance**: 0.0304
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.7
- **Final σ (mean)**: 0.389


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17391,"average_solve_count":345.0,"average_success_count":345.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06013,"descend_to_goal.speed":0.02462,"lift_1.speed":0.08424,"transport_arc.arc_height":0.15459,"transport_arc.speed":0.06146},"optimized_scores":{"best_composite_score":0.60585,"best_fitness_score":0.97585,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.50878,0.04108,-0.00138],"force_p95":0.60286,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69213,"mean_force":0.17395,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49649,0.04053,0.02519]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6175.0,"contact_point_centroid":[0.50085,0.05974,0.07695],"force_p95":0.1019,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37821,"mean_force":0.06279,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50028,0.04048,0.07425]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7572.0,"contact_point_centroid":[0.50185,0.02171,0.0761],"force_p95":0.08751,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29764,"mean_force":0.04994,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50026,0.04048,0.07429]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7722.0,"contact_point_centroid":[0.61246,0.18236,0.2274],"force_p95":0.07868,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28142,"mean_force":0.05324,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61656,0.16378,0.22391]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9018.0,"contact_point_centroid":[0.62054,0.14498,0.22618],"force_p95":0.07431,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2107,"mean_force":0.04729,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61643,0.16364,0.22557]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51251,0.04014,-0.00207],"force_p95":0.14845,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20333,"mean_force":0.12917,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49858,0.04073,0.02532]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13644.0,"contact_point_centroid":[0.52945,0.08642,0.24447],"force_p95":0.11475,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17173,"mean_force":0.07054,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52899,0.06733,0.24239]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3612.0,"contact_point_centroid":[0.49885,0.05994,0.02699],"force_p95":0.10515,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16546,"mean_force":0.05965,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49732,0.04062,0.02398]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17844.0,"contact_point_centroid":[0.53158,0.04816,0.24508],"force_p95":0.09406,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16309,"mean_force":0.05639,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52821,0.0665,0.24417]},{"body_a":"world","body_b":"grasp_target","contact_count":2076.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.1323,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50237,0.03546,0.17845]},{"body_a":"world","body_b":"grasp_target","contact_count":220.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50573,0.04261,0.04089]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5414.0,"contact_point_centroid":[0.49897,0.02173,0.02578],"force_p95":0.07865,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10075,"mean_force":0.04118,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49732,0.04062,0.02399]},{"body_a":"grasp_target","body_b":"hand","contact_count":30.0,"contact_point_centroid":[0.52327,0.02078,0.06185],"force_p95":0.02534,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06968,"mean_force":0.01967,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49597,0.04044,0.02907]}],"total_contact_groups":13},"final_pose_error":0.00976,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62474,0.17164,0.13705],"final_tcp_position":[0.62209,0.16994,0.15269],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.69213,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":520.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2076.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50697,0.0438,0.04865],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":55.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":220.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50598,0.04145,0.03333],"tcp_start":[0.50697,0.0438,0.04865],"tcp_to_object_dist_end":0.00996,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51242,0.04106,0.02575],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21159,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.13772,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10826.0,"raw_peak_contact_force":0.20333,"subtask_id":"grasp_1","tcp_end":[0.49729,0.04062,0.02395],"tcp_start":[0.50598,0.04145,0.03333],"tcp_to_object_dist_end":0.01524,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":352.0,"n_steps_budget":930.0,"object_pos_end":[0.52167,0.04114,0.12608],"object_pos_start":[0.51242,0.04106,0.02575],"object_to_goal_dist_end":0.16981,"object_to_goal_dist_start":0.21159,"object_z_max":0.12582,"peak_contact_force":0.1005,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13854.0,"raw_peak_contact_force":0.69213,"tcp_end":[0.50675,0.04067,0.12669],"tcp_start":[0.49729,0.04062,0.02395],"tcp_to_object_dist_end":0.01494,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":952.0,"n_steps_budget":1000.0,"object_pos_end":[0.61765,0.15994,0.28213],"object_pos_start":[0.52167,0.04114,0.12608],"object_to_goal_dist_end":0.13804,"object_to_goal_dist_start":0.16981,"object_z_max":0.29746,"peak_contact_force":0.08275,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":31488.0,"raw_peak_contact_force":0.17173,"subtask_id":"transport_arc","tcp_end":[0.61336,0.15847,0.2957],"tcp_start":[0.50675,0.04067,0.12669],"tcp_to_object_dist_end":0.01431,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":429.0,"n_steps_budget":1000.0,"object_pos_end":[0.62474,0.17164,0.13705],"object_pos_start":[0.61765,0.15994,0.28213],"object_to_goal_dist_end":0.00851,"object_to_goal_dist_start":0.13804,"object_z_max":0.28213,"peak_contact_force":0.07828,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16740.0,"raw_peak_contact_force":0.28142,"tcp_end":[0.62209,0.16994,0.15269],"tcp_start":[0.61336,0.15847,0.2957],"tcp_to_object_dist_end":0.01595,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10622,"average_solve_count":386.0,"average_success_count":386.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04126,"descend_to_goal.speed":0.02406,"lift_1.speed":0.03977,"transport_arc.arc_height":0.14088,"transport_arc.speed":0.08299},"optimized_scores":{"best_composite_score":0.60892,"best_fitness_score":0.97892,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.47931,0.04939,-0.00141],"force_p95":0.48755,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51565,"mean_force":0.18586,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46844,0.04902,0.02683]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9779.0,"contact_point_centroid":[0.54492,0.1931,0.31295],"force_p95":0.09458,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37317,"mean_force":0.07197,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.54779,0.17415,0.31091]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7093.0,"contact_point_centroid":[0.47085,0.06804,0.08002],"force_p95":0.08331,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23656,"mean_force":0.05279,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47161,0.04887,0.07724]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7930.0,"contact_point_centroid":[0.47287,0.02978,0.0763],"force_p95":0.08235,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22626,"mean_force":0.04857,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4714,0.04887,0.07505]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13616.0,"contact_point_centroid":[0.55361,0.15559,0.31162],"force_p95":0.07854,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22192,"mean_force":0.05454,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.54725,0.17321,0.31248]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17168.0,"contact_point_centroid":[0.47525,0.02459,0.26989],"force_p95":0.09817,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18598,"mean_force":0.06114,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.47142,0.04298,0.26886]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13620.0,"contact_point_centroid":[0.47268,0.06162,0.26764],"force_p95":0.11122,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1714,"mean_force":0.07326,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.47118,0.04256,0.26557]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48266,0.04895,-0.00203],"force_p95":0.13254,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15545,"mean_force":0.12582,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47052,0.04926,0.02715]},{"body_a":"world","body_b":"grasp_target","contact_count":2096.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48954,0.03935,0.17956]},{"body_a":"world","body_b":"grasp_target","contact_count":212.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47817,0.05101,0.04196]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4829.0,"contact_point_centroid":[0.46885,0.06834,0.02891],"force_p95":0.08139,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12066,"mean_force":0.04439,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46931,0.04913,0.02594]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5087.0,"contact_point_centroid":[0.47138,0.02993,0.02711],"force_p95":0.08324,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10766,"mean_force":0.04433,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46931,0.04913,0.02594]},{"body_a":"grasp_target","body_b":"hand","contact_count":43.0,"contact_point_centroid":[0.49899,0.02937,0.06361],"force_p95":0.02423,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.03719,"mean_force":0.01642,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46776,0.04887,0.03243]}],"total_contact_groups":13},"final_pose_error":0.00988,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.5809,0.22536,0.21321],"final_tcp_position":[0.5753,0.22172,0.23235],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.51565,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":525.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2096.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47997,0.052,0.04943],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":53.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":212.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47772,0.05006,0.03448],"tcp_start":[0.47997,0.052,0.04943],"tcp_to_object_dist_end":0.0099,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48249,0.04942,0.02587],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28973,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.13165,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11716.0,"raw_peak_contact_force":0.15545,"subtask_id":"grasp_1","tcp_end":[0.46928,0.04913,0.02591],"tcp_start":[0.47772,0.05006,0.03448],"tcp_to_object_dist_end":0.01321,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":362.0,"n_steps_budget":1000.0,"object_pos_end":[0.48945,0.04957,0.12549],"object_pos_start":[0.48249,0.04942,0.02587],"object_to_goal_dist_end":0.2274,"object_to_goal_dist_start":0.28973,"object_z_max":0.12522,"peak_contact_force":0.07984,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15152.0,"raw_peak_contact_force":0.51565,"tcp_end":[0.47704,0.04898,0.1269],"tcp_start":[0.46928,0.04913,0.02591],"tcp_to_object_dist_end":0.0125,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53234,0.13033,0.37992],"object_pos_start":[0.48945,0.04957,0.12549],"object_to_goal_dist_end":0.18572,"object_to_goal_dist_start":0.2274,"object_z_max":0.37986,"peak_contact_force":0.09336,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":30788.0,"raw_peak_contact_force":0.18598,"subtask_id":"transport_arc","tcp_end":[0.52203,0.12761,0.39343],"tcp_start":[0.47704,0.04898,0.1269],"tcp_to_object_dist_end":0.01721,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":743.0,"n_steps_budget":1000.0,"object_pos_end":[0.5809,0.22536,0.21321],"object_pos_start":[0.53234,0.13033,0.37992],"object_to_goal_dist_end":0.01765,"object_to_goal_dist_start":0.18572,"object_z_max":0.37992,"peak_contact_force":0.09255,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":23395.0,"raw_peak_contact_force":0.37317,"tcp_end":[0.5753,0.22172,0.23235],"tcp_start":[0.52203,0.12761,0.39343],"tcp_to_object_dist_end":0.02027,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.97772,"average_solve_count":404.0,"average_success_count":404.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.02989,"descend_to_goal.speed":0.03038,"lift_1.speed":0.09529,"transport_arc.arc_height":0.05066,"transport_arc.speed":0.01685},"optimized_scores":{"best_composite_score":0.23774,"best_fitness_score":0.60774,"best_task_score":0.26952},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":849.0,"contact_point_centroid":[0.61359,0.18247,-0.0036],"force_p95":0.75632,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.20091,"mean_force":0.19168,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.60174,0.21118,0.22743]},{"body_a":"world","body_b":"grasp_target","contact_count":93.0,"contact_point_centroid":[0.53407,-0.01581,-0.00167],"force_p95":0.69927,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.83693,"mean_force":0.17921,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51967,-0.01695,0.02261]},{"body_a":"grasp_target","body_b":"hand","contact_count":87.0,"contact_point_centroid":[0.54256,-0.03602,0.06657],"force_p95":0.29383,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45135,"mean_force":0.0686,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5196,-0.01696,0.0317]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1935.0,"contact_point_centroid":[0.59738,0.15701,0.29753],"force_p95":0.15219,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41228,"mean_force":0.10458,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.58972,0.17322,0.30163]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1600.0,"contact_point_centroid":[0.58808,0.19005,0.30309],"force_p95":0.16802,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37529,"mean_force":0.11661,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.58923,0.17153,0.30527]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6651.0,"contact_point_centroid":[0.52607,-0.03585,0.07585],"force_p95":0.09366,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36456,"mean_force":0.06136,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52434,-0.01704,0.0737]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6062.0,"contact_point_centroid":[0.52732,0.00191,0.07759],"force_p95":0.10785,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35742,"mean_force":0.06574,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52456,-0.01705,0.07535]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5373,-0.02028,-0.00239],"force_p95":0.22926,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33291,"mean_force":0.15489,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52187,-0.01697,0.02221]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13966.0,"contact_point_centroid":[0.55199,0.06887,0.23299],"force_p95":0.11262,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20919,"mean_force":0.07579,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55033,0.04998,0.23184]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14318.0,"contact_point_centroid":[0.55542,0.03238,0.2338],"force_p95":0.1048,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20775,"mean_force":0.0754,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55049,0.05051,0.23311]},{"body_a":"grasp_target","body_b":"hand","contact_count":322.0,"contact_point_centroid":[0.54388,-0.02909,0.05556],"force_p95":0.17537,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17801,"mean_force":0.03999,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52069,-0.01696,0.02089]},{"body_a":"world","body_b":"grasp_target","contact_count":2132.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51359,0.00863,0.17318]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3351.0,"contact_point_centroid":[0.52384,0.00197,0.02327],"force_p95":0.09849,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13348,"mean_force":0.05874,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52057,-0.01696,0.02076]},{"body_a":"world","body_b":"grasp_target","contact_count":240.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52867,-0.01428,0.03794]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4426.0,"contact_point_centroid":[0.52285,-0.03653,0.02323],"force_p95":0.0918,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09826,"mean_force":0.05506,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5206,-0.01696,0.02079]},{"body_a":"left_finger","body_b":"right_finger","contact_count":731.0,"contact_point_centroid":[0.60228,0.21358,0.2246],"force_p95":0.01328,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01621,"mean_force":0.01073,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.60259,0.21387,0.22227]}],"total_contact_groups":16},"final_pose_error":0.00916,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61343,0.18262,0.01602],"final_tcp_position":[0.60417,0.2216,0.20453],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273035.67208,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":534.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2132.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52948,-0.01188,0.04562],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":60.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":240.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52946,-0.01686,0.03075],"tcp_start":[0.52948,-0.01188,0.04562],"tcp_to_object_dist_end":0.00998,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53723,-0.01723,0.02476],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31419,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.20299,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9899.0,"raw_peak_contact_force":0.33291,"subtask_id":"grasp_1","tcp_end":[0.52055,-0.01695,0.02073],"tcp_start":[0.52946,-0.01686,0.03075],"tcp_to_object_dist_end":0.01716,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":370.0,"n_steps_budget":840.0,"object_pos_end":[0.54837,-0.01749,0.12574],"object_pos_start":[0.53723,-0.01723,0.02476],"object_to_goal_dist_end":0.2658,"object_to_goal_dist_start":0.31419,"object_z_max":0.1255,"peak_contact_force":0.11011,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12893.0,"raw_peak_contact_force":0.83693,"tcp_end":[0.5314,-0.01715,0.12586],"tcp_start":[0.52055,-0.01695,0.02073],"tcp_to_object_dist_end":0.01698,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.6037,0.16578,0.31676],"object_pos_start":[0.54837,-0.01749,0.12574],"object_to_goal_dist_end":0.12587,"object_to_goal_dist_start":0.2658,"object_z_max":0.31668,"peak_contact_force":0.15684,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28284.0,"raw_peak_contact_force":0.20919,"subtask_id":"transport_arc","tcp_end":[0.58723,0.16144,0.32984],"tcp_start":[0.5314,-0.01715,0.12586],"tcp_to_object_dist_end":0.02147,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":503.0,"n_steps_budget":1000.0,"object_pos_end":[0.61343,0.18262,0.01601],"object_pos_start":[0.6037,0.16578,0.31676],"object_to_goal_dist_end":0.19667,"object_to_goal_dist_start":0.12587,"object_z_max":0.31676,"peak_contact_force":273035.67208,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5115.0,"raw_peak_contact_force":2.20091,"tcp_end":[0.60417,0.2216,0.20453],"tcp_start":[0.60449,0.22102,0.2074],"tcp_to_object_dist_end":0.19273,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```