## Search State

- **Seed**: 7
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release → retract | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 4 | 0.2543 | 0.32 | ✅ accepted |
| 8 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 3 | 0.3763 | 0.31 | ❌ rejected |
| 7 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 3 | 0.3763 | 0.31 | ❌ rejected |
| 6 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 3 | 0.3763 | 0.31 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.2468 | 0.15 | ❌ rejected |

**Proposal policy**: task_score is 0.32 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.254) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
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
    - 0.03
    tolerance: 0.01
    orientation:
      mode: none
  retries:
    max_attempts: 0
    strategy: repeat
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: task_goal
    entity: placement_surface
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: none
  guards:
  - id: release_check
    when: before_phase
    predicate: pose_within_tolerance
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: release_1
- id: retract_1
  type: retract
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: none
  retries:
    max_attempts: 0
    strategy: repeat

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
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.03], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings: none
  - retries: max_attempts=0, strategy=repeat
- **release_1** (`release`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none
  - guards:
    - id=release_check, when=before_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=repeat
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings: none
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: 0.254
- **task_score** (E): 0.317
- **fitness_score**: 0.634  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2570 |
| descend_1 | 1.00 | 1.00 | 0.0154 |
| grasp_1 | 1.00 | 1.00 | 0.0128 |
| lift_1 | 1.00 | 1.00 | 0.1033 |
| transport_arc | 0.33 | 1.00 | 0.2629 |
| descend_to_goal | 1.00 | 1.00 | 0.1372 |
| release_1 | 1.00 | 1.00 | 0.0208 |
| retract_1 | 1.00 | 1.00 | 0.0779 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.505, 0.028, 0.048) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.505, 0.028, 0.048)→(0.504, 0.025, 0.033) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.504, 0.025, 0.033)→(0.496, 0.024, 0.024) | (0.511, 0.022, 0.026)→(0.511, 0.024, 0.025) | 0.273→0.272 | 1.00 / 40.000 | 0.158 | 0.230 |
| lift_1 | lift | 1.00 / step_budget | (0.496, 0.024, 0.024)→(0.505, 0.024, 0.126) | (0.511, 0.024, 0.025)→(0.520, 0.024, 0.126) | 0.272→0.221 | 1.00 / 38.667 | 0.097 | 0.579 |
| transport_arc | approach | 0.33 / step_budget | (0.505, 0.024, 0.126)→(0.571, 0.144, 0.341) | (0.520, 0.024, 0.126)→(0.581, 0.146, 0.329) | 0.221→0.157 | 1.00 / 33.000 | 0.107 | 0.172 |
| descend_to_goal | descend | 1.00 / step_budget | (0.571, 0.144, 0.341)→(0.601, 0.204, 0.227) | (0.581, 0.146, 0.329)→(0.602, 0.196, 0.142) | 0.157→0.080 | 1.00 / 29.667 | 0.074 | 0.901 |
| release_1 | release | 1.00 / step_budget | (0.601, 0.204, 0.227)→(0.596, 0.202, 0.247) | (0.602, 0.196, 0.142)→(0.602, 0.194, 0.016) | 0.080→0.180 | 1.00 / 4.000 | 0.103 | 1.298 |
| retract_1 | retract | 1.00 / step_budget | (0.596, 0.202, 0.247)→(0.603, 0.208, 0.325) | (0.602, 0.194, 0.016)→(0.602, 0.194, 0.019) | 0.180→0.176 | 1.00 / 4.000 | 0.123 | 0.126 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.423
- phase_score: 0.325
- phase_breakdown.approach_1_score: 0.677
- phase_breakdown.descend_1_score: 0.698
- phase_breakdown.transport_arc_score: 0.045
- phase_breakdown.release_1_score: 0.309
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.687

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.687
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.423
- **Median Q (composite search score)**: 0.230
- **K-run variance**: 0.0014
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.247


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29231,"average_solve_count":325.0,"average_success_count":325.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04843,"lift_1.speed":0.03611,"transport_arc.arc_height":0.11358,"transport_arc.speed":0.06778},"optimized_scores":{"best_composite_score":0.30739,"best_fitness_score":0.68739,"best_task_score":0.42308},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":197.0,"contact_point_centroid":[0.62555,0.17039,-0.00663],"force_p95":1.30553,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.69474,"mean_force":0.4086,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61639,0.16806,0.19462]},{"body_a":"world","body_b":"grasp_target","contact_count":93.0,"contact_point_centroid":[0.50921,0.041,-0.00148],"force_p95":0.46927,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5043,"mean_force":0.18136,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49639,0.04053,0.02486]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5634.0,"contact_point_centroid":[0.61251,0.18241,0.24408],"force_p95":0.08121,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28117,"mean_force":0.05466,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61685,0.16386,0.24038]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6862.0,"contact_point_centroid":[0.50049,0.05973,0.0754],"force_p95":0.10189,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26936,"mean_force":0.06214,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50001,0.04048,0.07269]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8302.0,"contact_point_centroid":[0.50171,0.0217,0.07583],"force_p95":0.08737,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2239,"mean_force":0.04957,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50016,0.04049,0.07403]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6886.0,"contact_point_centroid":[0.62058,0.14509,0.24138],"force_p95":0.07491,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21147,"mean_force":0.04665,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61685,0.16386,0.24038]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51251,0.04014,-0.00207],"force_p95":0.1487,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20399,"mean_force":0.12924,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49858,0.04074,0.02534]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1344.0,"contact_point_centroid":[0.62415,0.15042,0.1793],"force_p95":0.07404,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19045,"mean_force":0.04056,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.6202,0.16921,0.17859]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1108.0,"contact_point_centroid":[0.61601,0.1878,0.18242],"force_p95":0.07884,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1863,"mean_force":0.04687,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62019,0.16921,0.17857]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3611.0,"contact_point_centroid":[0.49885,0.05995,0.027],"force_p95":0.10536,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16698,"mean_force":0.05966,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49732,0.04063,0.024]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14801.0,"contact_point_centroid":[0.52466,0.08133,0.25214],"force_p95":0.1151,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16669,"mean_force":0.06853,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52433,0.06222,0.25015]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19067.0,"contact_point_centroid":[0.52689,0.04332,0.25379],"force_p95":0.09325,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16191,"mean_force":0.055,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5239,0.06175,0.25276]},{"body_a":"world","body_b":"grasp_target","contact_count":2108.0,"contact_point_centroid":[0.51251,0.03972,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50235,0.03542,0.17845]},{"body_a":"world","body_b":"grasp_target","contact_count":1152.0,"contact_point_centroid":[0.62972,0.17127,-0.00198],"force_p95":0.12408,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12509,"mean_force":0.12051,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61919,0.16942,0.23853]},{"body_a":"world","body_b":"grasp_target","contact_count":216.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50574,0.0426,0.04075]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5415.0,"contact_point_centroid":[0.49897,0.02174,0.02579],"force_p95":0.07865,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10117,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49733,0.04063,0.024]}],"total_contact_groups":17},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.62972,0.17127,0.01602],"final_tcp_position":[0.62371,0.17121,0.27546],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.69474,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":528.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2108.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50697,0.04376,0.04829],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0233,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":54.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":216.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50598,0.04146,0.03335],"tcp_start":[0.50697,0.04376,0.04829],"tcp_to_object_dist_end":0.00997,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51242,0.04107,0.02574],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21158,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.13791,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10826.0,"raw_peak_contact_force":0.20399,"subtask_id":"grasp_1","tcp_end":[0.49729,0.04063,0.02396],"tcp_start":[0.50598,0.04146,0.03335],"tcp_to_object_dist_end":0.01523,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":386.0,"n_steps_budget":1000.0,"object_pos_end":[0.52144,0.04113,0.12637],"object_pos_start":[0.51242,0.04107,0.02574],"object_to_goal_dist_end":0.16993,"object_to_goal_dist_start":0.21158,"object_z_max":0.12611,"peak_contact_force":0.1005,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15314.0,"raw_peak_contact_force":0.5043,"tcp_end":[0.50672,0.04068,0.12683],"tcp_start":[0.49729,0.04063,0.02396],"tcp_to_object_dist_end":0.01474,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":995.0,"n_steps_budget":1000.0,"object_pos_end":[0.61722,0.16002,0.28533],"object_pos_start":[0.52144,0.04113,0.12637],"object_to_goal_dist_end":0.14124,"object_to_goal_dist_start":0.16993,"object_z_max":0.30883,"peak_contact_force":0.08348,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33868.0,"raw_peak_contact_force":0.16669,"tcp_end":[0.61361,0.15874,0.29876],"tcp_start":[0.50672,0.04068,0.12683],"tcp_to_object_dist_end":0.01397,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":313.0,"n_steps_budget":1000.0,"object_pos_end":[0.62469,0.17126,0.16817],"object_pos_start":[0.61722,0.16002,0.28533],"object_to_goal_dist_end":0.02336,"object_to_goal_dist_start":0.14124,"object_z_max":0.28533,"peak_contact_force":0.07941,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":12520.0,"raw_peak_contact_force":0.28117,"tcp_end":[0.62214,0.16971,0.18288],"tcp_start":[0.61361,0.15874,0.29876],"tcp_to_object_dist_end":0.01501,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62951,0.17089,0.01468],"object_pos_start":[0.62469,0.17126,0.16817],"object_to_goal_dist_end":0.13037,"object_to_goal_dist_start":0.02336,"object_z_max":0.16817,"peak_contact_force":0.10053,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2649.0,"raw_peak_contact_force":1.69474,"subtask_id":"release_1","tcp_end":[0.61634,0.16805,0.20248],"tcp_start":[0.62214,0.16971,0.18288],"tcp_to_object_dist_end":0.18829,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":288.0,"n_steps_budget":600.0,"object_pos_end":[0.62972,0.17127,0.01602],"object_pos_start":[0.62951,0.17089,0.01468],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.13037,"object_z_max":0.0165,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1152.0,"raw_peak_contact_force":0.12509,"tcp_end":[0.62371,0.17121,0.27546],"tcp_start":[0.61634,0.16805,0.20248],"tcp_to_object_dist_end":0.25951,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11198,"average_solve_count":384.0,"average_success_count":384.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04072,"lift_1.speed":0.02303,"transport_arc.arc_height":0.18122,"transport_arc.speed":0.06567},"optimized_scores":{"best_composite_score":0.2255,"best_fitness_score":0.6055,"best_task_score":0.25314},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":153.0,"contact_point_centroid":[0.56119,0.21371,-0.00996],"force_p95":1.25507,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06852,"mean_force":0.5052,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57136,0.21985,0.27501]},{"body_a":"world","body_b":"grasp_target","contact_count":107.0,"contact_point_centroid":[0.47954,0.0492,-0.0015],"force_p95":0.39061,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44897,"mean_force":0.18202,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46827,0.049,0.02659]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13638.0,"contact_point_centroid":[0.53923,0.18614,0.32604],"force_p95":0.07618,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26691,"mean_force":0.05172,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.54423,0.16775,0.32284]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1214.0,"contact_point_centroid":[0.56774,0.239,0.25975],"force_p95":0.07342,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23047,"mean_force":0.04455,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57404,0.22109,0.25649]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8371.0,"contact_point_centroid":[0.47271,0.02978,0.07568],"force_p95":0.08208,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20241,"mean_force":0.04833,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47127,0.04886,0.07444]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7417.0,"contact_point_centroid":[0.47073,0.06804,0.07931],"force_p95":0.08351,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20149,"mean_force":0.05278,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47149,0.04886,0.07655]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1298.0,"contact_point_centroid":[0.58001,0.20274,0.25674],"force_p95":0.07195,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18553,"mean_force":0.04235,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57402,0.22109,0.25644]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14808.0,"contact_point_centroid":[0.54823,0.14787,0.32577],"force_p95":0.07135,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16201,"mean_force":0.04885,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.54346,0.16642,0.32445]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48266,0.04895,-0.00203],"force_p95":0.13254,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15545,"mean_force":0.12582,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47052,0.04926,0.02715]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20262.0,"contact_point_centroid":[0.46856,0.01596,0.27301],"force_p95":0.07956,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14211,"mean_force":0.05154,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.4666,0.03483,0.27138]},{"body_a":"world","body_b":"grasp_target","contact_count":2096.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48954,0.03935,0.17956]},{"body_a":"world","body_b":"grasp_target","contact_count":1208.0,"contact_point_centroid":[0.56114,0.21373,-0.0021],"force_p95":0.12613,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13041,"mean_force":0.11595,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.57464,0.22331,0.32043]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17491.0,"contact_point_centroid":[0.46646,0.05386,0.27109],"force_p95":0.08928,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12727,"mean_force":0.05815,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46652,0.0347,0.26853]},{"body_a":"world","body_b":"grasp_target","contact_count":212.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47817,0.05101,0.04196]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4829.0,"contact_point_centroid":[0.46885,0.06834,0.02891],"force_p95":0.08139,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12066,"mean_force":0.04439,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46931,0.04913,0.02594]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5087.0,"contact_point_centroid":[0.47138,0.02993,0.02711],"force_p95":0.08324,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10766,"mean_force":0.04433,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46931,0.04913,0.02594]}],"total_contact_groups":17},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.56114,0.21373,0.02602],"final_tcp_position":[0.57914,0.22709,0.36098],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":2.06852,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":525.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2096.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47997,0.052,0.04943],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":53.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":212.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47772,0.05006,0.03448],"tcp_start":[0.47997,0.052,0.04943],"tcp_to_object_dist_end":0.0099,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48249,0.04942,0.02587],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28973,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.13165,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11716.0,"raw_peak_contact_force":0.15545,"subtask_id":"grasp_1","tcp_end":[0.46928,0.04913,0.02591],"tcp_start":[0.47772,0.05006,0.03448],"tcp_to_object_dist_end":0.01321,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":381.0,"n_steps_budget":1000.0,"object_pos_end":[0.4893,0.04958,0.12548],"object_pos_start":[0.48249,0.04942,0.02587],"object_to_goal_dist_end":0.22745,"object_to_goal_dist_start":0.28973,"object_z_max":0.12521,"peak_contact_force":0.08044,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15956.0,"raw_peak_contact_force":0.44897,"tcp_end":[0.477,0.04898,0.12679],"tcp_start":[0.46928,0.04913,0.02591],"tcp_to_object_dist_end":0.01239,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52251,0.11276,0.38643],"object_pos_start":[0.4893,0.04958,0.12548],"object_to_goal_dist_end":0.20327,"object_to_goal_dist_start":0.22745,"object_z_max":0.38636,"peak_contact_force":0.08022,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37753.0,"raw_peak_contact_force":0.14211,"tcp_end":[0.512,0.11056,0.39496],"tcp_start":[0.477,0.04898,0.12679],"tcp_to_object_dist_end":0.01372,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":705.0,"n_steps_budget":1000.0,"object_pos_end":[0.56542,0.21949,0.24238],"object_pos_start":[0.52251,0.11276,0.38643],"object_to_goal_dist_end":0.02235,"object_to_goal_dist_start":0.20327,"object_z_max":0.38643,"peak_contact_force":0.07538,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":28446.0,"raw_peak_contact_force":0.26691,"tcp_end":[0.57539,0.22141,0.26001],"tcp_start":[0.512,0.11056,0.39496],"tcp_to_object_dist_end":0.02034,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56036,0.21469,0.01693],"object_pos_start":[0.56542,0.21949,0.24238],"object_to_goal_dist_end":0.2151,"object_to_goal_dist_start":0.02235,"object_z_max":0.24238,"peak_contact_force":0.08701,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2665.0,"raw_peak_contact_force":2.06852,"subtask_id":"release_1","tcp_end":[0.57132,0.21984,0.28095],"tcp_start":[0.57539,0.22141,0.26001],"tcp_to_object_dist_end":0.2643,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":302.0,"n_steps_budget":660.0,"object_pos_end":[0.56114,0.21373,0.02602],"object_pos_start":[0.56036,0.21469,0.01693],"object_to_goal_dist_end":0.20607,"object_to_goal_dist_start":0.2151,"object_z_max":0.02678,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1208.0,"raw_peak_contact_force":0.13041,"tcp_end":[0.57914,0.22709,0.36098],"tcp_start":[0.57132,0.21984,0.28095],"tcp_to_object_dist_end":0.33571,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57249,"average_solve_count":269.0,"average_success_count":269.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08171,"lift_1.speed":0.08266,"transport_arc.arc_height":0.05053,"transport_arc.speed":0.01618},"optimized_scores":{"best_composite_score":0.23001,"best_fitness_score":0.61001,"best_task_score":0.27407},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":217.0,"contact_point_centroid":[0.61684,0.19521,-0.0084],"force_p95":1.3703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.15593,"mean_force":0.40476,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.60345,0.2151,0.24538]},{"body_a":"world","body_b":"grasp_target","contact_count":95.0,"contact_point_centroid":[0.53411,-0.01589,-0.00165],"force_p95":0.66548,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.78516,"mean_force":0.17857,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51965,-0.01696,0.02264]},{"body_a":"grasp_target","body_b":"hand","contact_count":88.0,"contact_point_centroid":[0.54253,-0.03602,0.06655],"force_p95":0.28497,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43107,"mean_force":0.06832,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51958,-0.01697,0.03167]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2154.0,"contact_point_centroid":[0.59902,0.16266,0.2946],"force_p95":0.16812,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41082,"mean_force":0.10675,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59164,0.17885,0.29891]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1790.0,"contact_point_centroid":[0.58937,0.19535,0.29963],"force_p95":0.19629,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37266,"mean_force":0.11777,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59107,0.17699,0.30185]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6708.0,"contact_point_centroid":[0.52601,-0.03586,0.07554],"force_p95":0.09337,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.341,"mean_force":0.06126,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52428,-0.01705,0.07339]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6115.0,"contact_point_centroid":[0.52727,0.0019,0.07739],"force_p95":0.10788,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33582,"mean_force":0.06564,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52452,-0.01706,0.07516]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5373,-0.02029,-0.00239],"force_p95":0.22847,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33049,"mean_force":0.15464,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52187,-0.01698,0.02225]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13962.0,"contact_point_centroid":[0.55197,0.06889,0.23281],"force_p95":0.11265,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20766,"mean_force":0.0758,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55031,0.05,0.23165]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14344.0,"contact_point_centroid":[0.55543,0.03249,0.23369],"force_p95":0.10445,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20701,"mean_force":0.07531,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55051,0.05062,0.233]},{"body_a":"grasp_target","body_b":"hand","contact_count":320.0,"contact_point_centroid":[0.54387,-0.02926,0.05559],"force_p95":0.17083,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17363,"mean_force":0.03844,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52068,-0.01697,0.02092]},{"body_a":"world","body_b":"grasp_target","contact_count":2040.0,"contact_point_centroid":[0.53702,-0.02132,-0.00193],"force_p95":0.13256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51369,0.00864,0.17299]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3355.0,"contact_point_centroid":[0.52383,0.00196,0.02331],"force_p95":0.09856,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13633,"mean_force":0.05877,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52056,-0.01697,0.0208]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.61611,0.19563,-0.00194],"force_p95":0.12799,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12972,"mean_force":0.11788,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60154,0.21842,0.23944]},{"body_a":"world","body_b":"grasp_target","contact_count":240.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52866,-0.01431,0.038]},{"body_a":"world","body_b":"grasp_target","contact_count":1232.0,"contact_point_centroid":[0.61611,0.19563,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.60327,0.22175,0.29796]}],"total_contact_groups":19},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.61611,0.19563,0.01602],"final_tcp_position":[0.60746,0.22585,0.33781],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":2.15593,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":511.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2040.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.5295,-0.01189,0.04576],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.02313,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":60.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":240.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52945,-0.01687,0.03079],"tcp_start":[0.5295,-0.01189,0.04576],"tcp_to_object_dist_end":0.01,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53723,-0.01723,0.02477],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3142,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.20298,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9895.0,"raw_peak_contact_force":0.33049,"subtask_id":"grasp_1","tcp_end":[0.52054,-0.01696,0.02077],"tcp_start":[0.52945,-0.01687,0.03079],"tcp_to_object_dist_end":0.01716,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":373.0,"n_steps_budget":960.0,"object_pos_end":[0.54831,-0.0175,0.1256],"object_pos_start":[0.53723,-0.01723,0.02477],"object_to_goal_dist_end":0.26587,"object_to_goal_dist_start":0.3142,"object_z_max":0.12535,"peak_contact_force":0.11018,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13006.0,"raw_peak_contact_force":0.78516,"tcp_end":[0.53137,-0.01716,0.12574],"tcp_start":[0.52054,-0.01696,0.02077],"tcp_to_object_dist_end":0.01695,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60373,0.16582,0.31673],"object_pos_start":[0.54831,-0.0175,0.1256],"object_to_goal_dist_end":0.12582,"object_to_goal_dist_start":0.26587,"object_z_max":0.31665,"peak_contact_force":0.15707,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28306.0,"raw_peak_contact_force":0.20766,"tcp_end":[0.58723,0.16147,0.32974],"tcp_start":[0.53137,-0.01716,0.12574],"tcp_to_object_dist_end":0.02145,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":365.0,"n_steps_budget":1000.0,"object_pos_end":[0.61564,0.19716,0.01414],"object_pos_start":[0.60373,0.16582,0.31673],"object_to_goal_dist_end":0.19575,"object_to_goal_dist_start":0.12582,"object_z_max":0.31673,"peak_contact_force":0.06737,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4206.0,"raw_peak_contact_force":2.15593,"tcp_end":[0.6049,0.21952,0.23907],"tcp_start":[0.58723,0.16147,0.32974],"tcp_to_object_dist_end":0.22629,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61611,0.19563,0.01602],"object_pos_start":[0.61564,0.19716,0.01414],"object_to_goal_dist_end":0.19416,"object_to_goal_dist_start":0.19575,"object_z_max":0.01688,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1027.0,"raw_peak_contact_force":0.12972,"subtask_id":"release_1","tcp_end":[0.6004,0.21791,0.25906],"tcp_start":[0.6049,0.21952,0.23907],"tcp_to_object_dist_end":0.24457,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":308.0,"n_steps_budget":630.0,"object_pos_end":[0.61611,0.19563,0.01602],"object_pos_start":[0.61611,0.19563,0.01602],"object_to_goal_dist_end":0.19416,"object_to_goal_dist_start":0.19416,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1232.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60746,0.22585,0.33781],"tcp_start":[0.6004,0.21791,0.25906],"tcp_to_object_dist_end":0.32332,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```