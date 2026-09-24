## Search State

- **Seed**: 7
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.4847 | 0.76 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.2543 | 0.32 | ✅ accepted |
| 8 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 3 | 0.3763 | 0.31 | ❌ rejected |
| 7 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 3 | 0.3763 | 0.31 | ❌ rejected |
| 6 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 3 | 0.3763 | 0.31 | ✅ accepted |

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

## Current Skill (Q=0.485) — your mutation base

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

- **Composite score**: 0.485
- **task_score** (E): 0.758
- **fitness_score**: 0.855  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
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
| lift_1 | 1.00 | 1.00 | 0.1033 |
| transport_arc | 0.33 | 1.00 | 0.2674 |
| descend_to_goal | 1.00 | 1.00 | 0.1167 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.028, 0.048) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.028, 0.048)→(0.504, 0.025, 0.033) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.504, 0.025, 0.033)→(0.496, 0.024, 0.024) | (0.511, 0.022, 0.026)→(0.511, 0.024, 0.025) | 0.273→0.272 | 1.00 / 40.000 | 0.157 | 0.230 |
| lift_1 | lift | 1.00 / step_budget | (0.496, 0.024, 0.024)→(0.505, 0.024, 0.126) | (0.511, 0.024, 0.025)→(0.520, 0.024, 0.126) | 0.272→0.221 | 1.00 / 38.667 | 0.097 | 0.639 |
| transport_arc | approach | 0.33 / step_budget | (0.505, 0.024, 0.126)→(0.573, 0.150, 0.341) | (0.520, 0.024, 0.126)→(0.586, 0.154, 0.330) | 0.221→0.153 | 1.00 / 29.333 | 0.117 | 0.186 |
| descend_to_goal | descend | 1.00 / step_budget | (0.577, 0.164, 0.298)→(0.601, 0.205, 0.197) | (0.586, 0.154, 0.330)→(0.611, 0.197, 0.122) | 0.153→0.073 | 1.00 / 24.667 | 91000.195 | 0.967 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.148
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.707
- phase_breakdown.approach_1_score: 0.672
- phase_breakdown.descend_1_score: 0.721
- phase_breakdown.transport_arc_score: 0.820
- phase_breakdown.release_1_score: 0.000
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.979

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.979
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.606
- **K-run variance**: 0.0301
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.429


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10784,"average_solve_count":306.0,"average_success_count":306.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09312,"descend_to_goal.speed":0.02558,"lift_1.speed":0.04702,"transport_arc.arc_height":0.17599,"transport_arc.speed":0.09381},"optimized_scores":{"best_composite_score":0.60593,"best_fitness_score":0.97593,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.50935,0.04123,-0.00143],"force_p95":0.4986,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53916,"mean_force":0.17136,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49652,0.0405,0.02501]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6517.0,"contact_point_centroid":[0.61306,0.18251,0.22802],"force_p95":0.09382,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31139,"mean_force":0.06356,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61652,0.16383,0.22409]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6746.0,"contact_point_centroid":[0.50062,0.05969,0.07579],"force_p95":0.10179,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29077,"mean_force":0.06225,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50012,0.04045,0.07311]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8183.0,"contact_point_centroid":[0.50179,0.02168,0.07588],"force_p95":0.08735,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23538,"mean_force":0.04966,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50022,0.04045,0.07409]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8473.0,"contact_point_centroid":[0.62138,0.14576,0.22252],"force_p95":0.07781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23,"mean_force":0.04947,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61664,0.16397,0.22236]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51251,0.04013,-0.00207],"force_p95":0.14766,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20202,"mean_force":0.12903,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49864,0.0407,0.02532]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16254.0,"contact_point_centroid":[0.53661,0.0534,0.24034],"force_p95":0.09455,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18864,"mean_force":0.05727,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53294,0.07168,0.23966]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11451.0,"contact_point_centroid":[0.53605,0.09321,0.24361],"force_p95":0.11437,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17423,"mean_force":0.07709,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53521,0.07409,0.24112]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3617.0,"contact_point_centroid":[0.4989,0.05991,0.02699],"force_p95":0.10497,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16499,"mean_force":0.05974,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49739,0.04059,0.02398]},{"body_a":"world","body_b":"grasp_target","contact_count":1992.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13279,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50249,0.0355,0.17822]},{"body_a":"world","body_b":"grasp_target","contact_count":220.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50583,0.04257,0.04088]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5412.0,"contact_point_centroid":[0.49901,0.0217,0.02576],"force_p95":0.07871,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10014,"mean_force":0.04118,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49739,0.04059,0.02398]},{"body_a":"grasp_target","body_b":"hand","contact_count":40.0,"contact_point_centroid":[0.52322,0.02066,0.06258],"force_p95":0.0254,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.03198,"mean_force":0.01862,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49593,0.0404,0.02976]}],"total_contact_groups":13},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62761,0.17245,0.13722],"final_tcp_position":[0.62207,0.16993,0.15288],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":0.53916,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":499.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1992.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50716,0.04376,0.04872],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02367,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":55.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":220.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50605,0.04142,0.03333],"tcp_start":[0.50716,0.04376,0.04872],"tcp_to_object_dist_end":0.00991,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.04104,0.02575],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2116,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.13711,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10829.0,"raw_peak_contact_force":0.20202,"subtask_id":"grasp_1","tcp_end":[0.49736,0.0406,0.02395],"tcp_start":[0.50605,0.04142,0.03333],"tcp_to_object_dist_end":0.01518,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":381.0,"n_steps_budget":1000.0,"object_pos_end":[0.52147,0.04109,0.126],"object_pos_start":[0.51243,0.04104,0.02575],"object_to_goal_dist_end":0.16998,"object_to_goal_dist_start":0.2116,"object_z_max":0.12574,"peak_contact_force":0.10033,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15057.0,"raw_peak_contact_force":0.53916,"tcp_end":[0.50672,0.04064,0.12668],"tcp_start":[0.49736,0.0406,0.02395],"tcp_to_object_dist_end":0.01478,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":879.0,"n_steps_budget":1000.0,"object_pos_end":[0.62131,0.16118,0.28062],"object_pos_start":[0.52147,0.04109,0.126],"object_to_goal_dist_end":0.13621,"object_to_goal_dist_start":0.16998,"object_z_max":0.28986,"peak_contact_force":0.09387,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27705.0,"raw_peak_contact_force":0.18864,"tcp_end":[0.61351,0.1588,0.29294],"tcp_start":[0.50672,0.04064,0.12668],"tcp_to_object_dist_end":0.01477,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":421.0,"n_steps_budget":1000.0,"object_pos_end":[0.62761,0.17245,0.13722],"object_pos_start":[0.62131,0.16118,0.28062],"object_to_goal_dist_end":0.00781,"object_to_goal_dist_start":0.13621,"object_z_max":0.28062,"peak_contact_force":0.09549,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":14990.0,"raw_peak_contact_force":0.31139,"subtask_id":"transport_arc","tcp_end":[0.62207,0.16993,0.15288],"tcp_start":[0.61351,0.1588,0.29294],"tcp_to_object_dist_end":0.0168,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21964,"average_solve_count":387.0,"average_success_count":387.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04671,"descend_to_goal.speed":0.0324,"lift_1.speed":0.06591,"transport_arc.arc_height":0.14548,"transport_arc.speed":0.02798},"optimized_scores":{"best_composite_score":0.60892,"best_fitness_score":0.97892,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.47936,0.04915,-0.00133],"force_p95":0.54693,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.625,"mean_force":0.18039,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46853,0.04902,0.02712]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11541.0,"contact_point_centroid":[0.53968,0.18366,0.31218],"force_p95":0.09473,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29757,"mean_force":0.07038,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.54216,0.16474,0.31]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6855.0,"contact_point_centroid":[0.47093,0.06804,0.08036],"force_p95":0.08296,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2896,"mean_force":0.0527,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47168,0.04887,0.07756]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7550.0,"contact_point_centroid":[0.47301,0.02978,0.07648],"force_p95":0.08254,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27624,"mean_force":0.04904,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47146,0.04887,0.0752]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14435.0,"contact_point_centroid":[0.55045,0.14965,0.30625],"force_p95":0.08507,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21002,"mean_force":0.05876,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.54362,0.16725,0.30649]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48266,0.04895,-0.00203],"force_p95":0.13254,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15545,"mean_force":0.12582,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47052,0.04926,0.02715]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20085.0,"contact_point_centroid":[0.46883,0.01627,0.26958],"force_p95":0.07977,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14392,"mean_force":0.05172,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46679,0.03513,0.26795]},{"body_a":"world","body_b":"grasp_target","contact_count":2096.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48954,0.03935,0.17956]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17399.0,"contact_point_centroid":[0.46676,0.05429,0.26779],"force_p95":0.089,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13107,"mean_force":0.05807,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46678,0.03512,0.26524]},{"body_a":"world","body_b":"grasp_target","contact_count":212.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47817,0.05101,0.04196]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4829.0,"contact_point_centroid":[0.46885,0.06834,0.02891],"force_p95":0.08139,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12066,"mean_force":0.04439,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46931,0.04913,0.02594]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5087.0,"contact_point_centroid":[0.47138,0.02993,0.02711],"force_p95":0.08324,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10766,"mean_force":0.04433,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46931,0.04913,0.02594]},{"body_a":"grasp_target","body_b":"hand","contact_count":21.0,"contact_point_centroid":[0.49919,0.0294,0.0616],"force_p95":0.01648,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.01834,"mean_force":0.01002,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46794,0.04891,0.03054]}],"total_contact_groups":13},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.58303,0.22579,0.21376],"final_tcp_position":[0.57517,0.22154,0.23104],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":0.625,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":525.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2096.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47997,0.052,0.04943],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":53.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":212.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47772,0.05006,0.03448],"tcp_start":[0.47997,0.052,0.04943],"tcp_to_object_dist_end":0.0099,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48249,0.04942,0.02587],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28973,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.13165,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11716.0,"raw_peak_contact_force":0.15545,"subtask_id":"grasp_1","tcp_end":[0.46928,0.04913,0.02591],"tcp_start":[0.47772,0.05006,0.03448],"tcp_to_object_dist_end":0.01321,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":347.0,"n_steps_budget":1000.0,"object_pos_end":[0.48967,0.04958,0.12515],"object_pos_start":[0.48249,0.04942,0.02587],"object_to_goal_dist_end":0.22746,"object_to_goal_dist_start":0.28973,"object_z_max":0.12489,"peak_contact_force":0.07951,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14503.0,"raw_peak_contact_force":0.625,"tcp_end":[0.47707,0.04899,0.12684],"tcp_start":[0.46928,0.04913,0.02591],"tcp_to_object_dist_end":0.01273,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52613,0.11256,0.3844],"object_pos_start":[0.48967,0.04958,0.12515],"object_to_goal_dist_end":0.2008,"object_to_goal_dist_start":0.22746,"object_z_max":0.38431,"peak_contact_force":0.09219,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37484.0,"raw_peak_contact_force":0.14392,"tcp_end":[0.51135,0.10962,0.39202],"tcp_start":[0.47707,0.04899,0.12684],"tcp_to_object_dist_end":0.01688,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":840.0,"n_steps_budget":1000.0,"object_pos_end":[0.58303,0.22579,0.21376],"object_pos_start":[0.52613,0.11256,0.3844],"object_to_goal_dist_end":0.01704,"object_to_goal_dist_start":0.2008,"object_z_max":0.3844,"peak_contact_force":0.09462,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":25976.0,"raw_peak_contact_force":0.29757,"subtask_id":"transport_arc","tcp_end":[0.57517,0.22154,0.23104],"tcp_start":[0.51135,0.10962,0.39202],"tcp_to_object_dist_end":0.01946,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.04959,"average_solve_count":363.0,"average_success_count":363.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.01628,"descend_to_goal.speed":0.03514,"lift_1.speed":0.07035,"transport_arc.arc_height":0.0502,"transport_arc.speed":0.09818},"optimized_scores":{"best_composite_score":0.23928,"best_fitness_score":0.60928,"best_task_score":0.27261},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":861.0,"contact_point_centroid":[0.62222,0.19235,-0.00365],"force_p95":0.76498,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.29108,"mean_force":0.19439,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.6029,0.21445,0.23396]},{"body_a":"world","body_b":"grasp_target","contact_count":99.0,"contact_point_centroid":[0.5342,-0.01599,-0.00167],"force_p95":0.5878,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.75399,"mean_force":0.16765,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51966,-0.01695,0.02255]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":997.0,"contact_point_centroid":[0.59326,0.20651,0.31656],"force_p95":0.18827,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.47494,"mean_force":0.12369,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59475,0.1874,0.31864]},{"body_a":"grasp_target","body_b":"hand","contact_count":92.0,"contact_point_centroid":[0.54253,-0.03603,0.06671],"force_p95":0.28763,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40859,"mean_force":0.06687,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51958,-0.01696,0.03182]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5373,-0.02028,-0.00239],"force_p95":0.22926,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33291,"mean_force":0.15489,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52187,-0.01697,0.02221]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6884.0,"contact_point_centroid":[0.52597,-0.03585,0.07537],"force_p95":0.0936,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32653,"mean_force":0.06124,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52425,-0.01704,0.07323]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6317.0,"contact_point_centroid":[0.52724,0.00191,0.07748],"force_p95":0.10769,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32204,"mean_force":0.0652,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52452,-0.01705,0.07528]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1667.0,"contact_point_centroid":[0.60158,0.17167,0.31391],"force_p95":0.13325,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26998,"mean_force":0.07867,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59485,0.18776,0.31744]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16267.0,"contact_point_centroid":[0.55764,0.04117,0.24047],"force_p95":0.0952,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2268,"mean_force":0.06353,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55335,0.05914,0.24003]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12970.0,"contact_point_centroid":[0.55367,0.07476,0.23665],"force_p95":0.12531,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21724,"mean_force":0.08082,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55221,0.05559,0.2356]},{"body_a":"grasp_target","body_b":"hand","contact_count":322.0,"contact_point_centroid":[0.54388,-0.02909,0.05556],"force_p95":0.17537,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17801,"mean_force":0.03999,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52069,-0.01696,0.02089]},{"body_a":"world","body_b":"grasp_target","contact_count":2132.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51359,0.00863,0.17318]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3351.0,"contact_point_centroid":[0.52384,0.00197,0.02327],"force_p95":0.09849,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13348,"mean_force":0.05874,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52057,-0.01696,0.02076]},{"body_a":"world","body_b":"grasp_target","contact_count":240.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52867,-0.01428,0.03794]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4426.0,"contact_point_centroid":[0.52285,-0.03653,0.02323],"force_p95":0.0918,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09826,"mean_force":0.05506,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5206,-0.01696,0.02079]},{"body_a":"left_finger","body_b":"right_finger","contact_count":748.0,"contact_point_centroid":[0.60333,0.21629,0.23008],"force_p95":0.01301,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01632,"mean_force":0.01069,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.60355,0.21656,0.2276]}],"total_contact_groups":16},"final_pose_error":0.0079,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.62205,0.19253,0.01602],"final_tcp_position":[0.60449,0.22256,0.20618],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273000.3946,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":534.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2132.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.52948,-0.01188,0.04562],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":60.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":240.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52946,-0.01686,0.03075],"tcp_start":[0.52948,-0.01188,0.04562],"tcp_to_object_dist_end":0.00998,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53723,-0.01723,0.02476],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31419,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.20299,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9899.0,"raw_peak_contact_force":0.33291,"subtask_id":"grasp_1","tcp_end":[0.52055,-0.01695,0.02073],"tcp_start":[0.52946,-0.01686,0.03075],"tcp_to_object_dist_end":0.01716,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":383.0,"n_steps_budget":1000.0,"object_pos_end":[0.54827,-0.0175,0.12558],"object_pos_start":[0.53723,-0.01723,0.02476],"object_to_goal_dist_end":0.26589,"object_to_goal_dist_start":0.31419,"object_z_max":0.12534,"peak_contact_force":0.10992,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13392.0,"raw_peak_contact_force":0.75399,"tcp_end":[0.53135,-0.01715,0.12578],"tcp_start":[0.52055,-0.01695,0.02073],"tcp_to_object_dist_end":0.01692,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60947,0.18717,0.32389],"object_pos_start":[0.54827,-0.0175,0.12558],"object_to_goal_dist_end":0.12335,"object_to_goal_dist_start":0.26589,"object_z_max":0.32383,"peak_contact_force":0.16418,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":29237.0,"raw_peak_contact_force":0.2268,"tcp_end":[0.59428,0.18255,0.33751],"tcp_start":[0.53135,-0.01715,0.12578],"tcp_to_object_dist_end":0.02092,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":449.0,"n_steps_budget":1000.0,"object_pos_end":[0.62205,0.19253,0.01601],"object_pos_start":[0.60947,0.18717,0.32389],"object_to_goal_dist_end":0.19496,"object_to_goal_dist_start":0.12335,"object_z_max":0.32389,"peak_contact_force":273000.3946,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4273.0,"raw_peak_contact_force":2.29108,"subtask_id":"transport_arc","tcp_end":[0.60449,0.22256,0.20618],"tcp_start":[0.60492,0.22219,0.20937],"tcp_to_object_dist_end":0.19332,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```