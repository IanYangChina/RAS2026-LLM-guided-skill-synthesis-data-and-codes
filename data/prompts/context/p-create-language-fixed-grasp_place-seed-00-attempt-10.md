## Search State

- **Seed**: 0
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1875 | 0.33 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.1181 | 0.32 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2618 | 0.32 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.0590 | 0.19 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1378 | 0.24 | ❌ rejected |

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

## Current Skill (Q=0.187) — your mutation base

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
  guards:
  - id: grasp_retention
    when: during_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
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
    orientation:
      mode: keep_current
  subtask_id: release_1

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
  - guards:
    - id=grasp_retention, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=reduce_speed
- **place_approach** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.187
- **task_score** (E): 0.328
- **fitness_score**: 0.637  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0672 |
| descend_1 | 1.00 | 1.00 | 0.1952 |
| grasp_1 | 1.00 | 1.00 | 0.0117 |
| lift_vertical | 1.00 | 1.00 | 0.1435 |
| transport | 0.00 | 1.00 | 0.0495 |
| place_approach | 1.00 | 1.00 | 0.0843 |
| release_1 | 1.00 | 1.00 | 0.0215 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.003, 0.241) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.122 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.496, 0.003, 0.241)→(0.492, 0.001, 0.046) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.492, 0.001, 0.046)→(0.484, 0.001, 0.037) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 | 1.00 / 44.333 | 0.143 | 0.200 |
| lift_vertical | lift | 1.00 / step_budget | (0.484, 0.001, 0.037)→(0.481, 0.000, 0.181) | (0.497, 0.001, 0.026)→(0.491, 0.000, 0.165) | 0.266→0.215 | 1.00 / 37.000 | 0.080 | 0.519 |
| transport | approach | 0.00 / guard_failure | (0.543, 0.119, 0.244)→(0.560, 0.159, 0.264) | (0.491, 0.000, 0.165)→(0.545, 0.113, 0.222) | 0.215→0.093 | 1.00 / 32.333 | 0.069 | 0.189 |
| place_approach | descend | 1.00 / step_budget | (0.560, 0.159, 0.264)→(0.578, 0.182, 0.190) | (0.569, 0.160, 0.242)→(0.578, 0.181, 0.166) | 0.071→0.022 | 1.00 / 36.667 | 0.103 | 0.210 |
| release_1 | release | 1.00 / step_budget | (0.578, 0.182, 0.190)→(0.572, 0.180, 0.211) | (0.578, 0.181, 0.166)→(0.572, 0.171, 0.017) | 0.022→0.170 | 1.00 / 3.000 | 0.154 | 1.747 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.421
- phase_score: 0.416
- phase_breakdown.approach_1_score: 0.036
- phase_breakdown.descend_1_score: 0.892
- phase_breakdown.transport_arc_score: 0.172
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.538
- grasp_place_fitness: 0.682

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.682
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.421
- **Median Q (composite search score)**: 0.176
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at lower bound**: descend_1.grasp_z_offset
- **Final σ (mean)**: 0.322


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.59155,"average_solve_count":213.0,"average_success_count":213.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.20477,"descend_1.grasp_z_offset":0.01045,"lift_vertical.lift_height":0.1567,"lift_vertical.lift_speed":0.05487,"place_approach.place_speed":0.46217,"transport.transport_speed":0.08084},"optimized_scores":{"best_composite_score":0.15376,"best_fitness_score":0.60376,"best_task_score":0.25988},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":179.0,"contact_point_centroid":[0.53054,0.15143,-0.00812],"force_p95":1.30899,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.94366,"mean_force":0.42389,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54552,0.14758,0.24569]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.51057,-0.02209,-0.00142],"force_p95":0.47849,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53036,"mean_force":0.14805,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.49946,-0.02239,0.03722]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9013.0,"contact_point_centroid":[0.49722,-0.00317,0.10475],"force_p95":0.07889,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31677,"mean_force":0.05561,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.49692,-0.02231,0.1022]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9476.0,"contact_point_centroid":[0.49718,-0.0414,0.10316],"force_p95":0.07757,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29561,"mean_force":0.05358,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.49691,-0.02231,0.10098]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5137,-0.02287,-0.00206],"force_p95":0.13966,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18128,"mean_force":0.12725,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50177,-0.02244,0.03738]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4264.0,"contact_point_centroid":[0.54947,0.16425,0.2695],"force_p95":0.08215,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14838,"mean_force":0.05185,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.54886,0.14522,0.2675]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1328.0,"contact_point_centroid":[0.54928,0.12948,0.22978],"force_p95":0.06831,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14757,"mean_force":0.03978,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54859,0.14857,0.22727]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12716.0,"contact_point_centroid":[0.52326,0.0427,0.24121],"force_p95":0.08006,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14472,"mean_force":0.05555,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.522,0.06174,0.23926]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12906.0,"contact_point_centroid":[0.52288,0.07984,0.24039],"force_p95":0.07972,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14229,"mean_force":0.05433,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52167,0.0608,0.23846]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1122.0,"contact_point_centroid":[0.5498,0.1679,0.2288],"force_p95":0.07751,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1395,"mean_force":0.04747,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54856,0.14856,0.22719]},{"body_a":"world","body_b":"grasp_target","contact_count":824.0,"contact_point_centroid":[0.5137,-0.02302,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12322,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50311,-0.00877,0.27116]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4102.0,"contact_point_centroid":[0.50111,-0.00321,0.03887],"force_p95":0.07762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12847,"mean_force":0.05183,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50059,-0.02241,0.0361]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4557.0,"contact_point_centroid":[0.54955,0.12612,0.26896],"force_p95":0.08076,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12519,"mean_force":0.05005,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.54889,0.14529,0.26697]},{"body_a":"world","body_b":"grasp_target","contact_count":2412.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50723,-0.02054,0.14226]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4910.0,"contact_point_centroid":[0.50116,-0.0415,0.03793],"force_p95":0.06975,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08469,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5006,-0.02241,0.0361]}],"total_contact_groups":15},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.53776,0.14738,0.02057],"final_tcp_position":[0.55025,0.14896,0.23079],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":1.94366,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":207.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":824.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50807,-0.01856,0.24154],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21564,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":603.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2412.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50879,-0.0226,0.04515],"tcp_start":[0.50807,-0.01856,0.24154],"tcp_to_object_dist_end":0.01975,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51359,-0.02237,0.02579],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26536,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.13629,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10812.0,"raw_peak_contact_force":0.18128,"subtask_id":"grasp_1","tcp_end":[0.50057,-0.02241,0.03607],"tcp_start":[0.50879,-0.0226,0.04515],"tcp_to_object_dist_end":0.01659,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":477.0,"n_steps_budget":1000.0,"object_pos_end":[0.50736,-0.0223,0.15901],"object_pos_start":[0.51359,-0.02237,0.02579],"object_to_goal_dist_end":0.19082,"object_to_goal_dist_start":0.26536,"object_z_max":0.15875,"peak_contact_force":0.07991,"phase_name":"lift_vertical","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18573.0,"raw_peak_contact_force":0.53036,"tcp_end":[0.49705,-0.0223,0.17323],"tcp_start":[0.50057,-0.02241,0.03607],"tcp_to_object_dist_end":0.01756,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":706.0,"n_steps_budget":1000.0,"object_pos_end":[0.54639,0.11145,0.26287],"object_pos_start":[0.50736,-0.0223,0.15901],"object_to_goal_dist_end":0.05786,"object_to_goal_dist_start":0.19082,"object_z_max":0.28662,"peak_contact_force":0.08862,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25622.0,"raw_peak_contact_force":0.14472,"subtask_id":"transport_arc","tcp_end":[0.54854,0.14178,0.30583],"tcp_start":[0.5387,0.11154,0.28142],"tcp_to_object_dist_end":0.05263,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":215.0,"n_steps_budget":1000.0,"object_pos_end":[0.54592,0.14843,0.21045],"object_pos_start":[0.55605,0.14186,0.28679],"object_to_goal_dist_end":0.01451,"object_to_goal_dist_start":0.06556,"object_z_max":0.28684,"peak_contact_force":0.0766,"phase_name":"place_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8821.0,"raw_peak_contact_force":0.14838,"tcp_end":[0.55025,0.14896,0.23079],"tcp_start":[0.54854,0.14178,0.30583],"tcp_to_object_dist_end":0.0208,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53776,0.14738,0.02057],"object_pos_start":[0.54592,0.14843,0.21045],"object_to_goal_dist_end":0.20213,"object_to_goal_dist_start":0.01451,"object_z_max":0.21045,"peak_contact_force":0.21507,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2629.0,"raw_peak_contact_force":1.94366,"subtask_id":"release_1","tcp_end":[0.54548,0.14757,0.25268],"tcp_start":[0.55025,0.14896,0.23079],"tcp_to_object_dist_end":0.23224,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63314,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15861,"descend_1.grasp_z_offset":0.01229,"lift_vertical.lift_height":0.1405,"lift_vertical.lift_speed":0.0502,"place_approach.place_speed":0.30297,"transport.transport_speed":0.48898},"optimized_scores":{"best_composite_score":0.23232,"best_fitness_score":0.68232,"best_task_score":0.42099},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":120.0,"contact_point_centroid":[0.55904,0.22923,-0.0095],"force_p95":1.46433,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.52444,"mean_force":0.61728,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55356,0.23834,0.16559]},{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.49717,0.04339,-0.00151],"force_p95":0.49782,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51539,"mean_force":0.174,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.48742,0.04332,0.03949]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1056.0,"contact_point_centroid":[0.55844,0.22067,0.15032],"force_p95":0.1248,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34283,"mean_force":0.06766,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55719,0.24009,0.15007]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9069.0,"contact_point_centroid":[0.4844,0.0623,0.09884],"force_p95":0.0754,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30802,"mean_force":0.05024,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.48491,0.04309,0.09727]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8720.0,"contact_point_centroid":[0.48458,0.02388,0.09784],"force_p95":0.07432,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26672,"mean_force":0.0511,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.48491,0.04309,0.09582]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3625.0,"contact_point_centroid":[0.56048,0.25507,0.19127],"force_p95":0.10677,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2594,"mean_force":0.06466,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.55745,0.23662,0.19066]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2956.0,"contact_point_centroid":[0.56123,0.21739,0.19419],"force_p95":0.12742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25705,"mean_force":0.08266,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.55733,0.23634,0.1931]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50123,0.04486,-0.00214],"force_p95":0.16048,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22855,"mean_force":0.13289,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48963,0.04354,0.03947]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1229.0,"contact_point_centroid":[0.55762,0.25872,0.15056],"force_p95":0.08413,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21969,"mean_force":0.04279,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55746,0.24022,0.15051]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8921.0,"contact_point_centroid":[0.52001,0.11593,0.19525],"force_p95":0.1089,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19601,"mean_force":0.06632,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.5183,0.13497,0.19295]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10868.0,"contact_point_centroid":[0.52085,0.15706,0.19563],"force_p95":0.09406,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17301,"mean_force":0.05658,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51949,0.13815,0.19416]},{"body_a":"world","body_b":"grasp_target","contact_count":1392.0,"contact_point_centroid":[0.50118,0.04505,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49803,0.01906,0.24821]},{"body_a":"world","body_b":"grasp_target","contact_count":1860.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49585,0.04172,0.1208]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5036.0,"contact_point_centroid":[0.48837,0.02419,0.04139],"force_p95":0.0704,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11635,"mean_force":0.04298,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48849,0.04343,0.03824]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5513.0,"contact_point_centroid":[0.4882,0.06275,0.0408],"force_p95":0.06991,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07515,"mean_force":0.04096,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48849,0.04343,0.03825]}],"total_contact_groups":15},"final_pose_error":0.00988,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56385,0.22764,0.01815],"final_tcp_position":[0.55943,0.241,0.15439],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.52444,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":349.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1392.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49776,0.03951,0.19617],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17027,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":465.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1860.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49646,0.04415,0.04688],"tcp_start":[0.49776,0.03951,0.19617],"tcp_to_object_dist_end":0.02141,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50113,0.04381,0.02552],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24317,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15493,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12349.0,"raw_peak_contact_force":0.22855,"subtask_id":"grasp_1","tcp_end":[0.48846,0.04343,0.03821],"tcp_start":[0.49646,0.04415,0.04688],"tcp_to_object_dist_end":0.01793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":416.0,"n_steps_budget":1000.0,"object_pos_end":[0.49475,0.04308,0.14369],"object_pos_start":[0.50113,0.04381,0.02552],"object_to_goal_dist_end":0.2135,"object_to_goal_dist_start":0.24317,"object_z_max":0.14342,"peak_contact_force":0.08212,"phase_name":"lift_vertical","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17875.0,"raw_peak_contact_force":0.51539,"tcp_end":[0.4849,0.0431,0.15923],"tcp_start":[0.48846,0.04343,0.03821],"tcp_to_object_dist_end":0.01839,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":599.0,"n_steps_budget":1000.0,"object_pos_end":[0.53394,0.15318,0.17992],"object_pos_start":[0.49475,0.04308,0.14369],"object_to_goal_dist_end":0.10214,"object_to_goal_dist_start":0.2135,"object_z_max":0.20962,"peak_contact_force":0.11968,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":19789.0,"raw_peak_contact_force":0.19601,"subtask_id":"transport_arc","tcp_end":[0.55677,0.23239,0.23344],"tcp_start":[0.52558,0.15278,0.20095],"tcp_to_object_dist_end":0.09829,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":225.0,"n_steps_budget":1000.0,"object_pos_end":[0.56232,0.24018,0.1285],"object_pos_start":[0.57013,0.2332,0.20971],"object_to_goal_dist_end":0.01898,"object_to_goal_dist_start":0.06426,"object_z_max":0.20973,"peak_contact_force":0.13345,"phase_name":"place_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6581.0,"raw_peak_contact_force":0.2594,"tcp_end":[0.55943,0.241,0.15439],"tcp_start":[0.55677,0.23239,0.23344],"tcp_to_object_dist_end":0.02606,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56385,0.22764,0.01815],"object_pos_start":[0.56232,0.24018,0.1285],"object_to_goal_dist_end":0.12977,"object_to_goal_dist_start":0.01898,"object_z_max":0.1285,"peak_contact_force":0.1597,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2405.0,"raw_peak_contact_force":1.52444,"subtask_id":"release_1","tcp_end":[0.55349,0.23831,0.17505],"tcp_start":[0.55943,0.241,0.15439],"tcp_to_object_dist_end":0.1576,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46875,"average_solve_count":192.0,"average_success_count":192.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.2528,"descend_1.grasp_z_offset":0.01,"lift_vertical.lift_height":0.19183,"lift_vertical.lift_speed":0.05389,"place_approach.place_speed":0.12945,"transport.transport_speed":0.38319},"optimized_scores":{"best_composite_score":0.17631,"best_fitness_score":0.62631,"best_task_score":0.30416},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":193.0,"contact_point_centroid":[0.61149,0.13715,-0.00665],"force_p95":1.2973,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.77377,"mean_force":0.38255,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61848,0.15312,0.19705]},{"body_a":"world","body_b":"grasp_target","contact_count":80.0,"contact_point_centroid":[0.47304,-0.01935,-0.00143],"force_p95":0.44813,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51103,"mean_force":0.15391,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.46342,-0.01945,0.03843]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11475.0,"contact_point_centroid":[0.46092,-0.0002,0.12206],"force_p95":0.0768,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27941,"mean_force":0.05233,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.46109,-0.01938,0.12002]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11835.0,"contact_point_centroid":[0.46085,-0.03852,0.12152],"force_p95":0.07523,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27776,"mean_force":0.05123,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.46108,-0.01938,0.11975]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1135.0,"contact_point_centroid":[0.62308,0.13458,0.18041],"force_p95":0.10007,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24018,"mean_force":0.0631,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62199,0.15422,0.18061]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1187.0,"contact_point_centroid":[0.62344,0.17309,0.18197],"force_p95":0.07981,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23786,"mean_force":0.04202,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62241,0.15435,0.18141]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7916.0,"contact_point_centroid":[0.52154,0.02593,0.23518],"force_p95":0.0888,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22713,"mean_force":0.05766,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52055,0.04507,0.23258]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7562.0,"contact_point_centroid":[0.60069,0.11081,0.21562],"force_p95":0.09658,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22178,"mean_force":0.06538,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.59926,0.12993,0.2151]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9377.0,"contact_point_centroid":[0.60094,0.14919,0.21546],"force_p95":0.07907,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21243,"mean_force":0.05135,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.59967,0.13035,0.21455]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02005,-0.00206],"force_p95":0.14007,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1903,"mean_force":0.12738,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46559,-0.0195,0.03839]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8864.0,"contact_point_centroid":[0.52181,0.06464,0.23469],"force_p95":0.07763,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.189,"mean_force":0.05205,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52102,0.04561,0.23275]},{"body_a":"world","body_b":"grasp_target","contact_count":384.0,"contact_point_centroid":[0.47616,-0.02015,-0.00168],"force_p95":0.13822,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12396,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4915,-0.00579,0.29256]},{"body_a":"world","body_b":"grasp_target","contact_count":2968.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4763,-0.01623,0.1635]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4829.0,"contact_point_centroid":[0.46448,-0.00026,0.03955],"force_p95":0.06805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10074,"mean_force":0.04491,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46449,-0.01947,0.03729]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5170.0,"contact_point_centroid":[0.46433,-0.0387,0.03909],"force_p95":0.06675,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07814,"mean_force":0.04285,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46449,-0.01947,0.03729]}],"total_contact_groups":15},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.61397,0.1383,0.01357],"final_tcp_position":[0.62402,0.15465,0.1851],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.77377,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":97.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02601],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28839,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12218,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":384.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48244,-0.01287,0.28459],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25876,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":742.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02601],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28839,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2968.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.47224,-0.01964,0.04509],"tcp_start":[0.48244,-0.01287,0.28459],"tcp_to_object_dist_end":0.01948,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47607,-0.01959,0.02578],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28822,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13781,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11799.0,"raw_peak_contact_force":0.1903,"subtask_id":"grasp_1","tcp_end":[0.46446,-0.01947,0.03726],"tcp_start":[0.47224,-0.01964,0.04509],"tcp_to_object_dist_end":0.01632,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":570.0,"n_steps_budget":1000.0,"object_pos_end":[0.47058,-0.01948,0.19376],"object_pos_start":[0.47607,-0.01959,0.02578],"object_to_goal_dist_end":0.24043,"object_to_goal_dist_start":0.28822,"object_z_max":0.19348,"peak_contact_force":0.0779,"phase_name":"lift_vertical","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":23390.0,"raw_peak_contact_force":0.51103,"tcp_end":[0.46139,-0.01937,0.2094],"tcp_start":[0.46446,-0.01947,0.03726],"tcp_to_object_dist_end":0.01814,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":444.0,"n_steps_budget":1000.0,"object_pos_end":[0.55427,0.07297,0.22347],"object_pos_start":[0.47058,-0.01948,0.19376],"object_to_goal_dist_end":0.12044,"object_to_goal_dist_start":0.24043,"object_z_max":0.22857,"peak_contact_force":0.0,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":16780.0,"raw_peak_contact_force":0.22713,"subtask_id":"transport_arc","tcp_end":[0.57464,0.10366,0.25262],"tcp_start":[0.56356,0.09129,0.24965],"tcp_to_object_dist_end":0.04697,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":477.0,"n_steps_budget":1000.0,"object_pos_end":[0.62714,0.15483,0.15842],"object_pos_start":[0.58132,0.10352,0.22863],"object_to_goal_dist_end":0.03218,"object_to_goal_dist_start":0.08426,"object_z_max":0.22863,"peak_contact_force":0.09801,"phase_name":"place_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16939.0,"raw_peak_contact_force":0.22178,"tcp_end":[0.62402,0.15465,0.1851],"tcp_start":[0.57464,0.10366,0.25262],"tcp_to_object_dist_end":0.02686,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61397,0.1383,0.01357],"object_pos_start":[0.62714,0.15483,0.15842],"object_to_goal_dist_end":0.17853,"object_to_goal_dist_start":0.03218,"object_z_max":0.15842,"peak_contact_force":0.0859,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2515.0,"raw_peak_contact_force":1.77377,"subtask_id":"release_1","tcp_end":[0.61844,0.15311,0.20454],"tcp_start":[0.62402,0.15465,0.1851],"tcp_to_object_dist_end":0.19159,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```