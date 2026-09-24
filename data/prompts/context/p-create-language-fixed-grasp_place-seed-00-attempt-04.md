## Search State

- **Seed**: 0
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0204 | 0.22 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2553 | 0.32 | ✅ accepted |
| 2 | approach → descend → grasp → approach → release | linear_cartesian | linear_cartesian | — | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 2 | 0.1528 | 0.25 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 4 | 0.2796 | 0.21 | ❌ rejected |
| 0 | approach → descend → grasp → approach → release | linear_cartesian | linear_cartesian | — | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | time_limit | 2 | 0.1529 | 0.25 | ✅ accepted |

**Proposal policy**: task_score is 0.22 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.020) — your mutation base

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

- **Composite score**: 0.020
- **task_score** (E): 0.216
- **fitness_score**: 0.570  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.550

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0501 |
| descend_1 | 1.00 | 1.00 | 0.2051 |
| grasp_1 | 1.00 | 1.00 | 0.0117 |
| lift_up | 0.33 | 1.00 | 0.0438 |
| transport_arc | 0.33 | 1.00 | 0.1924 |
| place_descend | 1.00 | 1.00 | 0.1134 |
| release_1 | 1.00 | 1.00 | 0.0216 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.001, 0.260) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 7.424 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.494, 0.001, 0.260)→(0.493, 0.001, 0.055) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.493, 0.001, 0.055)→(0.485, 0.000, 0.047) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 | 1.00 / 43.333 | 0.148 | 0.195 |
| lift_up | lift | 0.33 / guard_failure | (0.482, 0.000, 0.119)→(0.480, 0.000, 0.163) | (0.497, 0.001, 0.026)→(0.494, 0.001, 0.130) | 0.266→0.219 | 1.00 / 23.000 | 0.038 | 0.450 |
| transport_arc | approach | 0.33 / step_budget | (0.480, 0.000, 0.163)→(0.554, 0.125, 0.281) | (0.493, 0.001, 0.134)→(0.511, 0.054, 0.016) | 0.219→0.231 | 1.00 / 8.333 | 0.123 | 1.530 |
| place_descend | descend | 1.00 / step_budget | (0.554, 0.125, 0.281)→(0.577, 0.179, 0.188) | (0.511, 0.054, 0.016)→(0.511, 0.054, 0.016) | 0.231→0.231 | 1.00 / 8.667 | 185255.887 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.577, 0.179, 0.188)→(0.572, 0.177, 0.209) | (0.511, 0.054, 0.016)→(0.511, 0.054, 0.016) | 0.231→0.231 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.255
- phase_score: 0.372
- phase_breakdown.approach_1_score: 0.008
- phase_breakdown.descend_1_score: 0.892
- phase_breakdown.transport_arc_score: 0.070
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.628
- grasp_place_fitness: 0.592

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.592
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.255
- **Median Q (composite search score)**: 0.010
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.249


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.24401,"descend_1.grasp_z_offset":0.01825,"lift_up.grasp_force_threshold":0.17393,"lift_up.lift_height":0.14527,"lift_up.lift_speed":0.29397,"place_descend.place_speed":0.26213,"transport_arc.transport_height":0.1863,"transport_arc.transport_speed":0.24608},"optimized_scores":{"best_composite_score":0.00965,"best_fitness_score":0.55965,"best_task_score":0.18829},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3022.0,"contact_point_centroid":[0.51497,0.01468,-0.00235],"force_p95":0.12885,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.73745,"mean_force":0.13983,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.51792,0.05112,0.26424]},{"body_a":"world","body_b":"grasp_target","contact_count":129.0,"contact_point_centroid":[0.51118,-0.02214,-0.00113],"force_p95":0.24937,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47799,"mean_force":0.06256,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.49923,-0.02226,0.0458]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8539.0,"contact_point_centroid":[0.49944,-0.00329,0.09713],"force_p95":0.10588,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34597,"mean_force":0.06457,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.49691,-0.02219,0.09498]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8361.0,"contact_point_centroid":[0.49966,-0.04115,0.09834],"force_p95":0.10242,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30894,"mean_force":0.06644,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.49693,-0.02219,0.09655]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1744.0,"contact_point_centroid":[0.50317,0.00517,0.17718],"force_p95":0.14593,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23823,"mean_force":0.08319,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.4967,-0.01322,0.17784]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1534.0,"contact_point_centroid":[0.50298,-0.03276,0.17655],"force_p95":0.17453,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23758,"mean_force":0.09286,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.49651,-0.01417,0.17674]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51371,-0.02289,-0.00206],"force_p95":0.14136,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18349,"mean_force":0.1277,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50186,-0.02233,0.0452]},{"body_a":"world","body_b":"grasp_target","contact_count":484.0,"contact_point_centroid":[0.5137,-0.02302,-0.00174],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12364,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50285,-0.00752,0.28845]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4105.0,"contact_point_centroid":[0.50117,-0.00309,0.04668],"force_p95":0.07796,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13377,"mean_force":0.05185,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5007,-0.0223,0.04391]},{"body_a":"world","body_b":"grasp_target","contact_count":2724.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50686,-0.01924,0.16353]},{"body_a":"world","body_b":"grasp_target","contact_count":1408.0,"contact_point_centroid":[0.51499,0.01461,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.54016,0.11885,0.27457]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51499,0.01461,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54516,0.14367,0.22827]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4913.0,"contact_point_centroid":[0.50123,-0.04139,0.04575],"force_p95":0.07012,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07879,"mean_force":0.04465,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5007,-0.0223,0.04392]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2995.0,"contact_point_centroid":[0.5191,0.05373,0.27012],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01586,"mean_force":0.01058,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.51883,0.05373,0.26783]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1495.0,"contact_point_centroid":[0.54061,0.11891,0.27668],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01278,"mean_force":0.0105,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.54018,0.1189,0.27446]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.54787,0.14439,0.22589],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0126,"mean_force":0.01001,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54729,0.14437,0.22343]}],"total_contact_groups":16},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.51499,0.01461,0.01602],"final_tcp_position":[0.54873,0.14448,0.2264],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":273009.13438,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":122.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.2656,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":22.02735,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":484.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50706,-0.01606,0.27665],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25081,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":681.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.2656,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2724.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.50883,-0.02248,0.05299],"tcp_start":[0.50706,-0.01606,0.27665],"tcp_to_object_dist_end":0.02741,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51362,-0.02235,0.02577],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26536,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.13808,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10818.0,"raw_peak_contact_force":0.18349,"subtask_id":"grasp_1","tcp_end":[0.50067,-0.0223,0.04388],"tcp_start":[0.50883,-0.02248,0.05299],"tcp_to_object_dist_end":0.02227,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":529.0,"n_steps_budget":600.0,"object_pos_end":[0.51154,-0.02228,0.14068],"object_pos_start":[0.51362,-0.02235,0.02577],"object_to_goal_dist_end":0.19666,"object_to_goal_dist_start":0.26536,"object_z_max":0.14274,"peak_contact_force":0.0,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":17029.0,"raw_peak_contact_force":0.47799,"tcp_end":[0.49613,-0.02216,0.16907],"tcp_start":[0.49705,-0.02219,0.16671],"tcp_to_object_dist_end":0.03231,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51499,0.01461,0.01602],"object_pos_start":[0.51032,-0.02224,0.14287],"object_to_goal_dist_end":0.25047,"object_to_goal_dist_start":0.196,"object_z_max":0.15826,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9295.0,"raw_peak_contact_force":1.73745,"subtask_id":"transport_arc","tcp_end":[0.5333,0.09492,0.32433],"tcp_start":[0.49613,-0.02216,0.16907],"tcp_to_object_dist_end":0.31913,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":352.0,"n_steps_budget":1000.0,"object_pos_end":[0.51499,0.01461,0.01602],"object_pos_start":[0.51499,0.01461,0.01602],"object_to_goal_dist_end":0.25047,"object_to_goal_dist_start":0.25047,"object_z_max":0.01602,"peak_contact_force":273009.13438,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2903.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.54873,0.14448,0.2264],"tcp_start":[0.5333,0.09492,0.32433],"tcp_to_object_dist_end":0.24953,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51499,0.01461,0.01602],"object_pos_start":[0.51499,0.01461,0.01602],"object_to_goal_dist_end":0.25047,"object_to_goal_dist_start":0.25047,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.54394,0.14327,0.24858],"tcp_start":[0.54873,0.14448,0.2264],"tcp_to_object_dist_end":0.26735,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.99174,"average_solve_count":121.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.24235,"descend_1.grasp_z_offset":0.01871,"lift_up.grasp_force_threshold":0.1304,"lift_up.lift_height":0.22476,"lift_up.lift_speed":0.25664,"place_descend.place_speed":0.19967,"transport_arc.transport_height":0.16303,"transport_arc.transport_speed":0.15774},"optimized_scores":{"best_composite_score":0.04216,"best_fitness_score":0.59216,"best_task_score":0.25504},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2848.0,"contact_point_centroid":[0.5097,0.09674,-0.00232],"force_p95":0.12895,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.3576,"mean_force":0.13836,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50745,0.11103,0.19667]},{"body_a":"world","body_b":"grasp_target","contact_count":135.0,"contact_point_centroid":[0.49923,0.04337,-0.00144],"force_p95":0.26443,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47876,"mean_force":0.08835,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.48724,0.04323,0.04617]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5022.0,"contact_point_centroid":[0.48719,0.02402,0.08734],"force_p95":0.11477,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32783,"mean_force":0.06843,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.48518,0.04303,0.08542]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5657.0,"contact_point_centroid":[0.48737,0.06204,0.08634],"force_p95":0.11244,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32733,"mean_force":0.06339,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.4852,0.04303,0.08419]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2260.0,"contact_point_centroid":[0.49271,0.07462,0.15438],"force_p95":0.14534,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3017,"mean_force":0.09208,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.48598,0.05631,0.15433]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2076.0,"contact_point_centroid":[0.49223,0.03663,0.15405],"force_p95":0.15643,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24664,"mean_force":0.09355,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.4856,0.05513,0.15352]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04489,-0.00214],"force_p95":0.16131,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22351,"mean_force":0.13314,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48981,0.04347,0.0459]},{"body_a":"world","body_b":"grasp_target","contact_count":756.0,"contact_point_centroid":[0.50118,0.04505,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12327,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49838,0.01719,0.28564]},{"body_a":"world","body_b":"grasp_target","contact_count":2692.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49633,0.03978,0.16178]},{"body_a":"world","body_b":"grasp_target","contact_count":2360.0,"contact_point_centroid":[0.50973,0.09682,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.53963,0.19357,0.17927]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50973,0.09682,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55388,0.23626,0.14433]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4814.0,"contact_point_centroid":[0.4877,0.02405,0.04838],"force_p95":0.07114,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1082,"mean_force":0.04511,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48868,0.04336,0.04467]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5999.0,"contact_point_centroid":[0.48788,0.06263,0.04778],"force_p95":0.0664,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.06921,"mean_force":0.03769,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48868,0.04337,0.04468]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2781.0,"contact_point_centroid":[0.50914,0.11397,0.20122],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0165,"mean_force":0.01054,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.50865,0.11395,0.19899]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2515.0,"contact_point_centroid":[0.54012,0.1935,0.18152],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.01046,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.53958,0.19347,0.17935]},{"body_a":"left_finger","body_b":"right_finger","contact_count":222.0,"contact_point_centroid":[0.5571,0.23761,0.14222],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.01009,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55661,0.23758,0.14009]}],"total_contact_groups":16},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.50973,0.09682,0.01602],"final_tcp_position":[0.55818,0.23801,0.14302],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":273009.67134,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":190.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":756.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49818,0.03565,0.27253],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.24671,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":673.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2692.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49662,0.04407,0.05335],"tcp_start":[0.49818,0.03565,0.27253],"tcp_to_object_dist_end":0.02772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50116,0.04381,0.02549],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24318,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15673,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12613.0,"raw_peak_contact_force":0.22351,"subtask_id":"grasp_1","tcp_end":[0.48865,0.04336,0.04464],"tcp_start":[0.49662,0.04407,0.05335],"tcp_to_object_dist_end":0.02288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":321.0,"n_steps_budget":600.0,"object_pos_end":[0.50315,0.04358,0.11469],"object_pos_start":[0.50116,0.04381,0.02549],"object_to_goal_dist_end":0.21284,"object_to_goal_dist_start":0.24318,"object_z_max":0.1217,"peak_contact_force":0.0,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":10814.0,"raw_peak_contact_force":0.47876,"tcp_end":[0.4833,0.04285,0.14716],"tcp_start":[0.48513,0.04301,0.13881],"tcp_to_object_dist_end":0.03806,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50973,0.09682,0.01602],"object_pos_start":[0.50085,0.04345,0.12187],"object_to_goal_dist_end":0.20495,"object_to_goal_dist_start":0.21267,"object_z_max":0.13177,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9965.0,"raw_peak_contact_force":1.3576,"subtask_id":"transport_arc","tcp_end":[0.5216,0.1454,0.224],"tcp_start":[0.4833,0.04285,0.14716],"tcp_to_object_dist_end":0.21391,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":590.0,"n_steps_budget":1000.0,"object_pos_end":[0.50973,0.09682,0.01602],"object_pos_start":[0.50973,0.09682,0.01602],"object_to_goal_dist_end":0.20495,"object_to_goal_dist_start":0.20495,"object_z_max":0.01602,"peak_contact_force":273009.67134,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4875.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.55818,0.23801,0.14302],"tcp_start":[0.5216,0.1454,0.224],"tcp_to_object_dist_end":0.19599,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50973,0.09682,0.01602],"object_pos_start":[0.50973,0.09682,0.01602],"object_to_goal_dist_end":0.20495,"object_to_goal_dist_start":0.20495,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1022.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.55225,0.23548,0.16425],"tcp_start":[0.55818,0.23801,0.14302],"tcp_to_object_dist_end":0.20738,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.19658,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19251,"descend_1.grasp_z_offset":0.02429,"lift_up.grasp_force_threshold":0.1155,"lift_up.lift_height":0.13413,"lift_up.lift_speed":0.15081,"place_descend.place_speed":0.29794,"transport_arc.transport_height":0.1307,"transport_arc.transport_speed":0.34627},"optimized_scores":{"best_composite_score":0.00933,"best_fitness_score":0.55933,"best_task_score":0.20458},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3176.0,"contact_point_centroid":[0.50963,0.05164,-0.00229],"force_p95":0.12789,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.49458,"mean_force":0.1371,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54785,0.07408,0.24343]},{"body_a":"world","body_b":"grasp_target","contact_count":142.0,"contact_point_centroid":[0.47429,-0.01904,-0.00118],"force_p95":0.21245,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39375,"mean_force":0.05493,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.46303,-0.01955,0.05336]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5685.0,"contact_point_centroid":[0.4636,-0.00102,0.09901],"force_p95":0.13405,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33499,"mean_force":0.09323,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.46097,-0.01949,0.1018]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6108.0,"contact_point_centroid":[0.46337,-0.0379,0.09657],"force_p95":0.13186,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31177,"mean_force":0.0873,"phase_index":3.0,"phase_name":"lift_up","phase_type":"lift","tcp_position_centroid":[0.461,-0.01949,0.09907]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1105.0,"contact_point_centroid":[0.47411,0.00733,0.17215],"force_p95":0.16964,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23642,"mean_force":0.10801,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46774,-0.01045,0.17637]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":928.0,"contact_point_centroid":[0.47294,-0.0302,0.17143],"force_p95":0.14924,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2208,"mean_force":0.10727,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.46643,-0.01199,0.17535]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47615,-0.02013,-0.00208],"force_p95":0.14589,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17655,"mean_force":0.12857,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46557,-0.01961,0.05252]},{"body_a":"world","body_b":"grasp_target","contact_count":880.0,"contact_point_centroid":[0.47616,-0.02015,-0.00185],"force_p95":0.1371,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12318,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48878,-0.00772,0.26652]},{"body_a":"world","body_b":"grasp_target","contact_count":2160.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47373,-0.01807,0.14453]},{"body_a":"world","body_b":"grasp_target","contact_count":1132.0,"contact_point_centroid":[0.50969,0.05168,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.6149,0.14464,0.24417]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.50969,0.05168,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62062,0.15384,0.19545]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4156.0,"contact_point_centroid":[0.46505,-0.00051,0.05106],"force_p95":0.09113,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09802,"mean_force":0.05385,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46449,-0.01959,0.05141]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4911.0,"contact_point_centroid":[0.46424,-0.03852,0.05132],"force_p95":0.07371,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08136,"mean_force":0.04395,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46449,-0.01959,0.05142]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3201.0,"contact_point_centroid":[0.55137,0.07747,0.2484],"force_p95":0.0111,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01577,"mean_force":0.01051,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55111,0.07747,0.24619]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1207.0,"contact_point_centroid":[0.61534,0.14466,0.24643],"force_p95":0.01095,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0127,"mean_force":0.01045,"phase_index":5.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61491,0.14465,0.24412]},{"body_a":"left_finger","body_b":"right_finger","contact_count":215.0,"contact_point_centroid":[0.62354,0.15464,0.19409],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01104,"mean_force":0.01033,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62308,0.15462,0.19191]}],"total_contact_groups":16},"final_pose_error":0.00982,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.50969,0.05168,0.01602],"final_tcp_position":[0.6247,0.15492,0.19576],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":9748.8555,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":221.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":880.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47766,-0.01646,0.23142],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20544,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":540.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2160.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47208,-0.01976,0.05925],"tcp_start":[0.47766,-0.01646,0.23142],"tcp_to_object_dist_end":0.03348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47606,-0.01964,0.02559],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28836,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14834,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10867.0,"raw_peak_contact_force":0.17655,"subtask_id":"grasp_1","tcp_end":[0.46446,-0.01958,0.05138],"tcp_start":[0.47208,-0.01976,0.05925],"tcp_to_object_dist_end":0.02828,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.46797,-0.01968,0.13604],"object_pos_start":[0.47606,-0.01964,0.02559],"object_to_goal_dist_end":0.24825,"object_to_goal_dist_start":0.28836,"object_z_max":0.13587,"peak_contact_force":0.11438,"phase_name":"lift_up","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11935.0,"raw_peak_contact_force":0.39375,"tcp_end":[0.46105,-0.01948,0.17166],"tcp_start":[0.46446,-0.01958,0.05138],"tcp_to_object_dist_end":0.03628,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50969,0.05168,0.01602],"object_pos_start":[0.46797,-0.01968,0.13604],"object_to_goal_dist_end":0.23802,"object_to_goal_dist_start":0.24825,"object_z_max":0.14207,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8410.0,"raw_peak_contact_force":1.49458,"subtask_id":"transport_arc","tcp_end":[0.6072,0.13563,0.29322],"tcp_start":[0.46105,-0.01948,0.17166],"tcp_to_object_dist_end":0.30561,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":283.0,"n_steps_budget":1000.0,"object_pos_end":[0.50969,0.05168,0.01602],"object_pos_start":[0.50969,0.05168,0.01602],"object_to_goal_dist_end":0.23802,"object_to_goal_dist_start":0.23802,"object_z_max":0.01602,"peak_contact_force":9748.8555,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2339.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.6247,0.15492,0.19576],"tcp_start":[0.6072,0.13563,0.29322],"tcp_to_object_dist_end":0.23705,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50969,0.05168,0.01602],"object_pos_start":[0.50969,0.05168,0.01602],"object_to_goal_dist_end":0.23802,"object_to_goal_dist_start":0.23802,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1015.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61918,0.15338,0.21486],"tcp_start":[0.6247,0.15492,0.19576],"tcp_to_object_dist_end":0.24873,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```