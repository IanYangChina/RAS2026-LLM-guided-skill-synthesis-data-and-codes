## Search State

- **Seed**: 0
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0352 | 0.18 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0204 | 0.22 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2553 | 0.32 | ✅ accepted |
| 2 | approach → descend → grasp → approach → release | linear_cartesian | linear_cartesian | — | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 2 | 0.1528 | 0.25 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 4 | 0.2796 | 0.21 | ❌ rejected |

**Proposal policy**: task_score is 0.18 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.035) — your mutation base

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
- id: lift_transport
  type: lift
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: target.offset.z
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
  guards:
  - id: grasp_retention
    when: during_phase
    predicate: bilateral_grasp
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: transport_arc
- id: place_approach
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
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: release_1
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
- **lift_transport** (`lift`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=grasp_retention, when=during_phase, predicate=bilateral_grasp, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=reduce_speed
- **place_approach** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=placement_surface, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
- **release_1** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.035
- **task_score** (E): 0.180
- **fitness_score**: 0.555  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0940 |
| descend_1 | 1.00 | 1.00 | 0.1721 |
| grasp_1 | 1.00 | 1.00 | 0.0117 |
| lift_straight | 0.00 | 0.33 | 0.0006 |
| transport_arc | 0.00 | 1.00 | 0.2452 |
| descend_to_goal | 1.00 | 1.00 | 0.2938 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, -0.000, 0.224) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.495, -0.000, 0.224)→(0.492, 0.001, 0.052) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.492, 0.001, 0.052)→(0.484, 0.000, 0.044) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 | 1.00 / 41.333 | 0.147 | 0.191 |
| lift_straight | lift | 0.00 / guard_failure | (0.487, 0.000, 0.174)→(0.487, 0.000, 0.175) | (0.497, 0.001, 0.026)→(0.504, 0.001, 0.133) | 0.266→0.217 | 0.33 / 1.000 | 0.001 | 0.470 |
| transport_arc | approach | 0.00 / step_budget | (0.487, 0.000, 0.175)→(0.496, 0.027, 0.414) | (0.504, 0.002, 0.142)→(0.514, 0.010, 0.016) | 0.210→0.259 | 1.00 / 8.000 | 3249.651 | 1.594 |
| descend_to_goal | descend | 1.00 / step_budget | (0.496, 0.027, 0.414)→(0.577, 0.179, 0.187) | (0.514, 0.010, 0.016)→(0.514, 0.010, 0.016) | 0.259→0.259 | 1.00 / 8.000 | 3249.753 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.219
- phase_score: 0.357
- phase_breakdown.approach_1_score: 0.011
- phase_breakdown.descend_1_score: 0.808
- phase_breakdown.transport_arc_score: 0.005
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.819
- grasp_place_fitness: 0.566

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.566
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.219
- **Median Q (composite search score)**: 0.033
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.299


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.525,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06997,"descend_1.grasp_z_offset":0.01684,"descend_to_goal.place_speed":0.3367,"lift_straight.lift_height":0.25913,"lift_straight.lift_speed":0.34673,"transport_arc.transport_arc_height":0.21293,"transport_arc.transport_height":0.30324,"transport_arc.transport_speed":0.34409},"optimized_scores":{"best_composite_score":0.03281,"best_fitness_score":0.55281,"best_task_score":0.17121},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3704.0,"contact_point_centroid":[0.52951,-0.01284,-0.00224],"force_p95":0.12752,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.56949,"mean_force":0.13488,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48129,-0.08577,0.34327]},{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.51186,-0.02231,-0.00123],"force_p95":0.29052,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48109,"mean_force":0.07919,"phase_index":3.0,"phase_name":"lift_straight","phase_type":"lift","tcp_position_centroid":[0.49873,-0.02233,0.0436]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5145.0,"contact_point_centroid":[0.50261,-0.00338,0.0952],"force_p95":0.13116,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34401,"mean_force":0.07847,"phase_index":3.0,"phase_name":"lift_straight","phase_type":"lift","tcp_position_centroid":[0.49926,-0.02226,0.09301]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5582.0,"contact_point_centroid":[0.50252,-0.04104,0.09233],"force_p95":0.12953,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29922,"mean_force":0.07379,"phase_index":3.0,"phase_name":"lift_straight","phase_type":"lift","tcp_position_centroid":[0.49919,-0.02226,0.09079]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8.0,"contact_point_centroid":[0.50912,-0.00378,0.16304],"force_p95":0.20751,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2161,"mean_force":0.11196,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50184,-0.0222,0.17028]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51371,-0.02289,-0.00206],"force_p95":0.14013,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18196,"mean_force":0.12738,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50126,-0.0224,0.04325]},{"body_a":"world","body_b":"grasp_target","contact_count":2384.0,"contact_point_centroid":[0.5137,-0.02302,-0.00194],"force_p95":0.13098,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50324,-0.0105,0.20373]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4105.0,"contact_point_centroid":[0.50078,-0.00316,0.04472],"force_p95":0.07777,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1323,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50009,-0.02237,0.04197]},{"body_a":"world","body_b":"grasp_target","contact_count":756.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50734,-0.0219,0.07944]},{"body_a":"world","body_b":"grasp_target","contact_count":3200.0,"contact_point_centroid":[0.52957,-0.01284,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.52552,0.05983,0.36287]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4910.0,"contact_point_centroid":[0.50081,-0.04145,0.04379],"force_p95":0.06994,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08108,"mean_force":0.04466,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50009,-0.02237,0.04198]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3624.0,"contact_point_centroid":[0.481,-0.08847,0.3577],"force_p95":0.01106,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01623,"mean_force":0.01064,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48061,-0.08846,0.35546]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3440.0,"contact_point_centroid":[0.52579,0.05942,0.3659],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01283,"mean_force":0.01038,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.52541,0.05942,0.36354]}],"total_contact_groups":13},"final_pose_error":0.00986,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.52957,-0.01284,0.01602],"final_tcp_position":[0.54891,0.14407,0.22558],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":9749.01316,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":597.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2384.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50869,-0.02133,0.10826],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08241,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":189.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":756.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50817,-0.02256,0.05097],"tcp_start":[0.50869,-0.02133,0.10826],"tcp_to_object_dist_end":0.02556,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51361,-0.02238,0.02578],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26538,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.13695,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10815.0,"raw_peak_contact_force":0.18196,"subtask_id":"grasp_1","tcp_end":[0.50006,-0.02237,0.04194],"tcp_start":[0.50817,-0.02256,0.05097],"tcp_to_object_dist_end":0.02109,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":394.0,"n_steps_budget":600.0,"object_pos_end":[0.52058,-0.02233,0.11103],"object_pos_start":[0.51361,-0.02238,0.02578],"object_to_goal_dist_end":0.20906,"object_to_goal_dist_start":0.26538,"object_z_max":0.14272,"peak_contact_force":0.00299,"phase_name":"lift_straight","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10875.0,"raw_peak_contact_force":0.48109,"tcp_end":[0.5019,-0.02217,0.17022],"tcp_start":[0.50186,-0.02218,0.16871],"tcp_to_object_dist_end":0.06207,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52957,-0.01284,0.01602],"object_pos_start":[0.51995,-0.02139,0.14187],"object_to_goal_dist_end":0.26473,"object_to_goal_dist_start":0.19373,"object_z_max":0.14187,"peak_contact_force":9748.70668,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7336.0,"raw_peak_contact_force":1.56949,"subtask_id":"transport_arc","tcp_end":[0.50169,-0.02447,0.50468],"tcp_start":[0.5019,-0.02217,0.17022],"tcp_to_object_dist_end":0.48959,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":800.0,"n_steps_budget":1000.0,"object_pos_end":[0.52957,-0.01284,0.01602],"object_pos_start":[0.52957,-0.01284,0.01602],"object_to_goal_dist_end":0.26473,"object_to_goal_dist_start":0.26473,"object_z_max":0.01602,"peak_contact_force":9749.01316,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6640.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.54891,0.14407,0.22558],"tcp_start":[0.50169,-0.02447,0.50468],"tcp_to_object_dist_end":0.26251,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.42857,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.22063,"descend_1.grasp_z_offset":0.02496,"descend_to_goal.place_speed":0.18586,"lift_straight.lift_height":0.27618,"lift_straight.lift_speed":0.23775,"transport_arc.transport_arc_height":0.11943,"transport_arc.transport_height":0.22648,"transport_arc.transport_speed":0.2594},"optimized_scores":{"best_composite_score":0.04626,"best_fitness_score":0.56626,"best_task_score":0.21864},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3742.0,"contact_point_centroid":[0.51723,0.06403,-0.00222],"force_p95":0.12763,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.4695,"mean_force":0.13469,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49129,0.05132,0.29306]},{"body_a":"world","body_b":"grasp_target","contact_count":134.0,"contact_point_centroid":[0.49976,0.04272,-0.00153],"force_p95":0.22891,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38964,"mean_force":0.06817,"phase_index":3.0,"phase_name":"lift_straight","phase_type":"lift","tcp_position_centroid":[0.48748,0.04323,0.05244]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3173.0,"contact_point_centroid":[0.49085,0.02451,0.08837],"force_p95":0.15886,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38949,"mean_force":0.10121,"phase_index":3.0,"phase_name":"lift_straight","phase_type":"lift","tcp_position_centroid":[0.48759,0.0431,0.09067]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4714.0,"contact_point_centroid":[0.48997,0.06136,0.08998],"force_p95":0.14493,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28161,"mean_force":0.07575,"phase_index":3.0,"phase_name":"lift_straight","phase_type":"lift","tcp_position_centroid":[0.48759,0.0431,0.09075]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50121,0.04496,-0.00216],"force_p95":0.16888,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21589,"mean_force":0.13395,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48989,0.04347,0.05211]},{"body_a":"world","body_b":"grasp_target","contact_count":828.0,"contact_point_centroid":[0.50118,0.04505,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12322,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49837,0.01741,0.27696]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3415.0,"contact_point_centroid":[0.49114,0.02419,0.05034],"force_p95":0.10843,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12861,"mean_force":0.06324,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48877,0.04337,0.05088]},{"body_a":"world","body_b":"grasp_target","contact_count":2396.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49626,0.04019,0.15594]},{"body_a":"world","body_b":"grasp_target","contact_count":2988.0,"contact_point_centroid":[0.51729,0.06406,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.53891,0.18245,0.26472]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5005.0,"contact_point_centroid":[0.48899,0.06212,0.05109],"force_p95":0.072,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07546,"mean_force":0.04264,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48877,0.04337,0.05089]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3693.0,"contact_point_centroid":[0.49229,0.05293,0.30377],"force_p95":0.01112,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01623,"mean_force":0.01061,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49194,0.05292,0.30154]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3190.0,"contact_point_centroid":[0.53935,0.1826,0.26674],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01292,"mean_force":0.01044,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.53895,0.18258,0.26444]}],"total_contact_groups":12},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.51729,0.06406,0.01602],"final_tcp_position":[0.55853,0.23763,0.15034],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.4695,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":208.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":828.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49812,0.0365,0.25428],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22845,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":599.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2396.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49664,0.04407,0.05957],"tcp_start":[0.49812,0.0365,0.25428],"tcp_to_object_dist_end":0.03387,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50114,0.04367,0.02535],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24337,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16937,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10220.0,"raw_peak_contact_force":0.21589,"subtask_id":"grasp_1","tcp_end":[0.48874,0.04336,0.05085],"tcp_start":[0.49664,0.04407,0.05957],"tcp_to_object_dist_end":0.02835,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":347.0,"n_steps_budget":690.0,"object_pos_end":[0.50211,0.0455,0.1242],"object_pos_start":[0.50114,0.04367,0.02535],"object_to_goal_dist_end":0.21009,"object_to_goal_dist_start":0.24337,"object_z_max":0.12438,"peak_contact_force":0.0,"phase_name":"lift_straight","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8021.0,"raw_peak_contact_force":0.38964,"tcp_end":[0.49043,0.04313,0.16243],"tcp_start":[0.49043,0.04313,0.16239],"tcp_to_object_dist_end":0.04004,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51729,0.06406,0.01602],"object_pos_start":[0.50389,0.04827,0.12063],"object_to_goal_dist_end":0.22805,"object_to_goal_dist_start":0.20736,"object_z_max":0.12063,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7435.0,"raw_peak_contact_force":1.4695,"subtask_id":"transport_arc","tcp_end":[0.52016,0.12744,0.38445],"tcp_start":[0.49043,0.04313,0.16243],"tcp_to_object_dist_end":0.37386,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":747.0,"n_steps_budget":1000.0,"object_pos_end":[0.51729,0.06406,0.01602],"object_pos_start":[0.51729,0.06406,0.01602],"object_to_goal_dist_end":0.22805,"object_to_goal_dist_start":0.22805,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6178.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.55853,0.23763,0.15034],"tcp_start":[0.52016,0.12744,0.38445],"tcp_to_object_dist_end":0.22331,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.20611,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.28973,"descend_1.grasp_z_offset":0.0118,"descend_to_goal.place_speed":0.48411,"lift_straight.lift_height":0.27051,"lift_straight.lift_speed":0.33855,"transport_arc.transport_arc_height":0.13105,"transport_arc.transport_height":0.23472,"transport_arc.transport_speed":0.1462},"optimized_scores":{"best_composite_score":0.02665,"best_fitness_score":0.54665,"best_task_score":0.149},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3675.0,"contact_point_centroid":[0.49583,-0.02212,-0.00229],"force_p95":0.12438,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.74213,"mean_force":0.13451,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.45478,-0.03211,0.27999]},{"body_a":"world","body_b":"grasp_target","contact_count":137.0,"contact_point_centroid":[0.47464,-0.01976,-0.00113],"force_p95":0.42997,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53879,"mean_force":0.06791,"phase_index":3.0,"phase_name":"lift_straight","phase_type":"lift","tcp_position_centroid":[0.46297,-0.01964,0.04084]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5445.0,"contact_point_centroid":[0.46636,-0.00066,0.09605],"force_p95":0.12612,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33465,"mean_force":0.0731,"phase_index":3.0,"phase_name":"lift_straight","phase_type":"lift","tcp_position_centroid":[0.46368,-0.0196,0.09376]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5848.0,"contact_point_centroid":[0.46625,-0.03848,0.09388],"force_p95":0.12459,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2976,"mean_force":0.06948,"phase_index":3.0,"phase_name":"lift_straight","phase_type":"lift","tcp_position_centroid":[0.4636,-0.0196,0.09225]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02007,-0.00204],"force_p95":0.13509,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17399,"mean_force":0.12604,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46538,-0.0197,0.04017]},{"body_a":"world","body_b":"grasp_target","contact_count":740.0,"contact_point_centroid":[0.47616,-0.02015,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12329,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48803,-0.00839,0.30457]},{"body_a":"world","body_b":"grasp_target","contact_count":3284.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47419,-0.01805,0.1774]},{"body_a":"world","body_b":"grasp_target","contact_count":3924.0,"contact_point_centroid":[0.49579,-0.02213,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.54732,0.06997,0.26351]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4839.0,"contact_point_centroid":[0.46431,-0.00046,0.04144],"force_p95":0.06742,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09662,"mean_force":0.04487,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46428,-0.01968,0.03907]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5143.0,"contact_point_centroid":[0.46417,-0.03889,0.04097],"force_p95":0.06609,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08297,"mean_force":0.04293,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46428,-0.01968,0.03907]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3623.0,"contact_point_centroid":[0.45478,-0.03244,0.28688],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01612,"mean_force":0.01066,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.4545,-0.03244,0.28459]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4185.0,"contact_point_centroid":[0.54769,0.07007,0.26564],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01284,"mean_force":0.01045,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.54741,0.07007,0.26342]}],"total_contact_groups":12},"final_pose_error":0.01053,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.49579,-0.02213,0.01602],"final_tcp_position":[0.62373,0.15397,0.18507],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.74213,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":186.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":740.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47827,-0.01631,0.3108],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.28482,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":821.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3284.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47201,-0.01985,0.04688],"tcp_start":[0.47827,-0.01631,0.3108],"tcp_to_object_dist_end":0.02127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47606,-0.01975,0.02584],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28829,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13361,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11782.0,"raw_peak_contact_force":0.17399,"subtask_id":"grasp_1","tcp_end":[0.46425,-0.01967,0.03904],"tcp_start":[0.47201,-0.01985,0.04688],"tcp_to_object_dist_end":0.01771,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":387.0,"n_steps_budget":600.0,"object_pos_end":[0.48857,-0.01981,0.16421],"object_pos_start":[0.47606,-0.01975,0.02584],"object_to_goal_dist_end":0.23047,"object_to_goal_dist_start":0.28829,"object_z_max":0.16444,"peak_contact_force":0.0,"phase_name":"lift_straight","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11430.0,"raw_peak_contact_force":0.53879,"tcp_end":[0.46885,-0.01962,0.19128],"tcp_start":[0.46872,-0.01962,0.19112],"tcp_to_object_dist_end":0.03349,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49579,-0.02213,0.01602],"object_pos_start":[0.48883,-0.01984,0.16386],"object_to_goal_dist_end":0.28557,"object_to_goal_dist_start":0.23036,"object_z_max":0.16386,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7298.0,"raw_peak_contact_force":1.74213,"subtask_id":"transport_arc","tcp_end":[0.46489,-0.02181,0.35294],"tcp_start":[0.46885,-0.01962,0.19128],"tcp_to_object_dist_end":0.33833,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":981.0,"n_steps_budget":1000.0,"object_pos_end":[0.49579,-0.02213,0.01602],"object_pos_start":[0.49579,-0.02213,0.01602],"object_to_goal_dist_end":0.28557,"object_to_goal_dist_start":0.28557,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8109.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.62373,0.15397,0.18507],"tcp_start":[0.46489,-0.02181,0.35294],"tcp_to_object_dist_end":0.2756,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```