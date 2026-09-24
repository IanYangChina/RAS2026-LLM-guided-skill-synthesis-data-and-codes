## Search State

- **Seed**: 7
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2327 | 0.31 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.4847 | 0.76 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.2543 | 0.32 | ✅ accepted |
| 8 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 3 | 0.3763 | 0.31 | ❌ rejected |
| 7 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 3 | 0.3763 | 0.31 | ❌ rejected |

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

## Current Skill (Q=0.233) — your mutation base

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

- **Composite score**: 0.233
- **task_score** (E): 0.314
- **fitness_score**: 0.633  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2570 |
| descend_1 | 1.00 | 1.00 | 0.0154 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 1.00 | 1.00 | 0.1033 |
| transport_arc | 0.67 | 1.00 | 0.2807 |
| descend_to_goal | 1.00 | 0.67 | 0.1590 |
| release_1 | 1.00 | 1.00 | 0.0209 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.505, 0.028, 0.048) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.505, 0.028, 0.048)→(0.504, 0.025, 0.033) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.504, 0.025, 0.033)→(0.496, 0.024, 0.023) | (0.511, 0.022, 0.026)→(0.511, 0.024, 0.025) | 0.273→0.272 | 1.00 / 40.000 | 0.157 | 0.230 |
| lift_1 | lift | 1.00 / step_budget | (0.496, 0.024, 0.023)→(0.505, 0.024, 0.126) | (0.511, 0.024, 0.025)→(0.520, 0.024, 0.125) | 0.272→0.221 | 1.00 / 38.000 | 0.099 | 0.701 |
| transport_arc | approach | 0.67 / step_budget | (0.505, 0.024, 0.126)→(0.579, 0.164, 0.347) | (0.520, 0.024, 0.125)→(0.589, 0.167, 0.332) | 0.221→0.150 | 1.00 / 30.667 | 0.103 | 0.231 |
| descend_to_goal | descend | 1.00 / step_budget | (0.579, 0.164, 0.347)→(0.601, 0.205, 0.200) | (0.589, 0.167, 0.332)→(0.608, 0.207, 0.166) | 0.150→0.029 | 0.67 / 14.667 | 55983.942 | 0.375 |
| release_1 | release | 1.00 / step_budget | (0.601, 0.205, 0.200)→(0.596, 0.203, 0.220) | (0.608, 0.207, 0.166)→(0.611, 0.202, 0.016) | 0.029→0.178 | 1.00 / 4.000 | 0.114 | 1.673 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.423
- phase_score: 0.360
- phase_breakdown.approach_1_score: 0.675
- phase_breakdown.descend_1_score: 0.696
- phase_breakdown.transport_arc_score: 0.045
- phase_breakdown.release_1_score: 0.548
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.687

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.687
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.423
- **Median Q (composite search score)**: 0.212
- **K-run variance**: 0.0015
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.52988,"average_solve_count":251.0,"average_success_count":251.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05425,"descend_to_goal.speed":0.08405,"lift_1.speed":0.06416,"transport_arc.arc_height":0.11837,"transport_arc.speed":0.10091},"optimized_scores":{"best_composite_score":0.28733,"best_fitness_score":0.68733,"best_task_score":0.423},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":254.0,"contact_point_centroid":[0.62618,0.16988,-0.00547],"force_p95":1.042,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.2602,"mean_force":0.28685,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61588,0.16824,0.1628]},{"body_a":"world","body_b":"grasp_target","contact_count":83.0,"contact_point_centroid":[0.50949,0.04104,-0.00138],"force_p95":0.5085,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64653,"mean_force":0.16594,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49651,0.04051,0.0251]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5161.0,"contact_point_centroid":[0.6153,0.18331,0.22658],"force_p95":0.09672,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37318,"mean_force":0.07399,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61693,0.16415,0.22533]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6414.0,"contact_point_centroid":[0.50087,0.05972,0.07698],"force_p95":0.10197,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35367,"mean_force":0.06286,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50026,0.04047,0.07428]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":824.0,"contact_point_centroid":[0.61867,0.18874,0.14869],"force_p95":0.09532,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28989,"mean_force":0.06252,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62001,0.16945,0.14838]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7895.0,"contact_point_centroid":[0.50181,0.02171,0.07574],"force_p95":0.08758,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27711,"mean_force":0.04991,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5002,0.04047,0.07394]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7154.0,"contact_point_centroid":[0.62229,0.1461,0.22625],"force_p95":0.0866,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24183,"mean_force":0.05596,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61679,0.16399,0.22736]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11251.0,"contact_point_centroid":[0.52537,0.08008,0.25458],"force_p95":0.11653,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23336,"mean_force":0.08385,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52332,0.06098,0.25248]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1063.0,"contact_point_centroid":[0.62525,0.1515,0.14596],"force_p95":0.08776,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22888,"mean_force":0.05079,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62003,0.16946,0.14842]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15008.0,"contact_point_centroid":[0.52983,0.04472,0.25539],"force_p95":0.10754,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22405,"mean_force":0.06563,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52507,0.06288,0.25471]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51251,0.04014,-0.00207],"force_p95":0.14813,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20267,"mean_force":0.12909,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49858,0.04072,0.0252]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3614.0,"contact_point_centroid":[0.49885,0.05992,0.02687],"force_p95":0.10504,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16468,"mean_force":0.05963,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49732,0.04061,0.02387]},{"body_a":"world","body_b":"grasp_target","contact_count":2100.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50236,0.03545,0.17837]},{"body_a":"world","body_b":"grasp_target","contact_count":220.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50573,0.04259,0.0407]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5412.0,"contact_point_centroid":[0.49897,0.02172,0.02566],"force_p95":0.07864,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10028,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49733,0.04061,0.02387]},{"body_a":"grasp_target","body_b":"hand","contact_count":33.0,"contact_point_centroid":[0.52329,0.02076,0.0618],"force_p95":0.02348,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.03198,"mean_force":0.01735,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49599,0.04043,0.02902]}],"total_contact_groups":16},"final_pose_error":0.00976,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62868,0.17032,0.01599],"final_tcp_position":[0.62218,0.17002,0.15277],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.2602,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":526.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2100.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50697,0.04377,0.04839],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":55.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":220.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50598,0.04143,0.03321],"tcp_start":[0.50697,0.04377,0.04839],"tcp_to_object_dist_end":0.00986,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51242,0.04105,0.02575],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21159,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.13748,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10826.0,"raw_peak_contact_force":0.20267,"subtask_id":"grasp_1","tcp_end":[0.49729,0.04061,0.02383],"tcp_start":[0.50598,0.04143,0.03321],"tcp_to_object_dist_end":0.01525,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":368.0,"n_steps_budget":1000.0,"object_pos_end":[0.52161,0.04112,0.12596],"object_pos_start":[0.51242,0.04105,0.02575],"object_to_goal_dist_end":0.16987,"object_to_goal_dist_start":0.21159,"object_z_max":0.1257,"peak_contact_force":0.10025,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14425.0,"raw_peak_contact_force":0.64653,"tcp_end":[0.50672,0.04065,0.1267],"tcp_start":[0.49729,0.04061,0.02383],"tcp_to_object_dist_end":0.01491,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":935.0,"n_steps_budget":1000.0,"object_pos_end":[0.62272,0.16167,0.28378],"object_pos_start":[0.52161,0.04112,0.12596],"object_to_goal_dist_end":0.13926,"object_to_goal_dist_start":0.16987,"object_z_max":0.30937,"peak_contact_force":0.0958,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26259.0,"raw_peak_contact_force":0.23336,"tcp_end":[0.61379,0.159,0.29916],"tcp_start":[0.50672,0.04065,0.1267],"tcp_to_object_dist_end":0.01799,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":397.0,"n_steps_budget":1000.0,"object_pos_end":[0.62809,0.17247,0.13396],"object_pos_start":[0.62272,0.16167,0.28378],"object_to_goal_dist_end":0.01108,"object_to_goal_dist_start":0.13926,"object_z_max":0.28378,"peak_contact_force":0.09542,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12315.0,"raw_peak_contact_force":0.37318,"subtask_id":"release_1","tcp_end":[0.62218,0.17002,0.15277],"tcp_start":[0.61379,0.159,0.29916],"tcp_to_object_dist_end":0.01987,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62868,0.17032,0.01599],"object_pos_start":[0.62809,0.17247,0.13396],"object_to_goal_dist_end":0.12906,"object_to_goal_dist_start":0.01108,"object_z_max":0.13396,"peak_contact_force":0.09732,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2141.0,"raw_peak_contact_force":1.2602,"tcp_end":[0.6158,0.16822,0.1724],"tcp_start":[0.62218,0.17002,0.15277],"tcp_to_object_dist_end":0.15695,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17493,"average_solve_count":343.0,"average_success_count":343.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.02944,"descend_to_goal.speed":0.01553,"lift_1.speed":0.11067,"transport_arc.arc_height":0.18594,"transport_arc.speed":0.08692},"optimized_scores":{"best_composite_score":0.1984,"best_fitness_score":0.5984,"best_task_score":0.23896},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":341.0,"contact_point_centroid":[0.5882,0.20984,-0.00575],"force_p95":1.06402,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.73606,"mean_force":0.26329,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57077,0.21993,0.24087]},{"body_a":"world","body_b":"grasp_target","contact_count":75.0,"contact_point_centroid":[0.48003,0.04916,-0.00134],"force_p95":0.59337,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70111,"mean_force":0.15035,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4684,0.04901,0.02724]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":104.0,"contact_point_centroid":[0.57592,0.24146,0.22818],"force_p95":0.26308,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43009,"mean_force":0.19342,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57455,0.2216,0.23066]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8464.0,"contact_point_centroid":[0.54233,0.18705,0.31967],"force_p95":0.15106,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36046,"mean_force":0.08449,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.5442,0.16792,0.32016]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":336.0,"contact_point_centroid":[0.58194,0.20676,0.22515],"force_p95":0.17302,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35391,"mean_force":0.07192,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57429,0.2215,0.23004]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6255.0,"contact_point_centroid":[0.47118,0.06806,0.07953],"force_p95":0.083,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32387,"mean_force":0.05369,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47163,0.04887,0.07662]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6856.0,"contact_point_centroid":[0.47345,0.02981,0.07692],"force_p95":0.08403,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30973,"mean_force":0.05021,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47155,0.04888,0.07548]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11508.0,"contact_point_centroid":[0.55096,0.15127,0.3171],"force_p95":0.09622,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20682,"mean_force":0.06339,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.54454,0.16851,0.31925]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15208.0,"contact_point_centroid":[0.47647,0.02465,0.27332],"force_p95":0.10406,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20428,"mean_force":0.06772,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.47151,0.04289,0.27222]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12108.0,"contact_point_centroid":[0.47342,0.0608,0.2706],"force_p95":0.11472,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18348,"mean_force":0.0821,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.47081,0.04174,0.26855]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48266,0.04895,-0.00203],"force_p95":0.13254,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15545,"mean_force":0.12582,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47052,0.04926,0.02715]},{"body_a":"world","body_b":"grasp_target","contact_count":2096.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48954,0.03935,0.17956]},{"body_a":"world","body_b":"grasp_target","contact_count":212.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47817,0.05101,0.04196]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4829.0,"contact_point_centroid":[0.46885,0.06834,0.02891],"force_p95":0.08139,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12066,"mean_force":0.04439,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46931,0.04913,0.02594]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5087.0,"contact_point_centroid":[0.47138,0.02993,0.02711],"force_p95":0.08324,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10766,"mean_force":0.04433,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46931,0.04913,0.02594]}],"total_contact_groups":15},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58797,0.20994,0.01668],"final_tcp_position":[0.57526,0.22164,0.23237],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":167951.73011,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":525.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2096.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47997,0.052,0.04943],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":53.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":212.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47772,0.05006,0.03448],"tcp_start":[0.47997,0.052,0.04943],"tcp_to_object_dist_end":0.0099,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48249,0.04942,0.02587],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28973,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.13165,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11716.0,"raw_peak_contact_force":0.15545,"subtask_id":"grasp_1","tcp_end":[0.46928,0.04913,0.02591],"tcp_start":[0.47772,0.05006,0.03448],"tcp_to_object_dist_end":0.01321,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":321.0,"n_steps_budget":690.0,"object_pos_end":[0.49077,0.04978,0.1242],"object_pos_start":[0.48249,0.04942,0.02587],"object_to_goal_dist_end":0.2273,"object_to_goal_dist_start":0.28973,"object_z_max":0.12393,"peak_contact_force":0.08679,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13186.0,"raw_peak_contact_force":0.70111,"tcp_end":[0.47711,0.04899,0.12667],"tcp_start":[0.46928,0.04913,0.02591],"tcp_to_object_dist_end":0.0139,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53066,0.12752,0.37934],"object_pos_start":[0.49077,0.04978,0.1242],"object_to_goal_dist_end":0.18721,"object_to_goal_dist_start":0.2273,"object_z_max":0.37929,"peak_contact_force":0.09672,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27316.0,"raw_peak_contact_force":0.20428,"tcp_end":[0.52054,0.12506,0.39573],"tcp_start":[0.47711,0.04899,0.12667],"tcp_to_object_dist_end":0.01942,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":14.0,"n_steps":759.0,"n_steps_budget":1000.0,"object_pos_end":[0.57971,0.22468,0.20814],"object_pos_start":[0.53066,0.12752,0.37934],"object_to_goal_dist_end":0.02283,"object_to_goal_dist_start":0.18721,"object_z_max":0.37934,"peak_contact_force":167951.73011,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":19972.0,"raw_peak_contact_force":0.36046,"subtask_id":"release_1","tcp_end":[0.57526,0.22164,0.23237],"tcp_start":[0.52054,0.12506,0.39573],"tcp_to_object_dist_end":0.02482,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58797,0.20994,0.01668],"object_pos_start":[0.57971,0.22468,0.20814],"object_to_goal_dist_end":0.21472,"object_to_goal_dist_start":0.02283,"object_z_max":0.20814,"peak_contact_force":0.12285,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":781.0,"raw_peak_contact_force":1.73606,"tcp_end":[0.5707,0.21991,0.25329],"tcp_start":[0.57526,0.22164,0.23237],"tcp_to_object_dist_end":0.23745,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32203,"average_solve_count":295.0,"average_success_count":295.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04664,"descend_to_goal.speed":0.04035,"lift_1.speed":0.07151,"transport_arc.arc_height":0.06323,"transport_arc.speed":0.15275},"optimized_scores":{"best_composite_score":0.21243,"best_fitness_score":0.61243,"best_task_score":0.27892},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":610.0,"contact_point_centroid":[0.6169,0.2269,-0.00397],"force_p95":0.82761,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.02385,"mean_force":0.20545,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60195,0.2226,0.21693]},{"body_a":"world","body_b":"grasp_target","contact_count":99.0,"contact_point_centroid":[0.5342,-0.01599,-0.00167],"force_p95":0.58777,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.75394,"mean_force":0.16764,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51966,-0.01695,0.02255]},{"body_a":"grasp_target","body_b":"hand","contact_count":91.0,"contact_point_centroid":[0.54253,-0.03602,0.06657],"force_p95":0.2877,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40834,"mean_force":0.0674,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51957,-0.01696,0.03168]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3291.0,"contact_point_centroid":[0.59982,0.2333,0.29004],"force_p95":0.14364,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39152,"mean_force":0.09802,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.60349,0.2147,0.29172]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5373,-0.02028,-0.00239],"force_p95":0.22922,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33293,"mean_force":0.15489,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52187,-0.01697,0.02221]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6884.0,"contact_point_centroid":[0.52597,-0.03585,0.07537],"force_p95":0.0936,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32655,"mean_force":0.06124,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52425,-0.01704,0.07323]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6317.0,"contact_point_centroid":[0.52724,0.00191,0.07748],"force_p95":0.10769,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32204,"mean_force":0.0652,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52452,-0.01705,0.07528]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4409.0,"contact_point_centroid":[0.61011,0.19844,0.28277],"force_p95":0.10586,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26735,"mean_force":0.07393,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.60362,0.21519,0.28753]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14181.0,"contact_point_centroid":[0.56161,0.04952,0.25722],"force_p95":0.10896,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25586,"mean_force":0.07446,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55636,0.06758,0.25719]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13370.0,"contact_point_centroid":[0.55722,0.08418,0.25641],"force_p95":0.11152,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21541,"mean_force":0.07746,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55562,0.0653,0.25572]},{"body_a":"grasp_target","body_b":"hand","contact_count":322.0,"contact_point_centroid":[0.54388,-0.02909,0.05557],"force_p95":0.17522,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17786,"mean_force":0.03993,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52069,-0.01696,0.02089]},{"body_a":"world","body_b":"grasp_target","contact_count":2132.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51359,0.00863,0.17319]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3351.0,"contact_point_centroid":[0.52384,0.00197,0.02328],"force_p95":0.0985,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13358,"mean_force":0.05875,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52057,-0.01696,0.02076]},{"body_a":"world","body_b":"grasp_target","contact_count":240.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52867,-0.01428,0.03795]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4425.0,"contact_point_centroid":[0.52285,-0.03653,0.02323],"force_p95":0.09181,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09826,"mean_force":0.05507,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5206,-0.01696,0.02079]}],"total_contact_groups":15},"final_pose_error":0.00984,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61693,0.22686,0.016],"final_tcp_position":[0.60634,0.2243,0.21573],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":2.02385,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":534.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2132.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52948,-0.01188,0.04562],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":60.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":240.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52946,-0.01686,0.03076],"tcp_start":[0.52948,-0.01188,0.04562],"tcp_to_object_dist_end":0.00998,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53723,-0.01723,0.02476],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31419,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.20301,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9898.0,"raw_peak_contact_force":0.33293,"subtask_id":"grasp_1","tcp_end":[0.52055,-0.01695,0.02073],"tcp_start":[0.52946,-0.01686,0.03076],"tcp_to_object_dist_end":0.01716,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":383.0,"n_steps_budget":1000.0,"object_pos_end":[0.54827,-0.0175,0.12558],"object_pos_start":[0.53723,-0.01723,0.02476],"object_to_goal_dist_end":0.26589,"object_to_goal_dist_start":0.31419,"object_z_max":0.12533,"peak_contact_force":0.10992,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13391.0,"raw_peak_contact_force":0.75394,"tcp_end":[0.53135,-0.01715,0.12578],"tcp_start":[0.52055,-0.01695,0.02073],"tcp_to_object_dist_end":0.01692,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":28.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61357,0.21298,0.33139],"object_pos_start":[0.54827,-0.0175,0.12558],"object_to_goal_dist_end":0.1249,"object_to_goal_dist_start":0.26589,"object_z_max":0.33139,"peak_contact_force":0.11703,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27551.0,"raw_peak_contact_force":0.25586,"tcp_end":[0.60293,0.20856,0.34731],"tcp_start":[0.53135,-0.01715,0.12578],"tcp_to_object_dist_end":0.01965,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":379.0,"n_steps_budget":1000.0,"object_pos_end":[0.61627,0.22343,0.15512],"object_pos_start":[0.61357,0.21298,0.33139],"object_to_goal_dist_end":0.05281,"object_to_goal_dist_start":0.1249,"object_z_max":0.33139,"peak_contact_force":0.0,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7700.0,"raw_peak_contact_force":0.39152,"subtask_id":"release_1","tcp_end":[0.60634,0.2243,0.21573],"tcp_start":[0.60293,0.20856,0.34731],"tcp_to_object_dist_end":0.06142,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61693,0.22686,0.016],"object_pos_start":[0.61627,0.22343,0.15512],"object_to_goal_dist_end":0.19153,"object_to_goal_dist_start":0.05281,"object_z_max":0.15512,"peak_contact_force":0.12297,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":610.0,"raw_peak_contact_force":2.02385,"tcp_end":[0.60139,0.22234,0.23541],"tcp_start":[0.60634,0.2243,0.21573],"tcp_to_object_dist_end":0.22,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```