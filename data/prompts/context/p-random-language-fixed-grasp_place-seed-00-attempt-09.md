## Search State

- **Seed**: 0
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 14 | -0.1990 | 0.35 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 10 | 0.3306 | 0.89 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 11 | 0.3363 | 1.00 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | time_limit | 11 | -0.0188 | 0.35 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 11 | 0.3380 | 1.00 | ✅ accepted |

**Proposal policy**: task_score is 0.35 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.199) — your mutation base

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
    - 0.2
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
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
    - 0.0
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
      - 0.0
      - 0.05
      default: 0.0
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: release_1

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
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.2]
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
    - transport_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - transport_x_offset: status=consumed; consumers=target.offset.x (replace)
    - transport_y_offset: status=consumed; consumers=target.offset.y (replace)
    - transport_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: -0.199
- **task_score** (E): 0.350
- **fitness_score**: 0.651  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.850

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0997 |
| descend_1 | 1.00 | 1.00 | 0.1657 |
| grasp_1 | 1.00 | 1.00 | 0.0124 |
| lift_1 | 0.33 | 1.00 | 0.1229 |
| transport_to_goal | 0.67 | 1.00 | 0.2001 |
| descend_to_goal | 1.00 | 1.00 | 0.0274 |
| release_1 | 1.00 | 1.00 | 0.0220 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.000, 0.206) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 3.093 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.494, 0.000, 0.206)→(0.492, 0.001, 0.041) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.492, 0.001, 0.041)→(0.483, 0.000, 0.032) | (0.497, 0.001, 0.026)→(0.497, 0.000, 0.026) | 0.265→0.266 | 1.00 / 42.667 | 0.145 | 0.188 |
| lift_1 | lift | 0.33 / step_budget | (0.483, 0.000, 0.032)→(0.480, 0.000, 0.154) | (0.497, 0.000, 0.026)→(0.489, 0.000, 0.141) | 0.266→0.221 | 1.00 / 37.000 | 0.080 | 0.628 |
| transport_to_goal | approach | 0.67 / step_budget | (0.480, 0.000, 0.154)→(0.577, 0.162, 0.189) | (0.489, 0.000, 0.141)→(0.578, 0.163, 0.170) | 0.221→0.035 | 1.00 / 39.667 | 98.562 | 0.135 |
| descend_to_goal | descend | 1.00 / step_budget | (0.577, 0.162, 0.189)→(0.584, 0.185, 0.185) | (0.578, 0.163, 0.170)→(0.584, 0.186, 0.164) | 0.035→0.023 | 1.00 / 36.333 | 0.080 | 0.195 |
| release_1 | release | 1.00 / step_budget | (0.584, 0.185, 0.185)→(0.579, 0.183, 0.206) | (0.584, 0.186, 0.164)→(0.576, 0.182, 0.025) | 0.023→0.161 | 1.00 / 2.667 | 0.113 | 1.340 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.452
- phase_score: 0.705
- phase_breakdown.release_1_score: 0.490
- phase_breakdown.approach_1_score: 0.024
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.transport_arc_score: 0.731
- phase_breakdown.descend_1_score: 0.783
- grasp_place_fitness: 0.703

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.703
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.452
- **Median Q (composite search score)**: -0.205
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.326


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.82796,"average_solve_count":279.0,"average_success_count":279.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16426,"approach_1.approach_speed":0.05972,"descend_1.descend_speed":0.02609,"descend_1.grasp_z_offset":0.01258,"descend_to_goal.descend_to_goal_speed":0.02589,"descend_to_goal.descend_to_goal_z_offset":-0.01607,"lift_1.lift_height":0.26068,"lift_1.lift_speed":0.07057,"release_1.release_duration":1.40241,"transport_to_goal.transport_speed":0.13795,"transport_to_goal.transport_tolerance":0.00952,"transport_to_goal.transport_x_offset":-0.01283,"transport_to_goal.transport_y_offset":-0.01286,"transport_to_goal.transport_z_offset":0.02738},"optimized_scores":{"best_composite_score":-0.24532,"best_fitness_score":0.60468,"best_task_score":0.26582},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":177.0,"contact_point_centroid":[0.53372,0.14262,-0.00829],"force_p95":1.3659,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.46351,"mean_force":0.41601,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54369,0.14551,0.21356]},{"body_a":"world","body_b":"grasp_target","contact_count":156.0,"contact_point_centroid":[0.50838,-0.02224,-0.00118],"force_p95":0.3532,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53418,"mean_force":0.10501,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49821,-0.02248,0.03888]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20845.0,"contact_point_centroid":[0.49683,-0.00341,0.09549],"force_p95":0.07361,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30795,"mean_force":0.04916,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49554,-0.02242,0.09372]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17834.0,"contact_point_centroid":[0.49561,-0.0416,0.0965],"force_p95":0.07955,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30558,"mean_force":0.05595,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49552,-0.02242,0.09369]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1009.0,"contact_point_centroid":[0.55386,0.12872,0.19487],"force_p95":0.08202,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17815,"mean_force":0.05128,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54719,0.14655,0.19619]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":882.0,"contact_point_centroid":[0.5456,0.16567,0.19681],"force_p95":0.08757,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17756,"mean_force":0.05796,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54719,0.14655,0.19619]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5137,-0.02311,-0.00204],"force_p95":0.13741,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17284,"mean_force":0.12643,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50109,-0.02254,0.03875]},{"body_a":"world","body_b":"grasp_target","contact_count":1364.0,"contact_point_centroid":[0.5137,-0.02302,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50311,-0.00959,0.25142]},{"body_a":"world","body_b":"grasp_target","contact_count":2160.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50701,-0.02129,0.12394]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19015.0,"contact_point_centroid":[0.51035,0.01323,0.18247],"force_p95":0.07612,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11023,"mean_force":0.05085,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50774,0.0322,0.18052]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12468.0,"contact_point_centroid":[0.53259,0.13203,0.20243],"force_p95":0.08423,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10653,"mean_force":0.05751,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.5336,0.11293,0.2006]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5316.0,"contact_point_centroid":[0.50076,-0.00345,0.0393],"force_p95":0.06827,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10561,"mean_force":0.04123,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49985,-0.02251,0.03741]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13859.0,"contact_point_centroid":[0.53954,0.09548,0.20079],"force_p95":0.07767,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10122,"mean_force":0.05281,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.53394,0.11372,0.20055]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19170.0,"contact_point_centroid":[0.50785,0.04961,0.18182],"force_p95":0.07201,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0974,"mean_force":0.05042,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50728,0.03049,0.17956]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4159.0,"contact_point_centroid":[0.49916,-0.04178,0.04023],"force_p95":0.08015,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09008,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49986,-0.02251,0.03741]}],"total_contact_groups":15},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.54024,0.14436,0.02387],"final_tcp_position":[0.54874,0.1468,0.19906],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":295.53806,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":342.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1364.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50851,-0.01999,0.20213],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17621,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":540.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2160.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50839,-0.02267,0.04684],"tcp_start":[0.50851,-0.01999,0.20213],"tcp_to_object_dist_end":0.02149,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51359,-0.023,0.02582],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26575,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.13732,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11275.0,"raw_peak_contact_force":0.17284,"subtask_id":"grasp_1","tcp_end":[0.49982,-0.02251,0.03737],"tcp_start":[0.50839,-0.02267,0.04684],"tcp_to_object_dist_end":0.01798,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50385,-0.02301,0.13508],"object_pos_start":[0.51359,-0.023,0.02582],"object_to_goal_dist_end":0.20146,"object_to_goal_dist_start":0.26575,"object_z_max":0.13498,"peak_contact_force":0.0789,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38835.0,"raw_peak_contact_force":0.53418,"tcp_end":[0.49586,-0.02242,0.15351],"tcp_start":[0.49982,-0.02251,0.03737],"tcp_to_object_dist_end":0.0201,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52616,0.0792,0.18425],"object_pos_start":[0.50385,-0.02301,0.13508],"object_to_goal_dist_end":0.08634,"object_to_goal_dist_start":0.20146,"object_z_max":0.18417,"peak_contact_force":295.53806,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38185.0,"raw_peak_contact_force":0.11023,"subtask_id":"transport_arc","tcp_end":[0.52077,0.07796,0.20729],"tcp_start":[0.49586,-0.02242,0.15351],"tcp_to_object_dist_end":0.0237,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":749.0,"n_steps_budget":1000.0,"object_pos_end":[0.55303,0.14897,0.17258],"object_pos_start":[0.52616,0.0792,0.18425],"object_to_goal_dist_end":0.04949,"object_to_goal_dist_start":0.08634,"object_z_max":0.18426,"peak_contact_force":0.08772,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":26327.0,"raw_peak_contact_force":0.10653,"tcp_end":[0.54874,0.1468,0.19906],"tcp_start":[0.52077,0.07796,0.20729],"tcp_to_object_dist_end":0.02691,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54024,0.14436,0.02387],"object_pos_start":[0.55303,0.14897,0.17258],"object_to_goal_dist_end":0.19874,"object_to_goal_dist_start":0.04949,"object_z_max":0.17258,"peak_contact_force":0.12023,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2068.0,"raw_peak_contact_force":1.46351,"subtask_id":"release_1","tcp_end":[0.54362,0.1455,0.22182],"tcp_start":[0.54874,0.1468,0.19906],"tcp_to_object_dist_end":0.19799,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.74038,"average_solve_count":312.0,"average_success_count":312.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17933,"approach_1.approach_speed":0.01022,"descend_1.descend_speed":0.04299,"descend_1.grasp_z_offset":0.00444,"descend_to_goal.descend_to_goal_speed":0.04308,"descend_to_goal.descend_to_goal_z_offset":0.0188,"lift_1.lift_height":0.15036,"lift_1.lift_speed":0.0943,"release_1.release_duration":1.41438,"transport_to_goal.transport_speed":0.09217,"transport_to_goal.transport_tolerance":0.0138,"transport_to_goal.transport_x_offset":0.0137,"transport_to_goal.transport_y_offset":0.02311,"transport_to_goal.transport_z_offset":0.02357},"optimized_scores":{"best_composite_score":-0.14696,"best_fitness_score":0.70304,"best_task_score":0.4517},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":138.0,"contact_point_centroid":[0.55626,0.24,-0.00902],"force_p95":1.21444,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.26614,"mean_force":0.51455,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5582,0.24172,0.17143]},{"body_a":"world","body_b":"grasp_target","contact_count":152.0,"contact_point_centroid":[0.49793,0.04239,-0.00124],"force_p95":0.40978,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68148,"mean_force":0.09697,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48588,0.04322,0.03178]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15351.0,"contact_point_centroid":[0.48366,0.06221,0.10076],"force_p95":0.08396,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34253,"mean_force":0.05892,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48338,0.043,0.09804]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18746.0,"contact_point_centroid":[0.48552,0.0241,0.09823],"force_p95":0.0798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31738,"mean_force":0.04974,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48337,0.043,0.09669]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":360.0,"contact_point_centroid":[0.55841,0.26209,0.16582],"force_p95":0.09044,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24434,"mean_force":0.05963,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.5645,0.2443,0.16147]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50127,0.04496,-0.00215],"force_p95":0.1651,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22993,"mean_force":0.13384,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48877,0.04349,0.03112]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":420.0,"contact_point_centroid":[0.57121,0.22635,0.16136],"force_p95":0.0733,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2087,"mean_force":0.04948,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.5645,0.2443,0.16147]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5008.0,"contact_point_centroid":[0.48935,0.02439,0.0312],"force_p95":0.07665,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1942,"mean_force":0.04313,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48754,0.04338,0.02983]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19252.0,"contact_point_centroid":[0.53028,0.13015,0.16309],"force_p95":0.08394,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15829,"mean_force":0.05371,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52476,0.14817,0.16316]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15800.0,"contact_point_centroid":[0.52186,0.16581,0.16606],"force_p95":0.09114,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14959,"mean_force":0.06263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52428,0.14702,0.16318]},{"body_a":"world","body_b":"grasp_target","contact_count":1376.0,"contact_point_centroid":[0.50118,0.04505,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49789,0.01834,0.25846]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1102.0,"contact_point_centroid":[0.55593,0.2613,0.16146],"force_p95":0.07635,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12994,"mean_force":0.04511,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56204,0.24344,0.15707]},{"body_a":"world","body_b":"grasp_target","contact_count":2400.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49553,0.0413,0.12663]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1295.0,"contact_point_centroid":[0.56879,0.22546,0.15689],"force_p95":0.06771,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11785,"mean_force":0.04077,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.56203,0.24343,0.15705]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4239.0,"contact_point_centroid":[0.48766,0.0627,0.03248],"force_p95":0.0847,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09594,"mean_force":0.05191,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48754,0.04338,0.02983]}],"total_contact_groups":15},"final_pose_error":0.00532,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.5619,0.24238,0.02762],"final_tcp_position":[0.56373,0.24412,0.16035],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":9.03261,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":345.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":9.03261,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1376.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49773,0.03872,0.216],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19012,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":600.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2400.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49607,0.04414,0.03892],"tcp_start":[0.49773,0.03872,0.216],"tcp_to_object_dist_end":0.0139,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50118,0.04399,0.02548],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24303,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16197,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11047.0,"raw_peak_contact_force":0.22993,"subtask_id":"grasp_1","tcp_end":[0.48751,0.04337,0.0298],"tcp_start":[0.49607,0.04414,0.03892],"tcp_to_object_dist_end":0.01435,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":903.0,"n_steps_budget":990.0,"object_pos_end":[0.49452,0.04398,0.15602],"object_pos_start":[0.50118,0.04399,0.02548],"object_to_goal_dist_end":0.2129,"object_to_goal_dist_start":0.24303,"object_z_max":0.15591,"peak_contact_force":0.0805,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":34249.0,"raw_peak_contact_force":0.68148,"tcp_end":[0.48379,0.04304,0.16848],"tcp_start":[0.48751,0.04337,0.0298],"tcp_to_object_dist_end":0.01647,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56681,0.24676,0.14305],"object_pos_start":[0.49452,0.04398,0.15602],"object_to_goal_dist_end":0.00482,"object_to_goal_dist_start":0.2129,"object_z_max":0.15606,"peak_contact_force":0.07723,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35052.0,"raw_peak_contact_force":0.15829,"subtask_id":"transport_arc","tcp_end":[0.56514,0.24412,0.16244],"tcp_start":[0.48379,0.04304,0.16848],"tcp_to_object_dist_end":0.01964,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":20.0,"n_steps_budget":1000.0,"object_pos_end":[0.56461,0.24644,0.14075],"object_pos_start":[0.56681,0.24676,0.14305],"object_to_goal_dist_end":0.00623,"object_to_goal_dist_start":0.00482,"object_z_max":0.14305,"peak_contact_force":0.07617,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":780.0,"raw_peak_contact_force":0.24434,"tcp_end":[0.56373,0.24412,0.16035],"tcp_start":[0.56514,0.24412,0.16244],"tcp_to_object_dist_end":0.01976,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5619,0.24238,0.02762],"object_pos_start":[0.56461,0.24644,0.14075],"object_to_goal_dist_end":0.11921,"object_to_goal_dist_start":0.00623,"object_z_max":0.14075,"peak_contact_force":0.14382,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2535.0,"raw_peak_contact_force":1.26614,"subtask_id":"release_1","tcp_end":[0.55812,0.24169,0.18173],"tcp_start":[0.56373,0.24412,0.16035],"tcp_to_object_dist_end":0.15416,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16471,"average_solve_count":255.0,"average_success_count":255.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16105,"approach_1.approach_speed":0.04883,"descend_1.descend_speed":0.03781,"descend_1.grasp_z_offset":0.001,"descend_to_goal.descend_to_goal_speed":0.09508,"descend_to_goal.descend_to_goal_z_offset":0.00713,"lift_1.lift_height":0.21278,"lift_1.lift_speed":0.06883,"release_1.release_duration":0.554,"transport_to_goal.transport_speed":0.10447,"transport_to_goal.transport_tolerance":0.01777,"transport_to_goal.transport_x_offset":0.02334,"transport_to_goal.transport_y_offset":0.01296,"transport_to_goal.transport_z_offset":0.01897},"optimized_scores":{"best_composite_score":-0.20479,"best_fitness_score":0.64521,"best_task_score":0.33239},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":224.0,"contact_point_centroid":[0.62611,0.16025,-0.00678],"force_p95":0.99536,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.28948,"mean_force":0.3194,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63482,0.16159,0.20555]},{"body_a":"world","body_b":"grasp_target","contact_count":147.0,"contact_point_centroid":[0.47132,-0.01934,-0.00113],"force_p95":0.46743,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66789,"mean_force":0.11774,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46143,-0.01969,0.02904]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20961.0,"contact_point_centroid":[0.46,-0.00059,0.08521],"force_p95":0.07287,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30474,"mean_force":0.04895,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45874,-0.01963,0.08345]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18590.0,"contact_point_centroid":[0.45876,-0.03881,0.08609],"force_p95":0.07767,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30216,"mean_force":0.05392,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45873,-0.01963,0.08335]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1343.0,"contact_point_centroid":[0.64307,0.14394,0.19219],"force_p95":0.06773,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23613,"mean_force":0.04063,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63858,0.16266,0.19078]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":436.0,"contact_point_centroid":[0.63892,0.1825,0.19966],"force_p95":0.08537,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23543,"mean_force":0.05814,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.64269,0.16396,0.19625]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1120.0,"contact_point_centroid":[0.63531,0.18148,0.19434],"force_p95":0.07532,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23106,"mean_force":0.04676,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.63855,0.16265,0.19071]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":478.0,"contact_point_centroid":[0.64683,0.14511,0.19714],"force_p95":0.0739,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19518,"mean_force":0.05077,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.6426,0.16394,0.19617]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02019,-0.00203],"force_p95":0.13567,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1616,"mean_force":0.12553,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4642,-0.01974,0.02867]},{"body_a":"world","body_b":"grasp_target","contact_count":1316.0,"contact_point_centroid":[0.47616,-0.02015,-0.0019],"force_p95":0.13564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.123,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48761,-0.00826,0.25109]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19160.0,"contact_point_centroid":[0.55416,0.0971,0.17203],"force_p95":0.07741,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13571,"mean_force":0.05091,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.556,0.07822,0.1694]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19618.0,"contact_point_centroid":[0.5568,0.05753,0.1702],"force_p95":0.07387,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13377,"mean_force":0.05049,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55426,0.07652,0.16885]},{"body_a":"world","body_b":"grasp_target","contact_count":2284.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47228,-0.01859,0.11742]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5074.0,"contact_point_centroid":[0.46422,-0.00065,0.02903],"force_p95":0.0687,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10426,"mean_force":0.04304,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.463,-0.01972,0.02749]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4308.0,"contact_point_centroid":[0.46248,-0.03897,0.03012],"force_p95":0.07772,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09478,"mean_force":0.05019,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.463,-0.01972,0.02749]}],"total_contact_groups":15},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62638,0.15967,0.02488],"final_tcp_position":[0.64016,0.16314,0.19442],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.28948,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":330.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1316.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47598,-0.0174,0.20041],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17441,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":571.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2284.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47137,-0.01985,0.03578],"tcp_start":[0.47598,-0.0174,0.20041],"tcp_to_object_dist_end":0.01088,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47602,-0.02003,0.02587],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28847,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.1358,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11182.0,"raw_peak_contact_force":0.1616,"subtask_id":"grasp_1","tcp_end":[0.46297,-0.01972,0.02746],"tcp_start":[0.47137,-0.01985,0.03578],"tcp_to_object_dist_end":0.01315,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46926,-0.02008,0.13188],"object_pos_start":[0.47602,-0.02003,0.02587],"object_to_goal_dist_end":0.24863,"object_to_goal_dist_start":0.28847,"object_z_max":0.1318,"peak_contact_force":0.07994,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39698.0,"raw_peak_contact_force":0.66789,"tcp_end":[0.45902,-0.01963,0.14127],"tcp_start":[0.46297,-0.01972,0.02746],"tcp_to_object_dist_end":0.0139,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":983.0,"n_steps_budget":1000.0,"object_pos_end":[0.64058,0.16421,0.18171],"object_pos_start":[0.46926,-0.02008,0.13188],"object_to_goal_dist_end":0.01335,"object_to_goal_dist_start":0.24863,"object_z_max":0.18167,"peak_contact_force":0.07141,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38778.0,"raw_peak_contact_force":0.13571,"subtask_id":"transport_arc","tcp_end":[0.64395,0.16404,0.19755],"tcp_start":[0.45902,-0.01963,0.14127],"tcp_to_object_dist_end":0.0162,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":23.0,"n_steps_budget":1000.0,"object_pos_end":[0.63429,0.16276,0.17785],"object_pos_start":[0.64058,0.16421,0.18171],"object_to_goal_dist_end":0.013,"object_to_goal_dist_start":0.01335,"object_z_max":0.18171,"peak_contact_force":0.07627,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":914.0,"raw_peak_contact_force":0.23543,"tcp_end":[0.64016,0.16314,0.19442],"tcp_start":[0.64395,0.16404,0.19755],"tcp_to_object_dist_end":0.01758,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62638,0.15967,0.02488],"object_pos_start":[0.63429,0.16276,0.17785],"object_to_goal_dist_end":0.16522,"object_to_goal_dist_start":0.013,"object_z_max":0.17785,"peak_contact_force":0.07622,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2687.0,"raw_peak_contact_force":1.28948,"subtask_id":"release_1","tcp_end":[0.63477,0.16158,0.21402],"tcp_start":[0.64016,0.16314,0.19442],"tcp_to_object_dist_end":0.18934,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```