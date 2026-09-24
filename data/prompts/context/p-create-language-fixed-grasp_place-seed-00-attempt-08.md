## Search State

- **Seed**: 0
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2618 | 0.32 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.0590 | 0.19 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1378 | 0.24 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0352 | 0.18 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0204 | 0.22 | ❌ rejected |

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

## Current Skill (Q=0.262) — your mutation base

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

- **Composite score**: 0.262
- **task_score** (E): 0.316
- **fitness_score**: 0.632  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1351 |
| descend_1 | 1.00 | 1.00 | 0.1244 |
| grasp_1 | 1.00 | 1.00 | 0.0117 |
| lift_transport | 0.00 | 0.67 | 0.0002 |
| place_approach | 1.00 | 1.00 | 0.0861 |
| release_1 | 1.00 | 1.00 | 0.0220 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.001, 0.170) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.494, 0.001, 0.170)→(0.492, 0.001, 0.045) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.492, 0.001, 0.045)→(0.484, 0.000, 0.037) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 | 1.00 / 43.667 | 0.142 | 0.192 |
| lift_transport | lift | 0.00 / guard_failure | (0.540, 0.114, 0.180)→(0.540, 0.115, 0.180) | (0.497, 0.001, 0.026)→(0.559, 0.114, 0.156) | 0.266→0.091 | 0.67 / 2.667 | 0.000 | 0.463 |
| place_approach | approach | 1.00 / step_budget | (0.540, 0.115, 0.180)→(0.577, 0.178, 0.178) | (0.564, 0.120, 0.153)→(0.593, 0.149, 0.016) | 0.084→0.176 | 1.00 / 8.000 | 6499.337 | 1.706 |
| release_1 | release | 1.00 / step_budget | (0.577, 0.178, 0.178)→(0.571, 0.176, 0.199) | (0.593, 0.149, 0.016)→(0.593, 0.149, 0.016) | 0.176→0.176 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.413
- phase_score: 0.505
- phase_breakdown.approach_1_score: 0.058
- phase_breakdown.descend_1_score: 0.879
- phase_breakdown.transport_arc_score: 0.311
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.620
- grasp_place_fitness: 0.679

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.679
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.413
- **Median Q (composite search score)**: 0.251
- **K-run variance**: 0.0012
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.430


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0625,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13364,"descend_1.grasp_z_offset":0.01022,"lift_transport.lift_height":0.06699,"lift_transport.lift_speed":0.45845,"place_approach.place_speed":0.09568},"optimized_scores":{"best_composite_score":0.22545,"best_fitness_score":0.59545,"best_task_score":0.24296},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3464.0,"contact_point_centroid":[0.58412,0.1089,-0.00234],"force_p95":0.20447,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.55049,"mean_force":0.14336,"phase_index":4.0,"phase_name":"place_approach","phase_type":"approach","tcp_position_centroid":[0.53696,0.11217,0.18687]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.51316,-0.02029,-0.0012],"force_p95":0.34558,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54067,"mean_force":0.21644,"phase_index":3.0,"phase_name":"lift_transport","phase_type":"lift","tcp_position_centroid":[0.49959,-0.02034,0.03758]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4454.0,"contact_point_centroid":[0.5101,-0.0097,0.07978],"force_p95":0.13297,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3333,"mean_force":0.07959,"phase_index":3.0,"phase_name":"lift_transport","phase_type":"lift","tcp_position_centroid":[0.50702,0.00926,0.07767]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4915.0,"contact_point_centroid":[0.51178,0.03264,0.08605],"force_p95":0.11963,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31031,"mean_force":0.07166,"phase_index":3.0,"phase_name":"lift_transport","phase_type":"lift","tcp_position_centroid":[0.5084,0.01393,0.08424]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5137,-0.02287,-0.00205],"force_p95":0.1382,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17188,"mean_force":0.12684,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50165,-0.02249,0.03708]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":28.0,"contact_point_centroid":[0.53176,0.08173,0.15466],"force_p95":0.10743,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14566,"mean_force":0.04467,"phase_index":4.0,"phase_name":"place_approach","phase_type":"approach","tcp_position_centroid":[0.52475,0.06721,0.15956]},{"body_a":"world","body_b":"grasp_target","contact_count":1608.0,"contact_point_centroid":[0.5137,-0.02302,-0.00191],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50333,-0.00999,0.23605]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4104.0,"contact_point_centroid":[0.50103,-0.00326,0.03857],"force_p95":0.07744,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12621,"mean_force":0.05181,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50047,-0.02246,0.0358]},{"body_a":"world","body_b":"grasp_target","contact_count":1580.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5074,-0.02157,0.10784]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58409,0.11021,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54367,0.14017,0.21028]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4905.0,"contact_point_centroid":[0.50108,-0.04155,0.03763],"force_p95":0.06956,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09037,"mean_force":0.04472,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50048,-0.02246,0.03581]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3678.0,"contact_point_centroid":[0.53741,0.11252,0.18937],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01621,"mean_force":0.01053,"phase_index":4.0,"phase_name":"place_approach","phase_type":"approach","tcp_position_centroid":[0.53707,0.11252,0.18711]},{"body_a":"left_finger","body_b":"right_finger","contact_count":232.0,"contact_point_centroid":[0.54654,0.14087,0.20748],"force_p95":0.01083,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01251,"mean_force":0.00961,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54606,0.14086,0.20557]}],"total_contact_groups":13},"final_pose_error":0.01891,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.58409,0.11021,0.01602],"final_tcp_position":[0.54725,0.14108,0.20789],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":9749.04171,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":403.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1608.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50876,-0.02058,0.17186],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14594,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":395.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1580.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50867,-0.02265,0.04484],"tcp_start":[0.50876,-0.02058,0.17186],"tcp_to_object_dist_end":0.01949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51359,-0.0224,0.02581],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26537,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.13505,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10809.0,"raw_peak_contact_force":0.17188,"subtask_id":"grasp_1","tcp_end":[0.50044,-0.02246,0.03577],"tcp_start":[0.50867,-0.02265,0.04484],"tcp_to_object_dist_end":0.01649,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":335.0,"n_steps_budget":600.0,"object_pos_end":[0.5478,0.06691,0.13924],"object_pos_start":[0.51359,-0.0224,0.02581],"object_to_goal_dist_end":0.11861,"object_to_goal_dist_start":0.26537,"object_z_max":0.13929,"peak_contact_force":0.0,"phase_name":"lift_transport","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9515.0,"raw_peak_contact_force":0.54067,"subtask_id":"transport_arc","tcp_end":[0.52474,0.06699,0.15953],"tcp_start":[0.52473,0.06687,0.15945],"tcp_to_object_dist_end":0.03071,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.58409,0.11021,0.01602],"object_pos_start":[0.55043,0.07019,0.13836],"object_to_goal_dist_end":0.21223,"object_to_goal_dist_start":0.11681,"object_z_max":0.13836,"peak_contact_force":9749.04171,"phase_name":"place_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7170.0,"raw_peak_contact_force":1.55049,"subtask_id":"release_1","tcp_end":[0.54725,0.14108,0.20789],"tcp_start":[0.52474,0.06699,0.15953],"tcp_to_object_dist_end":0.1978,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58409,0.11021,0.01602],"object_pos_start":[0.58409,0.11021,0.01602],"object_to_goal_dist_end":0.21223,"object_to_goal_dist_start":0.21223,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1032.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.54232,0.13978,0.23058],"tcp_start":[0.54725,0.14108,0.20789],"tcp_to_object_dist_end":0.22058,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92453,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13452,"descend_1.grasp_z_offset":0.01116,"lift_transport.lift_height":0.08397,"lift_transport.lift_speed":0.48424,"place_approach.place_speed":0.279},"optimized_scores":{"best_composite_score":0.30923,"best_fitness_score":0.67923,"best_task_score":0.41272},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":821.0,"contact_point_centroid":[0.5835,0.23268,-0.00322],"force_p95":0.60874,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.77222,"mean_force":0.1769,"phase_index":4.0,"phase_name":"place_approach","phase_type":"approach","tcp_position_centroid":[0.55267,0.22539,0.15545]},{"body_a":"world","body_b":"grasp_target","contact_count":188.0,"contact_point_centroid":[0.50187,0.04737,-0.00143],"force_p95":0.36745,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45827,"mean_force":0.25198,"phase_index":3.0,"phase_name":"lift_transport","phase_type":"lift","tcp_position_centroid":[0.48804,0.04663,0.03879]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6995.0,"contact_point_centroid":[0.51384,0.12702,0.09654],"force_p95":0.11562,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33419,"mean_force":0.07369,"phase_index":3.0,"phase_name":"lift_transport","phase_type":"lift","tcp_position_centroid":[0.51006,0.10841,0.09517]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6021.0,"contact_point_centroid":[0.51171,0.08424,0.09229],"force_p95":0.1397,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25806,"mean_force":0.0859,"phase_index":3.0,"phase_name":"lift_transport","phase_type":"lift","tcp_position_centroid":[0.50803,0.10315,0.0902]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50123,0.04481,-0.00214],"force_p95":0.16315,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22983,"mean_force":0.13323,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48955,0.04354,0.03836]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4074.0,"contact_point_centroid":[0.48883,0.02416,0.03996],"force_p95":0.08269,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1573,"mean_force":0.05215,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48841,0.04344,0.03714]},{"body_a":"world","body_b":"grasp_target","contact_count":1656.0,"contact_point_centroid":[0.50118,0.04505,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49788,0.01962,0.23612]},{"body_a":"world","body_b":"grasp_target","contact_count":1588.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4957,0.04214,0.10852]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58388,0.23276,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55374,0.23611,0.14497]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5514.0,"contact_point_centroid":[0.48813,0.06257,0.03975],"force_p95":0.06993,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07617,"mean_force":0.04062,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48841,0.04344,0.03714]},{"body_a":"left_finger","body_b":"right_finger","contact_count":621.0,"contact_point_centroid":[0.55465,0.22907,0.15395],"force_p95":0.0136,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01534,"mean_force":0.01104,"phase_index":4.0,"phase_name":"place_approach","phase_type":"approach","tcp_position_centroid":[0.55419,0.22904,0.15185]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.55693,0.23745,0.14293],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01101,"mean_force":0.01013,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55646,0.23741,0.14072]}],"total_contact_groups":12},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.58388,0.23276,0.01602],"final_tcp_position":[0.55805,0.23787,0.14368],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.77222,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":415.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1656.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49756,0.04036,0.17229],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14639,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":397.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1588.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.4964,0.04416,0.04578],"tcp_start":[0.49756,0.04036,0.17229],"tcp_to_object_dist_end":0.02035,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50113,0.04362,0.02552],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24332,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15618,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11388.0,"raw_peak_contact_force":0.22983,"subtask_id":"grasp_1","tcp_end":[0.48838,0.04343,0.03711],"tcp_start":[0.4964,0.04416,0.04578],"tcp_to_object_dist_end":0.01723,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":506.0,"n_steps_budget":600.0,"object_pos_end":[0.56289,0.20253,0.15745],"object_pos_start":[0.50113,0.04362,0.02552],"object_to_goal_dist_end":0.04369,"object_to_goal_dist_start":0.24332,"object_z_max":0.15748,"peak_contact_force":0.0,"phase_name":"lift_transport","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13204.0,"raw_peak_contact_force":0.45827,"subtask_id":"transport_arc","tcp_end":[0.54555,0.20331,0.18321],"tcp_start":[0.54569,0.20303,0.18332],"tcp_to_object_dist_end":0.03107,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":273.0,"n_steps_budget":1000.0,"object_pos_end":[0.58388,0.23276,0.01602],"object_pos_start":[0.56655,0.21082,0.15086],"object_to_goal_dist_end":0.13275,"object_to_goal_dist_start":0.03436,"object_z_max":0.15086,"peak_contact_force":0.12262,"phase_name":"place_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1442.0,"raw_peak_contact_force":1.77222,"subtask_id":"release_1","tcp_end":[0.55805,0.23787,0.14368],"tcp_start":[0.54555,0.20331,0.18321],"tcp_to_object_dist_end":0.13035,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58388,0.23276,0.01602],"object_pos_start":[0.58388,0.23276,0.01602],"object_to_goal_dist_end":0.13275,"object_to_goal_dist_start":0.13275,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.55211,0.23534,0.16489],"tcp_start":[0.55805,0.23787,0.14368],"tcp_to_object_dist_end":0.15225,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.08421,"average_solve_count":95.0,"average_success_count":95.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12513,"descend_1.grasp_z_offset":0.01023,"lift_transport.lift_height":0.16774,"lift_transport.lift_speed":0.40787,"place_approach.place_speed":0.48416},"optimized_scores":{"best_composite_score":0.25066,"best_fitness_score":0.62066,"best_task_score":0.29371},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3677.0,"contact_point_centroid":[0.61216,0.10316,-0.00227],"force_p95":0.12581,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79504,"mean_force":0.13645,"phase_index":4.0,"phase_name":"place_approach","phase_type":"approach","tcp_position_centroid":[0.59151,0.12079,0.18517]},{"body_a":"world","body_b":"grasp_target","contact_count":121.0,"contact_point_centroid":[0.47866,-0.01707,-0.00114],"force_p95":0.28,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38934,"mean_force":0.1949,"phase_index":3.0,"phase_name":"lift_transport","phase_type":"lift","tcp_position_centroid":[0.46446,-0.01793,0.03934]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5209.0,"contact_point_centroid":[0.49905,0.03558,0.10007],"force_p95":0.12241,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31832,"mean_force":0.0715,"phase_index":3.0,"phase_name":"lift_transport","phase_type":"lift","tcp_position_centroid":[0.49574,0.0169,0.09846]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4635.0,"contact_point_centroid":[0.49472,-0.00635,0.09318],"force_p95":0.13794,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24353,"mean_force":0.07919,"phase_index":3.0,"phase_name":"lift_transport","phase_type":"lift","tcp_position_centroid":[0.49175,0.01264,0.09104]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02006,-0.00204],"force_p95":0.13562,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17554,"mean_force":0.12619,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46515,-0.01967,0.03838]},{"body_a":"world","body_b":"grasp_target","contact_count":1624.0,"contact_point_centroid":[0.47616,-0.02015,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48703,-0.00872,0.23282]},{"body_a":"world","body_b":"grasp_target","contact_count":1532.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4722,-0.01887,0.10447]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.61228,0.10322,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62085,0.15429,0.18179]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2.0,"contact_point_centroid":[0.55596,0.08547,0.18895],"force_p95":0.09555,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09989,"mean_force":0.05647,"phase_index":4.0,"phase_name":"place_approach","phase_type":"approach","tcp_position_centroid":[0.54841,0.07329,0.19625]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5075.0,"contact_point_centroid":[0.46374,-0.00039,0.03991],"force_p95":0.06572,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09696,"mean_force":0.04293,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46404,-0.01964,0.03729]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5392.0,"contact_point_centroid":[0.46362,-0.03889,0.03941],"force_p95":0.0647,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08472,"mean_force":0.04114,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46405,-0.01964,0.03729]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3698.0,"contact_point_centroid":[0.5936,0.1226,0.18718],"force_p95":0.01106,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01808,"mean_force":0.01059,"phase_index":4.0,"phase_name":"place_approach","phase_type":"approach","tcp_position_centroid":[0.59324,0.12259,0.18495]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.62396,0.15511,0.18061],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01265,"mean_force":0.00999,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62354,0.1551,0.17843]}],"total_contact_groups":13},"final_pose_error":0.01139,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.61228,0.10322,0.01602],"final_tcp_position":[0.62489,0.15536,0.1815],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":9748.8452,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":407.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1624.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47512,-0.01802,0.16474],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13874,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":383.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1532.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47178,-0.01982,0.04507],"tcp_start":[0.47512,-0.01802,0.16474],"tcp_to_object_dist_end":0.01955,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47606,-0.01972,0.02583],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28827,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13405,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12267.0,"raw_peak_contact_force":0.17554,"subtask_id":"grasp_1","tcp_end":[0.46402,-0.01964,0.03726],"tcp_start":[0.47178,-0.01982,0.04507],"tcp_to_object_dist_end":0.0166,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":359.0,"n_steps_budget":630.0,"object_pos_end":[0.56751,0.0713,0.17039],"object_pos_start":[0.47606,-0.01972,0.02583],"object_to_goal_dist_end":0.11043,"object_to_goal_dist_start":0.28827,"object_z_max":0.17112,"peak_contact_force":0.0,"phase_name":"lift_transport","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9965.0,"raw_peak_contact_force":0.38934,"subtask_id":"transport_arc","tcp_end":[0.54842,0.07325,0.19626],"tcp_start":[0.54842,0.07317,0.19624],"tcp_to_object_dist_end":0.03221,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61228,0.10322,0.01602],"object_pos_start":[0.57455,0.07886,0.16897],"object_to_goal_dist_end":0.18378,"object_to_goal_dist_start":0.10065,"object_z_max":0.16897,"peak_contact_force":9748.8452,"phase_name":"place_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7377.0,"raw_peak_contact_force":1.79504,"subtask_id":"release_1","tcp_end":[0.62489,0.15536,0.1815],"tcp_start":[0.54842,0.07325,0.19626],"tcp_to_object_dist_end":0.17396,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61228,0.10322,0.01602],"object_pos_start":[0.61228,0.10322,0.01602],"object_to_goal_dist_end":0.18378,"object_to_goal_dist_start":0.18378,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.6193,0.15382,0.20114],"tcp_start":[0.62489,0.15536,0.1815],"tcp_to_object_dist_end":0.19204,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```