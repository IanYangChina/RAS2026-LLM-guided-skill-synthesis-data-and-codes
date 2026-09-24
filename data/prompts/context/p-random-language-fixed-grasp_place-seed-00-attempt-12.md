## Search State

- **Seed**: 0
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 15 | -0.2227 | 0.34 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 11 | 0.3383 | 1.00 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 11 | 0.3383 | 1.00 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 14 | -0.1990 | 0.35 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 10 | 0.3306 | 0.89 | ❌ rejected |

**Proposal policy**: task_score is 0.34 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.223) — your mutation base

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
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
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
    offset:
    - 0.0
    - 0.0
    - 0.02
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_z_offset:
      type: scalar
      range:
      - 0.0
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
  subtask_id: grasp_1
- id: lift_1
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
    - 0.15
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
- id: transport_to_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.03
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    transport_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    transport_x_offset:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    transport_y_offset:
      type: scalar
      range:
      - -0.05
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: replace
    transport_z_offset:
      type: scalar
      range:
      - -0.02
      - 0.08
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: transport_arc

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15]
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02]
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15]
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03]
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - transport_x_offset: status=consumed; consumers=target.offset.x (replace)
    - transport_y_offset: status=consumed; consumers=target.offset.y (replace)
    - transport_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: -0.223
- **task_score** (E): 0.342
- **fitness_score**: 0.647  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.870

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0510 |
| descend_1 | 1.00 | 1.00 | 0.2140 |
| grasp_1 | 1.00 | 1.00 | 0.0125 |
| lift_1 | 1.00 | 1.00 | 0.1387 |
| transport_to_goal | 1.00 | 1.00 | 0.2051 |
| release_1 | 1.00 | 1.00 | 0.0222 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.498, -0.000, 0.253) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.125 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.498, -0.000, 0.253)→(0.492, 0.000, 0.040) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 11.263 | 0.125 |
| grasp_1 | grasp | 1.00 / step_budget | (0.492, 0.000, 0.040)→(0.484, 0.000, 0.030) | (0.497, 0.001, 0.026)→(0.497, 0.000, 0.025) | 0.265→0.266 | 1.00 / 42.333 | 0.162 | 0.224 |
| lift_1 | lift | 1.00 / step_budget | (0.484, 0.000, 0.030)→(0.480, 0.000, 0.169) | (0.497, 0.000, 0.025)→(0.493, 0.000, 0.162) | 0.266→0.217 | 1.00 / 38.000 | 0.081 | 0.652 |
| transport_to_goal | approach | 1.00 / step_budget | (0.480, 0.000, 0.169)→(0.583, 0.170, 0.185) | (0.493, 0.000, 0.162)→(0.587, 0.173, 0.172) | 0.217→0.028 | 1.00 / 40.333 | 0.072 | 0.135 |
| release_1 | release | 1.00 / step_budget | (0.583, 0.170, 0.185)→(0.578, 0.169, 0.206) | (0.587, 0.173, 0.172)→(0.574, 0.168, 0.024) | 0.028→0.164 | 1.00 / 3.667 | 0.147 | 1.528 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.434
- phase_score: 0.570
- phase_breakdown.release_1_score: 0.370
- phase_breakdown.approach_1_score: 0.010
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.504
- phase_breakdown.descend_1_score: 0.864
- grasp_place_fitness: 0.690

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.690
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.434
- **Median Q (composite search score)**: -0.227
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.338


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53371,"average_solve_count":178.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19034,"approach_1.approach_speed":0.07936,"approach_1.approach_tolerance":0.04075,"descend_1.descend_speed":0.04963,"descend_1.descend_tolerance":0.01401,"descend_1.grasp_z_offset":0.00076,"lift_1.lift_height":0.14316,"lift_1.lift_speed":0.0845,"lift_1.lift_tolerance":0.01651,"release_1.release_tolerance":0.00902,"transport_to_goal.transport_speed":0.16439,"transport_to_goal.transport_tolerance":0.01274,"transport_to_goal.transport_x_offset":0.01062,"transport_to_goal.transport_y_offset":0.00367,"transport_to_goal.transport_z_offset":-0.01482},"optimized_scores":{"best_composite_score":-0.26136,"best_fitness_score":0.60864,"best_task_score":0.26397},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":161.0,"contact_point_centroid":[0.54591,0.14362,-0.00919],"force_p95":1.43209,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.66305,"mean_force":0.47454,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55374,0.14721,0.21316]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.50974,-0.0216,-0.00134],"force_p95":0.54022,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67938,"mean_force":0.13667,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49833,-0.02185,0.03124]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9197.0,"contact_point_centroid":[0.49553,-0.04098,0.09549],"force_p95":0.08119,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33604,"mean_force":0.06016,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4955,-0.02179,0.09273]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11399.0,"contact_point_centroid":[0.4968,-0.00282,0.09324],"force_p95":0.07604,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32532,"mean_force":0.05019,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49549,-0.02179,0.0914]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51374,-0.02299,-0.0021],"force_p95":0.15307,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.215,"mean_force":0.1305,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50076,-0.02189,0.0311]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16286.0,"contact_point_centroid":[0.53155,0.05201,0.17894],"force_p95":0.07893,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15076,"mean_force":0.05321,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52856,0.07092,0.17732]},{"body_a":"world","body_b":"grasp_target","contact_count":224.0,"contact_point_centroid":[0.5137,-0.02302,-0.00142],"force_p95":0.13838,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12483,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5028,-0.00461,0.28255]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16802.0,"contact_point_centroid":[0.52593,0.08615,0.17879],"force_p95":0.07652,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13609,"mean_force":0.0513,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52714,0.06725,0.17635]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5275.0,"contact_point_centroid":[0.50053,-0.00282,0.03175],"force_p95":0.0638,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13359,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49952,-0.02187,0.02977]},{"body_a":"world","body_b":"grasp_target","contact_count":2240.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12508,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50607,-0.0166,0.14647]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1310.0,"contact_point_centroid":[0.55254,0.16675,0.19886],"force_p95":0.06612,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12236,"mean_force":0.03998,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55737,0.14831,0.19562]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1340.0,"contact_point_centroid":[0.5613,0.12934,0.19673],"force_p95":0.06644,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1109,"mean_force":0.03928,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55734,0.1483,0.19556]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4219.0,"contact_point_centroid":[0.49897,-0.04116,0.03268],"force_p95":0.07775,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08184,"mean_force":0.05178,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49953,-0.02187,0.02978]}],"total_contact_groups":13},"final_pose_error":0.01265,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.55056,0.1493,0.02225],"final_tcp_position":[0.55883,0.14843,0.19835],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":1.66305,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":57.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02586],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26573,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12536,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":224.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50628,-0.01115,0.25787],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23243,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":560.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02586],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26573,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2240.0,"raw_peak_contact_force":0.12508,"subtask_id":"descend_1","tcp_end":[0.50833,-0.02199,0.03939],"tcp_start":[0.50628,-0.01115,0.25787],"tcp_to_object_dist_end":0.01445,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51361,-0.02238,0.02564],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26548,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.1512,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11294.0,"raw_peak_contact_force":0.215,"subtask_id":"grasp_1","tcp_end":[0.49949,-0.02187,0.02974],"tcp_start":[0.50833,-0.02199,0.03939],"tcp_to_object_dist_end":0.0147,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":541.0,"n_steps_budget":1000.0,"object_pos_end":[0.50827,-0.02239,0.14829],"object_pos_start":[0.51361,-0.02238,0.02564],"object_to_goal_dist_end":0.19448,"object_to_goal_dist_start":0.26548,"object_z_max":0.14809,"peak_contact_force":0.07954,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":20684.0,"raw_peak_contact_force":0.67938,"tcp_end":[0.49569,-0.02178,0.15684],"tcp_start":[0.49949,-0.02187,0.02974],"tcp_to_object_dist_end":0.01522,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":866.0,"n_steps_budget":1000.0,"object_pos_end":[0.56405,0.1503,0.18397],"object_pos_start":[0.50827,-0.02239,0.14829],"object_to_goal_dist_end":0.03933,"object_to_goal_dist_start":0.19448,"object_z_max":0.18394,"peak_contact_force":0.06648,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33088.0,"raw_peak_contact_force":0.15076,"subtask_id":"transport_arc","tcp_end":[0.55883,0.14843,0.19835],"tcp_start":[0.49569,-0.02178,0.15684],"tcp_to_object_dist_end":0.01542,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55056,0.1493,0.02225],"object_pos_start":[0.56405,0.1503,0.18397],"object_to_goal_dist_end":0.19979,"object_to_goal_dist_start":0.03933,"object_z_max":0.18397,"peak_contact_force":0.24964,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2811.0,"raw_peak_contact_force":1.66305,"subtask_id":"release_1","tcp_end":[0.55369,0.1472,0.22084],"tcp_start":[0.55883,0.14843,0.19835],"tcp_to_object_dist_end":0.19863,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39921,"average_solve_count":253.0,"average_success_count":253.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18333,"approach_1.approach_speed":0.07443,"approach_1.approach_tolerance":0.0504,"descend_1.descend_speed":0.04193,"descend_1.descend_tolerance":0.01538,"descend_1.grasp_z_offset":0.00502,"lift_1.lift_height":0.17778,"lift_1.lift_speed":0.06366,"lift_1.lift_tolerance":0.02442,"release_1.release_tolerance":0.01957,"transport_to_goal.transport_speed":0.07434,"transport_to_goal.transport_tolerance":0.01627,"transport_to_goal.transport_x_offset":0.01263,"transport_to_goal.transport_y_offset":-0.01777,"transport_to_goal.transport_z_offset":0.02339},"optimized_scores":{"best_composite_score":-0.1801,"best_fitness_score":0.6899,"best_task_score":0.43379},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":245.0,"contact_point_centroid":[0.55638,0.21026,-0.00563],"force_p95":1.16514,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.32064,"mean_force":0.29329,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56249,0.2134,0.17533]},{"body_a":"world","body_b":"grasp_target","contact_count":77.0,"contact_point_centroid":[0.49798,0.0416,-0.0017],"force_p95":0.47221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56677,"mean_force":0.18277,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48681,0.04173,0.03701]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6874.0,"contact_point_centroid":[0.48403,0.06073,0.11301],"force_p95":0.08799,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34134,"mean_force":0.06086,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48442,0.04152,0.11052]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1048.0,"contact_point_centroid":[0.56114,0.23317,0.16499],"force_p95":0.07985,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2871,"mean_force":0.05181,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56635,0.21504,0.16045]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8590.0,"contact_point_centroid":[0.48578,0.02256,0.11158],"force_p95":0.08363,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28487,"mean_force":0.04986,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48443,0.04152,0.11018]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50135,0.0449,-0.00229],"force_p95":0.19937,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26577,"mean_force":0.14337,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4891,0.04195,0.03689]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1276.0,"contact_point_centroid":[0.57247,0.19688,0.16025],"force_p95":0.07672,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2274,"mean_force":0.04361,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56633,0.21503,0.16041]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4983.0,"contact_point_centroid":[0.48962,0.0229,0.03699],"force_p95":0.07156,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21036,"mean_force":0.04304,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4879,0.04185,0.0356]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14021.0,"contact_point_centroid":[0.53076,0.11189,0.17504],"force_p95":0.08209,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15061,"mean_force":0.05223,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52602,0.13033,0.17416]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11883.0,"contact_point_centroid":[0.52348,0.14936,0.17771],"force_p95":0.08304,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14148,"mean_force":0.05883,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52614,0.13058,0.17412]},{"body_a":"world","body_b":"grasp_target","contact_count":212.0,"contact_point_centroid":[0.50118,0.04505,-0.00138],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12479,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50032,0.00825,0.28287]},{"body_a":"world","body_b":"grasp_target","contact_count":2036.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12598,"mean_force":0.12264,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49733,0.03163,0.14876]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4122.0,"contact_point_centroid":[0.48824,0.06129,0.03819],"force_p95":0.09273,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0975,"mean_force":0.05425,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48791,0.04185,0.03562]}],"total_contact_groups":13},"final_pose_error":0.01622,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.55919,0.21163,0.02609],"final_tcp_position":[0.56809,0.21525,0.16363],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":33.54434,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":54.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02586],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24196,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12631,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":212.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50058,0.02069,0.25692],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23234,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":509.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02586],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24196,"object_z_max":0.02602,"peak_contact_force":33.54434,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2036.0,"raw_peak_contact_force":0.12598,"subtask_id":"descend_1","tcp_end":[0.49653,0.04254,0.04495],"tcp_start":[0.50058,0.02069,0.25692],"tcp_to_object_dist_end":0.01966,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50131,0.04303,0.02502],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24402,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.19159,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10905.0,"raw_peak_contact_force":0.26577,"subtask_id":"grasp_1","tcp_end":[0.48787,0.04184,0.03557],"tcp_start":[0.49653,0.04254,0.04495],"tcp_to_object_dist_end":0.01714,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":398.0,"n_steps_budget":1000.0,"object_pos_end":[0.49706,0.04264,0.17711],"object_pos_start":[0.50131,0.04303,0.02502],"object_to_goal_dist_end":0.2153,"object_to_goal_dist_start":0.24402,"object_z_max":0.17675,"peak_contact_force":0.08584,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15541.0,"raw_peak_contact_force":0.56677,"tcp_end":[0.48467,0.04155,0.1894],"tcp_start":[0.48787,0.04184,0.03557],"tcp_to_object_dist_end":0.01748,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":699.0,"n_steps_budget":1000.0,"object_pos_end":[0.57811,0.22006,0.1469],"object_pos_start":[0.49706,0.04264,0.17711],"object_to_goal_dist_end":0.02833,"object_to_goal_dist_start":0.2153,"object_z_max":0.17771,"peak_contact_force":0.07874,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":25904.0,"raw_peak_contact_force":0.15061,"subtask_id":"transport_arc","tcp_end":[0.56809,0.21525,0.16363],"tcp_start":[0.48467,0.04155,0.1894],"tcp_to_object_dist_end":0.02008,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55919,0.21163,0.02609],"object_pos_start":[0.57811,0.22006,0.1469],"object_to_goal_dist_end":0.12528,"object_to_goal_dist_start":0.02833,"object_z_max":0.1469,"peak_contact_force":0.10506,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2569.0,"raw_peak_contact_force":1.32064,"subtask_id":"release_1","tcp_end":[0.56241,0.21338,0.18522],"tcp_start":[0.56809,0.21525,0.16363],"tcp_to_object_dist_end":0.15917,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92262,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17096,"approach_1.approach_speed":0.09405,"approach_1.approach_tolerance":0.04532,"descend_1.descend_speed":0.09141,"descend_1.descend_tolerance":0.00517,"descend_1.grasp_z_offset":0.00025,"lift_1.lift_height":0.16404,"lift_1.lift_speed":0.07518,"lift_1.lift_tolerance":0.02907,"release_1.release_tolerance":0.02217,"transport_to_goal.transport_speed":0.1009,"transport_to_goal.transport_tolerance":0.01713,"transport_to_goal.transport_x_offset":0.00182,"transport_to_goal.transport_y_offset":-0.00311,"transport_to_goal.transport_z_offset":0.01249},"optimized_scores":{"best_composite_score":-0.22652,"best_fitness_score":0.64348,"best_task_score":0.32682},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":213.0,"contact_point_centroid":[0.61532,0.14289,-0.00721],"force_p95":1.03184,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.60142,"mean_force":0.34176,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61704,0.14661,0.2047]},{"body_a":"world","body_b":"grasp_target","contact_count":64.0,"contact_point_centroid":[0.47271,-0.01889,-0.0015],"force_p95":0.57074,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70963,"mean_force":0.28368,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46252,-0.01936,0.02718]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4950.0,"contact_point_centroid":[0.45951,-0.03854,0.09409],"force_p95":0.07901,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30952,"mean_force":0.05907,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4604,-0.01932,0.09144]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5990.0,"contact_point_centroid":[0.46108,-0.00029,0.09248],"force_p95":0.07536,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30814,"mean_force":0.05036,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4604,-0.01932,0.09097]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47618,-0.02012,-0.00206],"force_p95":0.14333,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19192,"mean_force":0.12774,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46483,-0.0194,0.02734]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1216.0,"contact_point_centroid":[0.61678,0.16628,0.19207],"force_p95":0.06931,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15646,"mean_force":0.04275,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62086,0.14771,0.18906]},{"body_a":"world","body_b":"grasp_target","contact_count":256.0,"contact_point_centroid":[0.47616,-0.02015,-0.0015],"force_p95":0.13832,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12476,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49431,-0.00455,0.2759]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1236.0,"contact_point_centroid":[0.62463,0.12877,0.18977],"force_p95":0.07077,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13733,"mean_force":0.04233,"phase_index":5.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62083,0.14771,0.18901]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12337,"mean_force":0.12261,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47764,-0.01529,0.13246]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5143.0,"contact_point_centroid":[0.46456,-0.00029,0.02769],"force_p95":0.06605,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11368,"mean_force":0.04229,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46362,-0.01938,0.02615]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17144.0,"contact_point_centroid":[0.54636,0.04963,0.17743],"force_p95":0.07263,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10346,"mean_force":0.05085,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.54434,0.06869,0.17582]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17988.0,"contact_point_centroid":[0.53958,0.08458,0.17769],"force_p95":0.07054,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09572,"mean_force":0.04815,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5414,0.06568,0.17524]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4434.0,"contact_point_centroid":[0.46311,-0.03865,0.02887],"force_p95":0.07765,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08709,"mean_force":0.04921,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46362,-0.01938,0.02615]},{"body_a":"grasp_target","body_b":"hand","contact_count":40.0,"contact_point_centroid":[0.49027,-0.0394,0.06922],"force_p95":0.01864,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.024,"mean_force":0.01079,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46077,-0.01934,0.03778]}],"total_contact_groups":14},"final_pose_error":0.01698,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.61243,0.14368,0.02406],"final_tcp_position":[0.62239,0.1478,0.1924],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.60142,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":65.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02588],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28846,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12353,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":256.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48682,-0.0107,0.24379],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21837,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02588],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28846,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.12337,"subtask_id":"descend_1","tcp_end":[0.4719,-0.0195,0.03431],"tcp_start":[0.48682,-0.0107,0.24379],"tcp_to_object_dist_end":0.00935,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47604,-0.01969,0.02577],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.2883,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14288,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11377.0,"raw_peak_contact_force":0.19192,"subtask_id":"grasp_1","tcp_end":[0.46359,-0.01937,0.02612],"tcp_start":[0.4719,-0.0195,0.03431],"tcp_to_object_dist_end":0.01246,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":275.0,"n_steps_budget":1000.0,"object_pos_end":[0.47284,-0.01982,0.16034],"object_pos_start":[0.47604,-0.01969,0.02577],"object_to_goal_dist_end":0.24099,"object_to_goal_dist_start":0.2883,"object_z_max":0.15985,"peak_contact_force":0.07683,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11044.0,"raw_peak_contact_force":0.70963,"tcp_end":[0.46051,-0.01931,0.16128],"tcp_start":[0.46359,-0.01937,0.02612],"tcp_to_object_dist_end":0.01237,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":870.0,"n_steps_budget":1000.0,"object_pos_end":[0.61926,0.14744,0.18614],"object_pos_start":[0.47284,-0.01982,0.16034],"object_to_goal_dist_end":0.01735,"object_to_goal_dist_start":0.24099,"object_z_max":0.18613,"peak_contact_force":0.07069,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35132.0,"raw_peak_contact_force":0.10346,"subtask_id":"transport_arc","tcp_end":[0.62239,0.1478,0.1924],"tcp_start":[0.46051,-0.01931,0.16128],"tcp_to_object_dist_end":0.00701,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61243,0.14368,0.02406],"object_pos_start":[0.61926,0.14744,0.18614],"object_to_goal_dist_end":0.16775,"object_to_goal_dist_start":0.01735,"object_z_max":0.18614,"peak_contact_force":0.0867,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2665.0,"raw_peak_contact_force":1.60142,"subtask_id":"release_1","tcp_end":[0.61699,0.1466,0.2128],"tcp_start":[0.62239,0.1478,0.1924],"tcp_to_object_dist_end":0.18881,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```