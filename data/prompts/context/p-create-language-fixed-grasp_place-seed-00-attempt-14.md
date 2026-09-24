## Search State

- **Seed**: 0
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0305 | 0.32 | ❌ rejected |
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.1351 | 0.40 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1748 | 0.31 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.3365 | 0.57 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1875 | 0.33 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`
- Frozen object start: [0.5136961687321454, -0.02302132862361297, 0.03]
- Frozen task target: [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]
- Goal object position: (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5540973523936195, 0.15165276355285293, 0.22199053588004086)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5136961687321454, -0.02302132862361297, 0.03)
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
  frozen_object_start: [0.5137, -0.023, 0.03]
  frozen_task_target: [0.5541, 0.1517, 0.222]
  frozen_object_starts: {'grasp_target': [0.5136961687321454, -0.02302132862361297, 0.03]}
  frozen_targets: {'place_target': [0.5540973523936195, 0.15165276355285293, 0.22199053588004086]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea

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

## Current Skill (Q=0.031) — your mutation base

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
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
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
    tolerance: 0.01
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
      mode: keep_current
  subtask_id: grasp_1
- id: lift_vertical
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
    offset_along_axis:
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 2
    strategy: reduce_speed
- id: transport
  type: approach
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: place_approach
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
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none
- **lift_vertical** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=reduce_speed
- **transport** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **place_approach** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.031
- **task_score** (E): 0.318
- **fitness_score**: 0.631  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.600

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0436 |
| descend_1 | 1.00 | 1.00 | 0.2237 |
| grasp_1 | 1.00 | 1.00 | 0.0117 |
| lift_vertical | 1.00 | 1.00 | 0.1244 |
| transport | 1.00 | 1.00 | 0.2921 |
| place_approach | 1.00 | 1.00 | 0.1528 |
| release_object | 1.00 | 1.00 | 0.0214 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, -0.000, 0.271) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.122 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.497, -0.000, 0.271)→(0.492, 0.001, 0.047) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.492, 0.001, 0.047)→(0.484, 0.000, 0.039) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 | 1.00 / 44.667 | 0.147 | 0.205 |
| lift_vertical | lift | 1.00 / step_budget | (0.484, 0.000, 0.039)→(0.481, 0.000, 0.163) | (0.497, 0.001, 0.026)→(0.495, 0.001, 0.145) | 0.266→0.225 | 1.00 / 27.667 | 0.098 | 0.519 |
| transport | approach | 1.00 / step_budget | (0.481, 0.000, 0.163)→(0.574, 0.169, 0.346) | (0.495, 0.001, 0.145)→(0.564, 0.128, 0.082) | 0.225→0.162 | 1.00 / 17.000 | 3249.745 | 1.533 |
| place_approach | descend | 1.00 / step_budget | (0.574, 0.169, 0.346)→(0.579, 0.182, 0.194) | (0.564, 0.128, 0.082)→(0.563, 0.134, 0.052) | 0.162→0.147 | 1.00 / 12.333 | 91002.072 | 0.221 |
| release_object | release | 1.00 / step_budget | (0.579, 0.182, 0.194)→(0.573, 0.180, 0.215) | (0.563, 0.134, 0.052)→(0.560, 0.133, 0.019) | 0.147→0.178 | 1.00 / 4.000 | 0.119 | 0.466 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.442
- phase_score: 0.396
- phase_breakdown.approach_1_score: 0.004
- phase_breakdown.descend_1_score: 0.902
- phase_breakdown.transport_arc_score: 0.135
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.544
- grasp_place_fitness: 0.691

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.691
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.442
- **Median Q (composite search score)**: 0.020
- **K-run variance**: 0.0021
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.405


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `096c354712624ed6bd8f9b9cbbbc2b7d35a94d9c1517cfb8353e2e383be5aaf0`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3798aa6551d21849355469c7d63897f628ac7de9267c18bb4301fe6cfaae0164`; realized-scene SHA-256: `f07a678caf5b8ea43212ad5a337315ad102b1ae725b01cf669f7af9bd0eea2ea`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5137,-0.02302,0.03]},{"name":"goal","value":[0.5541,0.15165,0.22199]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5137,-0.02302,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5541,0.15165,0.22199]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.63889,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19616,"approach_1.approach_speed":0.27562,"descend_1.descend_speed":0.20644,"descend_1.grasp_z_offset":0.01309,"lift_vertical.lift_height":0.11677,"lift_vertical.lift_speed":0.33772,"place_approach.place_speed":0.22799,"transport.transport_height":0.31327,"transport.transport_speed":0.47854},"optimized_scores":{"best_composite_score":-0.01997,"best_fitness_score":0.58003,"best_task_score":0.2179},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1611.0,"contact_point_centroid":[0.53849,0.05389,-0.00266],"force_p95":0.30241,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.09777,"mean_force":0.1529,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.53335,0.08862,0.38396]},{"body_a":"world","body_b":"grasp_target","contact_count":76.0,"contact_point_centroid":[0.51053,-0.022,-0.00136],"force_p95":0.49897,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51883,"mean_force":0.11674,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.49914,-0.0222,0.04003]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4460.0,"contact_point_centroid":[0.49932,-0.00315,0.08365],"force_p95":0.11103,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33477,"mean_force":0.07193,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.4969,-0.02214,0.08114]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1146.0,"contact_point_centroid":[0.50599,0.01051,0.16601],"force_p95":0.15688,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31107,"mean_force":0.09774,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.49989,-0.00802,0.16513]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4905.0,"contact_point_centroid":[0.49938,-0.04101,0.08174],"force_p95":0.10858,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30395,"mean_force":0.06712,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.49692,-0.02214,0.07998]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1086.0,"contact_point_centroid":[0.50538,-0.02815,0.1629],"force_p95":0.15935,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23463,"mean_force":0.09972,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.49942,-0.00965,0.16167]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51371,-0.02286,-0.00207],"force_p95":0.14329,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18647,"mean_force":0.12816,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50159,-0.02226,0.03993]},{"body_a":"world","body_b":"grasp_target","contact_count":476.0,"contact_point_centroid":[0.5137,-0.02302,-0.00174],"force_p95":0.13801,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12366,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50325,-0.00735,0.27339]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4099.0,"contact_point_centroid":[0.501,-0.00302,0.04141],"force_p95":0.07826,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13332,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50043,-0.02223,0.03865]},{"body_a":"world","body_b":"grasp_target","contact_count":2084.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50693,-0.01916,0.14408]},{"body_a":"world","body_b":"grasp_target","contact_count":2588.0,"contact_point_centroid":[0.5383,0.05385,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.55242,0.14648,0.36982]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.5383,0.05385,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54756,0.14922,0.23282]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4924.0,"contact_point_centroid":[0.50104,-0.04133,0.04048],"force_p95":0.0704,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07867,"mean_force":0.04468,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50043,-0.02223,0.03865]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1527.0,"contact_point_centroid":[0.5359,0.09453,0.39959],"force_p95":0.01204,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01653,"mean_force":0.01069,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.53546,0.09453,0.39742]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2775.0,"contact_point_centroid":[0.55282,0.14647,0.37249],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.0104,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.55242,0.14646,0.37031]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.54983,0.14989,0.2303],"force_p95":0.01086,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01089,"mean_force":0.00989,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.54962,0.14987,0.22798]}],"total_contact_groups":16},"final_pose_error":0.00979,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.5383,0.05385,0.01602],"final_tcp_position":[0.55111,0.15027,0.23121],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":9749.01912,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":120.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.2656,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12253,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":476.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50746,-0.01593,0.24362],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.2178,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":521.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.2656,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2084.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.50862,-0.02241,0.0477],"tcp_start":[0.50746,-0.01593,0.24362],"tcp_to_object_dist_end":0.02228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51361,-0.02225,0.02575],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26532,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.13937,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10823.0,"raw_peak_contact_force":0.18647,"subtask_id":"grasp_1","tcp_end":[0.5004,-0.02223,0.03862],"tcp_start":[0.50862,-0.02241,0.0477],"tcp_to_object_dist_end":0.01844,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":302.0,"n_steps_budget":600.0,"object_pos_end":[0.51355,-0.02217,0.11775],"object_pos_start":[0.51361,-0.02225,0.02575],"object_to_goal_dist_end":0.2067,"object_to_goal_dist_start":0.26532,"object_z_max":0.11749,"peak_contact_force":0.10615,"phase_name":"lift_vertical","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9441.0,"raw_peak_contact_force":0.51883,"tcp_end":[0.49667,-0.02212,0.13594],"tcp_start":[0.5004,-0.02223,0.03862],"tcp_to_object_dist_end":0.02482,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":611.0,"n_steps_budget":1000.0,"object_pos_end":[0.5383,0.05385,0.01602],"object_pos_start":[0.51355,-0.02217,0.11775],"object_to_goal_dist_end":0.22856,"object_to_goal_dist_start":0.2067,"object_z_max":0.17634,"peak_contact_force":9749.01912,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5370.0,"raw_peak_contact_force":2.09777,"subtask_id":"transport_arc","tcp_end":[0.55301,0.14279,0.50684],"tcp_start":[0.49667,-0.02212,0.13594],"tcp_to_object_dist_end":0.49903,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":647.0,"n_steps_budget":1000.0,"object_pos_end":[0.5383,0.05385,0.01602],"object_pos_start":[0.5383,0.05385,0.01602],"object_to_goal_dist_end":0.22856,"object_to_goal_dist_start":0.22856,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"place_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5363.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55111,0.15027,0.23121],"tcp_start":[0.55301,0.14279,0.50684],"tcp_to_object_dist_end":0.23615,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5383,0.05385,0.01602],"object_pos_start":[0.5383,0.05385,0.01602],"object_to_goal_dist_end":0.22856,"object_to_goal_dist_start":0.22856,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.54637,0.14884,0.25311],"tcp_start":[0.55111,0.15027,0.23121],"tcp_to_object_dist_end":0.25553,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `ed2df336ade3d991e9495251c8398520a59dd014a70bd2d7bb71dc7aefccaa8a`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.66279,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.28435,"approach_1.approach_speed":0.34558,"descend_1.descend_speed":0.15736,"descend_1.grasp_z_offset":0.01357,"lift_vertical.lift_height":0.20429,"lift_vertical.lift_speed":0.05413,"place_approach.place_speed":0.32754,"transport.transport_height":0.10672,"transport.transport_speed":0.29049},"optimized_scores":{"best_composite_score":0.09135,"best_fitness_score":0.69135,"best_task_score":0.44177},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":282.0,"contact_point_centroid":[0.54331,0.23701,-0.00492],"force_p95":0.75454,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.15226,"mean_force":0.23993,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55328,0.23693,0.16346]},{"body_a":"world","body_b":"grasp_target","contact_count":89.0,"contact_point_centroid":[0.49827,0.04272,-0.00153],"force_p95":0.42944,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50143,"mean_force":0.13214,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.48735,0.04292,0.04077]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3618.0,"contact_point_centroid":[0.5541,0.24685,0.19796],"force_p95":0.11644,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41756,"mean_force":0.07559,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.55497,0.22845,0.20043]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":612.0,"contact_point_centroid":[0.55382,0.21979,0.14647],"force_p95":0.12372,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32828,"mean_force":0.08417,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.557,0.23874,0.14905]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":837.0,"contact_point_centroid":[0.55613,0.25705,0.14532],"force_p95":0.09321,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31847,"mean_force":0.06483,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.55707,0.23877,0.14917]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12191.0,"contact_point_centroid":[0.48534,0.06184,0.12874],"force_p95":0.08088,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30933,"mean_force":0.05496,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.48505,0.04271,0.12652]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5490.0,"contact_point_centroid":[0.51859,0.11073,0.23385],"force_p95":0.09091,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29593,"mean_force":0.05834,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51841,0.12995,0.23209]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3171.0,"contact_point_centroid":[0.55254,0.20885,0.20141],"force_p95":0.13345,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26911,"mean_force":0.08427,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.55479,0.22792,0.20299]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12053.0,"contact_point_centroid":[0.48543,0.0236,0.13243],"force_p95":0.08027,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26626,"mean_force":0.05487,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.48507,0.04271,0.12998]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50125,0.04485,-0.00217],"force_p95":0.17001,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23553,"mean_force":0.13541,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48969,0.04314,0.04066]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6402.0,"contact_point_centroid":[0.51841,0.14961,0.23353],"force_p95":0.08231,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18103,"mean_force":0.04999,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51864,0.13062,0.2321]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5033.0,"contact_point_centroid":[0.48841,0.02379,0.04252],"force_p95":0.07154,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15461,"mean_force":0.04301,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48855,0.04304,0.03944]},{"body_a":"world","body_b":"grasp_target","contact_count":336.0,"contact_point_centroid":[0.50118,0.04505,-0.00163],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12422,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49898,0.01291,0.30179]},{"body_a":"world","body_b":"grasp_target","contact_count":2876.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49676,0.0358,0.17502]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5555.0,"contact_point_centroid":[0.48825,0.06239,0.04193],"force_p95":0.07142,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07455,"mean_force":0.04084,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48856,0.04304,0.03945]}],"total_contact_groups":15},"final_pose_error":0.00986,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.54319,0.23675,0.02636],"final_tcp_position":[0.55913,0.23952,0.15315],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.15226,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":85.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02598],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.2419,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12209,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":336.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49881,0.02795,0.30449],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.27904,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":719.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02598],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.2419,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2876.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.49656,0.04374,0.0481],"tcp_start":[0.49881,0.02795,0.30449],"tcp_to_object_dist_end":0.0226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50114,0.04355,0.0254],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24344,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16316,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12388.0,"raw_peak_contact_force":0.23553,"subtask_id":"grasp_1","tcp_end":[0.48853,0.04304,0.03941],"tcp_start":[0.49656,0.04374,0.0481],"tcp_to_object_dist_end":0.01886,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":630.0,"n_steps_budget":1000.0,"object_pos_end":[0.49415,0.04295,0.20496],"object_pos_start":[0.50114,0.04355,0.0254],"object_to_goal_dist_end":0.22156,"object_to_goal_dist_start":0.24344,"object_z_max":0.20469,"peak_contact_force":0.07888,"phase_name":"lift_vertical","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":24333.0,"raw_peak_contact_force":0.50143,"tcp_end":[0.4855,0.04275,0.22394],"tcp_start":[0.48853,0.04304,0.03941],"tcp_to_object_dist_end":0.02086,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":306.0,"n_steps_budget":1000.0,"object_pos_end":[0.55528,0.21977,0.21542],"object_pos_start":[0.49415,0.04295,0.20496],"object_to_goal_dist_end":0.07365,"object_to_goal_dist_start":0.22156,"object_z_max":0.21538,"peak_contact_force":0.09291,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":11892.0,"raw_peak_contact_force":0.29593,"subtask_id":"transport_arc","tcp_end":[0.55307,0.21952,0.24308],"tcp_start":[0.4855,0.04275,0.22394],"tcp_to_object_dist_end":0.02775,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":268.0,"n_steps_budget":1000.0,"object_pos_end":[0.55203,0.23837,0.12306],"object_pos_start":[0.55528,0.21977,0.21542],"object_to_goal_dist_end":0.02753,"object_to_goal_dist_start":0.07365,"object_z_max":0.21542,"peak_contact_force":0.13559,"phase_name":"place_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6789.0,"raw_peak_contact_force":0.41756,"tcp_end":[0.55913,0.23952,0.15315],"tcp_start":[0.55307,0.21952,0.24308],"tcp_to_object_dist_end":0.03093,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54319,0.23675,0.02636],"object_pos_start":[0.55203,0.23837,0.12306],"object_to_goal_dist_end":0.12254,"object_to_goal_dist_start":0.02753,"object_z_max":0.12306,"peak_contact_force":0.11078,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1731.0,"raw_peak_contact_force":1.15226,"subtask_id":"release_1","tcp_end":[0.5532,0.2369,0.17396],"tcp_start":[0.55913,0.23952,0.15315],"tcp_to_object_dist_end":0.14794,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `291bc6f2bd023fc25503740a7343328e565e43fc71fa3c9c5d2fdbe2d4351fd2`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.37037,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.21698,"approach_1.approach_speed":0.31653,"descend_1.descend_speed":0.16934,"descend_1.grasp_z_offset":0.01057,"lift_vertical.lift_height":0.11045,"lift_vertical.lift_speed":0.32854,"place_approach.place_speed":0.33751,"transport.transport_height":0.11873,"transport.transport_speed":0.43468},"optimized_scores":{"best_composite_score":0.02024,"best_fitness_score":0.62024,"best_task_score":0.29318},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":496.0,"contact_point_centroid":[0.59787,0.1096,-0.00414],"force_p95":0.85211,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.20438,"mean_force":0.22047,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.5958,0.12272,0.26499]},{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.47342,-0.01928,-0.00136],"force_p95":0.5248,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53686,"mean_force":0.13217,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.46331,-0.01938,0.03917]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2727.0,"contact_point_centroid":[0.50623,0.04162,0.16873],"force_p95":0.13434,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.4419,"mean_force":0.08632,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50034,0.02327,0.16787]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2283.0,"contact_point_centroid":[0.50183,0.00017,0.16515],"force_p95":0.16769,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34587,"mean_force":0.09922,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.49616,0.0188,0.16365]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4700.0,"contact_point_centroid":[0.46247,-0.0002,0.08093],"force_p95":0.10498,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3012,"mean_force":0.06275,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.46124,-0.01931,0.07846]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5109.0,"contact_point_centroid":[0.46254,-0.03833,0.08013],"force_p95":0.09982,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28774,"mean_force":0.05899,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.46123,-0.01931,0.07838]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02004,-0.00206],"force_p95":0.14199,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19262,"mean_force":0.12781,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46561,-0.01943,0.03892]},{"body_a":"world","body_b":"grasp_target","contact_count":340.0,"contact_point_centroid":[0.47616,-0.02015,-0.00163],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1242,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49235,-0.00551,0.28332]},{"body_a":"world","body_b":"grasp_target","contact_count":972.0,"contact_point_centroid":[0.59767,0.10961,-0.00199],"force_p95":0.12327,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12405,"mean_force":0.12268,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.62073,0.15015,0.24272]},{"body_a":"world","body_b":"grasp_target","contact_count":2432.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47685,-0.01592,0.15315]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.59767,0.10961,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62172,0.15476,0.19711]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4828.0,"contact_point_centroid":[0.46449,-0.00015,0.04008],"force_p95":0.06831,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10262,"mean_force":0.04496,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46451,-0.0194,0.03782]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5410.0,"contact_point_centroid":[0.46397,-0.03863,0.03954],"force_p95":0.0653,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07787,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46451,-0.0194,0.03782]},{"body_a":"left_finger","body_b":"right_finger","contact_count":337.0,"contact_point_centroid":[0.60413,0.13102,0.27552],"force_p95":0.01456,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01655,"mean_force":0.01116,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.60384,0.13101,0.27311]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1034.0,"contact_point_centroid":[0.62111,0.15021,0.24447],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01048,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.62078,0.15021,0.24224]},{"body_a":"left_finger","body_b":"right_finger","contact_count":221.0,"contact_point_centroid":[0.62456,0.15554,0.19604],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01096,"mean_force":0.01006,"phase_index":6.0,"phase_name":"release_object","phase_type":"release","tcp_position_centroid":[0.62414,0.15552,0.19355]}],"total_contact_groups":16},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.59767,0.10961,0.01602],"final_tcp_position":[0.62583,0.15588,0.19754],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273005.95881,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":86.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02598],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.2884,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12209,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":340.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48361,-0.01232,0.26345],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":608.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02598],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.2884,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2432.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.47225,-0.01956,0.04563],"tcp_start":[0.48361,-0.01232,0.26345],"tcp_to_object_dist_end":0.02001,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47607,-0.01952,0.02576],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28819,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13928,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12038.0,"raw_peak_contact_force":0.19262,"subtask_id":"grasp_1","tcp_end":[0.46448,-0.0194,0.03779],"tcp_start":[0.47225,-0.01956,0.04563],"tcp_to_object_dist_end":0.01671,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":273.0,"n_steps_budget":600.0,"object_pos_end":[0.47743,-0.01925,0.11284],"object_pos_start":[0.47607,-0.01952,0.02576],"object_to_goal_dist_end":0.24802,"object_to_goal_dist_start":0.28819,"object_z_max":0.11256,"peak_contact_force":0.10753,"phase_name":"lift_vertical","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9883.0,"raw_peak_contact_force":0.53686,"tcp_end":[0.46093,-0.01929,0.12885],"tcp_start":[0.46448,-0.0194,0.03779],"tcp_to_object_dist_end":0.023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":448.0,"n_steps_budget":1000.0,"object_pos_end":[0.59768,0.10956,0.01603],"object_pos_start":[0.47743,-0.01925,0.11284],"object_to_goal_dist_end":0.18405,"object_to_goal_dist_start":0.24802,"object_z_max":0.18191,"peak_contact_force":0.12416,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5843.0,"raw_peak_contact_force":2.20438,"subtask_id":"transport_arc","tcp_end":[0.61729,0.14513,0.28668],"tcp_start":[0.46093,-0.01929,0.12885],"tcp_to_object_dist_end":0.27369,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":243.0,"n_steps_budget":1000.0,"object_pos_end":[0.59767,0.10961,0.01602],"object_pos_start":[0.59768,0.10956,0.01603],"object_to_goal_dist_end":0.18404,"object_to_goal_dist_start":0.18405,"object_z_max":0.01603,"peak_contact_force":273005.95881,"phase_name":"place_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2006.0,"raw_peak_contact_force":0.12405,"tcp_end":[0.62583,0.15588,0.19754],"tcp_start":[0.61729,0.14513,0.28668],"tcp_to_object_dist_end":0.18943,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59767,0.10961,0.01602],"object_pos_start":[0.59767,0.10961,0.01602],"object_to_goal_dist_end":0.18404,"object_to_goal_dist_start":0.18404,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_object","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1021.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.6203,0.15431,0.21651],"tcp_start":[0.62583,0.15588,0.19754],"tcp_to_object_dist_end":0.20666,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```