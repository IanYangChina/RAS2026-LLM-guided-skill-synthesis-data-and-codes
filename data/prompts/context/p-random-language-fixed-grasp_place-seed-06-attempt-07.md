## Search State

- **Seed**: 6
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | time_limit | pose_tolerance | pose_tolerance | time_limit | 10 | -0.4748 | 0.17 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 9 | 0.0512 | 0.29 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 8 | 0.1050 | 0.30 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | -0.0191 | 0.31 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 8 | 0.2021 | 0.49 | ✅ accepted |

**Proposal policy**: task_score is 0.17 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`
- Frozen object start: [0.5038164351471943, -0.015672913018666156, 0.03]
- Frozen task target: [0.5869067239795378, 0.18744967655878825, 0.24811674852797]
- Goal object position: (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5869067239795378, 0.18744967655878825, 0.24811674852797)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5038164351471943, -0.015672913018666156, 0.03)
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
  frozen_object_start: [0.5038, -0.0157, 0.03]
  frozen_task_target: [0.5869, 0.1874, 0.2481]
  frozen_object_starts: {'grasp_target': [0.5038164351471943, -0.015672913018666156, 0.03]}
  frozen_targets: {'place_target': [0.5869067239795378, 0.18744967655878825, 0.24811674852797]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22

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

## Current Skill (Q=-0.475) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
phases:
- id: approach_to_object
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
    - 0.0
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: approach_1
- id: descend_to_grasp
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
    - 0.0
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: descend_1
- id: grasp_object
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    max_time:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: add
  subtask_id: grasp_1
- id: lift_object
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
      distance: 0.2
      axis: world_z
      mode: add_to_offset
      sign: positive
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
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: add
- id: transport_to_goal
  type: approach
  generator: arc_cartesian
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
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.arc_height
        mode: add
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: transport_arc
- id: release_at_goal
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    max_time:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.3
      binds_to:
      - path: duration.max_time
        mode: add
  guards:
  - id: object_still_grasped
    when: before_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (add)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (add)
- **grasp_object** (`grasp`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - max_time: status=consumed; consumers=duration.max_time (add)
- **lift_object** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.2, mode=add_to_offset, sign=positive}
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (add)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (add)
    - speed: status=consumed; consumers=generator.speed (add)
- **release_at_goal** (`release`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - max_time: status=consumed; consumers=duration.max_time (add)
  - guards:
    - id=object_still_grasped, when=before_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]

## Design Metrics

- **Composite score**: -0.475
- **task_score** (E): 0.169
- **fitness_score**: 0.175  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.650

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_object | 0.00 | 1.00 | 0.1516 |
| descend_to_grasp | 0.00 | 1.00 | 0.0562 |
| grasp_object | 1.00 | 1.00 | 0.0017 |
| lift_object | 1.00 | 1.00 | 0.1036 |
| transport_to_goal | 0.33 | 1.00 | 0.1696 |
| descend_to_place | 0.00 | 1.00 | 0.1091 |
| release_at_goal | 1.00 | 1.00 | 0.0272 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.423, 0.008, 0.171) | (0.500, 0.024, 0.030)→(0.482, 0.025, 0.023) | 0.269→0.281 | 1.00 / 5.000 | 198.603 | 1437.654 |
| descend_to_grasp | descend | 0.00 / step_budget | (0.423, 0.008, 0.171)→(0.464, 0.031, 0.173) | (0.482, 0.025, 0.023)→(0.481, 0.025, 0.023) | 0.281→0.281 | 1.00 / 4.667 | 45067.212 | 937.427 |
| grasp_object | grasp | 1.00 / step_budget | (0.464, 0.031, 0.173)→(0.464, 0.032, 0.171) | (0.481, 0.025, 0.023)→(0.481, 0.025, 0.023) | 0.281→0.281 | 1.00 / 9.667 | 67.669 | 307.445 |
| lift_object | lift | 1.00 / time_limit | (0.464, 0.032, 0.171)→(0.462, 0.032, 0.275) | (0.481, 0.025, 0.023)→(0.481, 0.025, 0.023) | 0.281→0.281 | 1.00 / 8.000 | 0.123 | 204.185 |
| transport_to_goal | approach | 0.33 / step_budget | (0.462, 0.032, 0.275)→(0.512, 0.132, 0.217) | (0.481, 0.025, 0.023)→(0.466, 0.046, 0.019) | 0.281→0.278 | 1.00 / 7.333 | 58.211 | 633.646 |
| descend_to_place | descend | 0.00 / step_budget | (0.512, 0.132, 0.217)→(0.572, 0.162, 0.290) | (0.466, 0.046, 0.019)→(0.467, 0.053, 0.016) | 0.278→0.276 | 1.00 / 9.667 | 274.216 | 902.164 |
| release_at_goal | release | 1.00 / step_budget | (0.572, 0.162, 0.290)→(0.572, 0.162, 0.317) | (0.467, 0.053, 0.016)→(0.467, 0.053, 0.016) | 0.276→0.276 | 1.00 / 4.000 | 0.123 | 130.550 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.257
- phase_score: 0.191
- phase_breakdown.transport_arc_score: 0.050
- phase_breakdown.release_1_score: 0.031
- phase_breakdown.approach_1_score: 0.035
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.074
- grasp_place_fitness: 0.222

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.222
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.257
- **Median Q (composite search score)**: -0.496
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.316


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `daf90631fcbaf423e19452d0c9b90b9715013985cc94ef12ca0cd881e96195aa`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `94660347aa4f41f6801e53bd449f8df59691da8bebfa4fef4947a3513fe04781`; realized-scene SHA-256: `584133b5261cffac0dd4282704ff39e97bf4d452e60b02507679bbdea5a4de22`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50382,-0.01567,0.03]},{"name":"goal","value":[0.58691,0.18745,0.24812]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50382,-0.01567,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58691,0.18745,0.24812]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":7.0,"average_failure_rate":0.07071,"average_mean_iterations":21.11111,"average_solve_count":99.0,"average_success_count":92.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.06588,"descend_to_grasp.speed":0.09569,"descend_to_place.place_down_distance":0.11294,"descend_to_place.speed":0.05771,"grasp_object.max_time":0.70976,"lift_object.lift_height":0.1388,"lift_object.speed":0.11583,"release_at_goal.max_time":0.23931,"transport_to_goal.arc_height":0.22373,"transport_to_goal.speed":0.25087},"optimized_scores":{"best_composite_score":-0.49649,"best_fitness_score":0.15351,"best_task_score":0.12439},"replay_outcomes":[{"contacts":{"omitted_contact_groups":7,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":852.0,"contact_point_centroid":[0.64346,-0.00655,-0.00046],"force_p95":215.41486,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1539.66927,"mean_force":202.89321,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.41614,-0.00673,0.14294]},{"body_a":"world","body_b":"link6","contact_count":637.0,"contact_point_centroid":[0.63077,-0.01183,-0.00021],"force_p95":595.05346,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":924.07772,"mean_force":291.91361,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.43599,-0.01578,0.19626]},{"body_a":"world","body_b":"link6","contact_count":914.0,"contact_point_centroid":[0.59704,0.16574,-0.00034],"force_p95":559.56488,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":908.26795,"mean_force":346.84602,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.43609,0.15704,0.22488]},{"body_a":"world","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.5356,-0.00042,-0.0038],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":322.21893,"mean_force":13.42579,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.38413,-0.00347,0.04538]},{"body_a":"world","body_b":"link6","contact_count":438.0,"contact_point_centroid":[0.67542,-0.01993,-0.00012],"force_p95":71.11936,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":245.91195,"mean_force":73.08917,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46457,-0.02222,0.17333]},{"body_a":"world","body_b":"link6","contact_count":112.0,"contact_point_centroid":[0.67146,-0.01929,-0.00021],"force_p95":147.84977,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":208.00208,"mean_force":97.78855,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46401,-0.02243,0.17713]},{"body_a":"world","body_b":"link6","contact_count":81.0,"contact_point_centroid":[0.59829,0.12637,-0.00012],"force_p95":101.33435,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":192.51741,"mean_force":62.12235,"phase_index":6.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.54925,0.15534,0.28868]},{"body_a":"grasp_target","body_b":"link7","contact_count":444.0,"contact_point_centroid":[0.50305,-0.02078,0.04331],"force_p95":1.19078,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.02285,"mean_force":0.42004,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.40315,-0.00463,0.1147]},{"body_a":"grasp_target","body_b":"hand","contact_count":313.0,"contact_point_centroid":[0.49441,-0.03096,0.05428],"force_p95":2.51678,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.66246,"mean_force":0.5787,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.3993,-0.00407,0.10196]},{"body_a":"world","body_b":"grasp_target","contact_count":2891.0,"contact_point_centroid":[0.4936,-0.01684,-0.00264],"force_p95":0.29479,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.40883,"mean_force":0.18436,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.43288,-0.00665,0.15971]},{"body_a":"grasp_target","body_b":"link6","contact_count":240.0,"contact_point_centroid":[0.49732,-0.0037,0.02719],"force_p95":0.71054,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.14829,"mean_force":0.41716,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.39897,0.00159,0.26813]},{"body_a":"world","body_b":"grasp_target","contact_count":3538.0,"contact_point_centroid":[0.47129,0.00846,-0.00262],"force_p95":0.53258,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86644,"mean_force":0.16613,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.41729,0.05819,0.27333]},{"body_a":"world","body_b":"grasp_target","contact_count":2648.0,"contact_point_centroid":[0.4981,-0.01608,-0.00199],"force_p95":0.12343,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13351,"mean_force":0.12266,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.43684,-0.0159,0.19627]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4981,-0.01608,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46457,-0.02223,0.17335]},{"body_a":"world","body_b":"grasp_target","contact_count":2284.0,"contact_point_centroid":[0.4981,-0.01608,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46307,-0.02233,0.22674]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.46763,0.01525,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.43696,0.15821,0.22436]}],"total_contact_groups":23},"final_pose_error":0.16097,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.46763,0.01525,0.01602],"final_tcp_position":[0.54948,0.15519,0.28838],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":1539.66927,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.49811,-0.01607,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31406,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":194.48732,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4524.0,"raw_peak_contact_force":1539.66927,"subtask_id":"approach_1","tcp_end":[0.44689,-0.01226,0.19882],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18027,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":662.0,"n_steps_budget":1000.0,"object_pos_end":[0.4981,-0.01608,0.02602],"object_pos_start":[0.49811,-0.01607,0.02602],"object_to_goal_dist_end":0.31407,"object_to_goal_dist_start":0.31406,"object_z_max":0.02602,"peak_contact_force":392.49134,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3309.0,"raw_peak_contact_force":924.07772,"subtask_id":"descend_1","tcp_end":[0.46467,-0.0227,0.17465],"tcp_start":[0.44689,-0.01226,0.19882],"tcp_to_object_dist_end":0.15249,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4981,-0.01608,0.02602],"object_pos_start":[0.4981,-0.01608,0.02602],"object_to_goal_dist_end":0.31407,"object_to_goal_dist_start":0.31407,"object_z_max":0.02602,"peak_contact_force":67.32734,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2576.0,"raw_peak_contact_force":245.91195,"subtask_id":"grasp_1","tcp_end":[0.46456,-0.02223,0.1732],"tcp_start":[0.46467,-0.0227,0.17465],"tcp_to_object_dist_end":0.15108,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.4981,-0.01608,0.02602],"object_pos_start":[0.4981,-0.01608,0.02602],"object_to_goal_dist_end":0.31407,"object_to_goal_dist_start":0.31407,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4860.0,"raw_peak_contact_force":208.00208,"tcp_end":[0.46364,-0.02233,0.29559],"tcp_start":[0.46456,-0.02223,0.1732],"tcp_to_object_dist_end":0.27184,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46763,0.01525,0.01602],"object_pos_start":[0.4981,-0.01608,0.02602],"object_to_goal_dist_end":0.31265,"object_to_goal_dist_start":0.31407,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8019.0,"raw_peak_contact_force":1.14829,"subtask_id":"transport_arc","tcp_end":[0.44207,0.13891,0.23564],"tcp_start":[0.46364,-0.02233,0.29559],"tcp_to_object_dist_end":0.25333,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46763,0.01525,0.01602],"object_pos_start":[0.46763,0.01525,0.01602],"object_to_goal_dist_end":0.31265,"object_to_goal_dist_start":0.31265,"object_z_max":0.01602,"peak_contact_force":255.01898,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9147.0,"raw_peak_contact_force":908.26795,"tcp_end":[0.54948,0.15519,0.28838],"tcp_start":[0.44207,0.13891,0.23564],"tcp_to_object_dist_end":0.31696,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46763,0.01525,0.01602],"object_pos_start":[0.46763,0.01525,0.01602],"object_to_goal_dist_end":0.31265,"object_to_goal_dist_start":0.31265,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1105.0,"raw_peak_contact_force":192.51741,"subtask_id":"release_1","tcp_end":[0.5494,0.15514,0.31585],"tcp_start":[0.54948,0.15519,0.28838],"tcp_to_object_dist_end":0.34081,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fe7e0be33c0bb4db9d2bbbb069b6113d0e5a69a675a0d70bc1f582243e99e3cf`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.54369,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.03947,"descend_to_grasp.speed":0.05106,"descend_to_place.place_down_distance":0.07486,"descend_to_place.speed":0.04798,"grasp_object.max_time":0.77378,"lift_object.lift_height":0.10925,"lift_object.speed":0.0996,"release_at_goal.max_time":0.15545,"transport_to_goal.arc_height":0.19639,"transport_to_goal.speed":0.15295},"optimized_scores":{"best_composite_score":-0.42835,"best_fitness_score":0.22165,"best_task_score":0.25726},"replay_outcomes":[{"contacts":{"omitted_contact_groups":8,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":687.0,"contact_point_centroid":[0.59003,0.07508,-0.00029],"force_p95":699.8647,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1451.95797,"mean_force":427.33966,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.43237,0.09406,0.22735]},{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.6432,0.01252,-0.00044],"force_p95":208.83799,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1330.93236,"mean_force":203.51256,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.40685,0.01194,0.12942]},{"body_a":"world","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.53514,0.01135,-0.00301],"force_p95":266.03137,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1260.11459,"mean_force":65.54553,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.38368,0.0065,0.04688]},{"body_a":"world","body_b":"link6","contact_count":976.0,"contact_point_centroid":[0.62994,0.0261,-0.00023],"force_p95":484.66885,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":983.76532,"mean_force":284.34764,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.42917,0.02991,0.18892]},{"body_a":"world","body_b":"link6","contact_count":997.0,"contact_point_centroid":[0.61939,0.15873,-0.00032],"force_p95":516.96992,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":636.96622,"mean_force":394.56215,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61903,0.16579,0.29354]},{"body_a":"world","body_b":"link6","contact_count":446.0,"contact_point_centroid":[0.67867,0.04344,-0.00012],"force_p95":71.93003,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":453.24916,"mean_force":69.34479,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46431,0.05128,0.1688]},{"body_a":"world","body_b":"link6","contact_count":143.0,"contact_point_centroid":[0.67517,0.04209,-0.00017],"force_p95":127.42111,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":203.90363,"mean_force":92.1091,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46369,0.05198,0.17212]},{"body_a":"world","body_b":"link6","contact_count":86.0,"contact_point_centroid":[0.64766,0.16289,-0.00012],"force_p95":76.95359,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":130.76664,"mean_force":55.76332,"phase_index":6.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.6276,0.16882,0.2935]},{"body_a":"grasp_target","body_b":"link7","contact_count":675.0,"contact_point_centroid":[0.50196,0.02638,0.04661],"force_p95":0.78977,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.7294,"mean_force":0.30133,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.40299,0.01019,0.11838]},{"body_a":"grasp_target","body_b":"hand","contact_count":402.0,"contact_point_centroid":[0.49607,0.02279,0.05611],"force_p95":1.66838,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.88793,"mean_force":0.39238,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.39804,0.0082,0.10265]},{"body_a":"world","body_b":"grasp_target","contact_count":2569.0,"contact_point_centroid":[0.49819,0.04309,-0.00339],"force_p95":0.37898,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.56047,"mean_force":0.2327,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.42463,0.01151,0.146]},{"body_a":"grasp_target","body_b":"link6","contact_count":414.0,"contact_point_centroid":[0.50249,0.06878,0.05696],"force_p95":0.43885,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.09738,"mean_force":0.15263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.44333,0.08846,0.25059]},{"body_a":"world","body_b":"grasp_target","contact_count":2845.0,"contact_point_centroid":[0.49802,0.04495,-0.00281],"force_p95":0.40749,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6688,"mean_force":0.17912,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.4502,0.10381,0.22565]},{"body_a":"world","body_b":"grasp_target","contact_count":3893.0,"contact_point_centroid":[0.49153,0.09237,-0.00206],"force_p95":0.12499,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57213,"mean_force":0.12718,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61922,0.16587,0.29355]},{"body_a":"grasp_target","body_b":"link7","contact_count":290.0,"contact_point_centroid":[0.5158,0.02762,0.05274],"force_p95":0.32441,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34338,"mean_force":0.19565,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.4011,0.02386,0.15849]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.5039,0.04146,-0.00218],"force_p95":0.21296,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26178,"mean_force":0.13508,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.42987,0.03022,0.18899]}],"total_contact_groups":24},"final_pose_error":0.22298,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.49174,0.09263,0.01602],"final_tcp_position":[0.62755,0.16926,0.29312],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":134400.05046,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50499,0.04074,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21576,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":201.61,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4557.0,"raw_peak_contact_force":1330.93236,"subtask_id":"approach_1","tcp_end":[0.42464,0.02,0.17125],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16727,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50363,0.04159,0.02602],"object_pos_start":[0.50499,0.04074,0.02602],"object_to_goal_dist_end":0.21602,"object_to_goal_dist_start":0.21576,"object_z_max":0.02604,"peak_contact_force":134400.05046,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5266.0,"raw_peak_contact_force":983.76532,"subtask_id":"descend_1","tcp_end":[0.46456,0.05075,0.17065],"tcp_start":[0.42464,0.02,0.17125],"tcp_to_object_dist_end":0.15009,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50363,0.04159,0.02602],"object_pos_start":[0.50363,0.04159,0.02602],"object_to_goal_dist_end":0.21602,"object_to_goal_dist_start":0.21602,"object_z_max":0.02602,"peak_contact_force":67.68724,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2589.0,"raw_peak_contact_force":453.24916,"subtask_id":"grasp_1","tcp_end":[0.46429,0.0513,0.16867],"tcp_start":[0.46456,0.05075,0.17065],"tcp_to_object_dist_end":0.1483,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.50363,0.04159,0.02602],"object_pos_start":[0.50363,0.04159,0.02602],"object_to_goal_dist_end":0.21602,"object_to_goal_dist_start":0.21602,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4908.0,"raw_peak_contact_force":203.90363,"tcp_end":[0.46294,0.05116,0.26297],"tcp_start":[0.46429,0.0513,0.16867],"tcp_to_object_dist_end":0.24061,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":941.0,"n_steps_budget":1000.0,"object_pos_end":[0.48762,0.07224,0.02427],"object_pos_start":[0.50363,0.04159,0.02602],"object_to_goal_dist_end":0.21029,"object_to_goal_dist_start":0.21602,"object_z_max":0.02722,"peak_contact_force":174.38891,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7937.0,"raw_peak_contact_force":1451.95797,"subtask_id":"transport_arc","tcp_end":[0.61011,0.16335,0.29343],"tcp_start":[0.46294,0.05116,0.26297],"tcp_to_object_dist_end":0.30943,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49174,0.09263,0.01602],"object_pos_start":[0.48762,0.07224,0.02427],"object_to_goal_dist_end":0.20365,"object_to_goal_dist_start":0.21029,"object_z_max":0.02427,"peak_contact_force":349.62179,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9165.0,"raw_peak_contact_force":636.96622,"tcp_end":[0.62755,0.16926,0.29312],"tcp_start":[0.61011,0.16335,0.29343],"tcp_to_object_dist_end":0.31797,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49174,0.09263,0.01602],"object_pos_start":[0.49174,0.09263,0.01602],"object_to_goal_dist_end":0.20365,"object_to_goal_dist_start":0.20365,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1106.0,"raw_peak_contact_force":130.76664,"subtask_id":"release_1","tcp_end":[0.62781,0.16888,0.31903],"tcp_start":[0.62755,0.16926,0.29312],"tcp_to_object_dist_end":0.3408,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `28f75809d7d1d0a11ca1a36dd459ad950e5a80b6bae34006f33ac9620425f5e5`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.90099,"average_solve_count":101.0,"average_success_count":101.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.02791,"descend_to_grasp.speed":0.06034,"descend_to_place.place_down_distance":0.06327,"descend_to_place.speed":0.02044,"grasp_object.max_time":0.9637,"lift_object.lift_height":0.10891,"lift_object.speed":0.08973,"release_at_goal.max_time":0.16944,"transport_to_goal.arc_height":0.13859,"transport_to_goal.speed":0.13885},"optimized_scores":{"best_composite_score":-0.49954,"best_fitness_score":0.15046,"best_task_score":0.12543},"replay_outcomes":[{"contacts":{"omitted_contact_groups":11,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.63379,0.0114,-0.00046],"force_p95":201.73377,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1442.3603,"mean_force":204.56549,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.39057,0.0107,0.11889]},{"body_a":"world","body_b":"link5","contact_count":891.0,"contact_point_centroid":[0.48166,0.16588,-0.00031],"force_p95":381.39534,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1161.25694,"mean_force":280.55921,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.50823,0.11811,0.26685]},{"body_a":"world","body_b":"link6","contact_count":341.0,"contact_point_centroid":[0.58199,0.18493,-0.00041],"force_p95":148.29787,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":927.714,"mean_force":115.69623,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.53147,0.14739,0.27239]},{"body_a":"world","body_b":"link6","contact_count":970.0,"contact_point_centroid":[0.62754,0.03126,-0.00021],"force_p95":474.1376,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":904.43765,"mean_force":299.34296,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.42577,0.03229,0.18646]},{"body_a":"world","body_b":"link6","contact_count":203.0,"contact_point_centroid":[0.52583,0.07428,-0.00022],"force_p95":318.17009,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":447.83109,"mean_force":191.37128,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.39666,0.08355,0.25265]},{"body_a":"world","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.59286,-0.01146,-0.00201],"force_p95":295.42916,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":343.94829,"mean_force":143.2522,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.44296,-0.01421,0.05203]},{"body_a":"world","body_b":"link6","contact_count":449.0,"contact_point_centroid":[0.67483,0.06221,-0.00012],"force_p95":71.91867,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":223.17422,"mean_force":69.07788,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46219,0.06656,0.1711]},{"body_a":"world","body_b":"link6","contact_count":120.0,"contact_point_centroid":[0.67209,0.06098,-0.00014],"force_p95":139.46538,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":200.65046,"mean_force":87.29957,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4616,0.06707,0.1736]},{"body_a":"world","body_b":"link5","contact_count":78.0,"contact_point_centroid":[0.46743,0.15867,-0.00013],"force_p95":68.23612,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":68.36497,"mean_force":50.37448,"phase_index":6.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.5384,0.16049,0.28908]},{"body_a":"world","body_b":"link6","contact_count":75.0,"contact_point_centroid":[0.57645,0.19653,-0.0001],"force_p95":31.17114,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":31.22211,"mean_force":22.65698,"phase_index":6.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.5384,0.16048,0.28907]},{"body_a":"grasp_target","body_b":"hand","contact_count":44.0,"contact_point_centroid":[0.45939,0.04063,0.03986],"force_p95":3.85001,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.06111,"mean_force":1.71492,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.38402,0.00633,0.05336]},{"body_a":"grasp_target","body_b":"hand","contact_count":5.0,"contact_point_centroid":[0.47007,0.07158,0.03624],"force_p95":1.61209,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.63953,"mean_force":1.07196,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.44245,-0.01794,0.0493]},{"body_a":"world","body_b":"grasp_target","contact_count":3909.0,"contact_point_centroid":[0.44771,0.04984,-0.00214],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.5989,"mean_force":0.14025,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.40277,0.0101,0.12923]},{"body_a":"grasp_target","body_b":"link7","contact_count":31.0,"contact_point_centroid":[0.4875,0.03032,0.01167],"force_p95":0.78277,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.81942,"mean_force":0.43281,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.37495,0.00629,0.05541]},{"body_a":"world","body_b":"grasp_target","contact_count":3918.0,"contact_point_centroid":[0.44145,0.05146,-0.00201],"force_p95":0.12613,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.80154,"mean_force":0.1254,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.50404,0.11085,0.25682]},{"body_a":"grasp_target","body_b":"link6","contact_count":83.0,"contact_point_centroid":[0.47076,0.07255,0.03558],"force_p95":0.29035,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.53628,"mean_force":0.1115,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.39174,0.09092,0.25842]}],"total_contact_groups":27},"final_pose_error":0.1463,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.44206,0.05158,0.01602],"final_tcp_position":[0.53839,0.16008,0.2888],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1442.3603,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44268,0.04997,0.01602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.31204,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":199.71245,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4893.0,"raw_peak_contact_force":1442.3603,"subtask_id":"approach_1","tcp_end":[0.3973,0.01679,0.14417],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13994,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44268,0.04997,0.01602],"object_pos_start":[0.44268,0.04997,0.01602],"object_to_goal_dist_end":0.31204,"object_to_goal_dist_start":0.31204,"object_z_max":0.01602,"peak_contact_force":409.09278,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4970.0,"raw_peak_contact_force":904.43765,"subtask_id":"descend_1","tcp_end":[0.46237,0.06605,0.17231],"tcp_start":[0.3973,0.01679,0.14417],"tcp_to_object_dist_end":0.15834,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.44268,0.04997,0.01602],"object_pos_start":[0.44268,0.04997,0.01602],"object_to_goal_dist_end":0.31204,"object_to_goal_dist_start":0.31204,"object_z_max":0.01602,"peak_contact_force":67.99129,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2590.0,"raw_peak_contact_force":223.17422,"subtask_id":"grasp_1","tcp_end":[0.46218,0.06658,0.17096],"tcp_start":[0.46237,0.06605,0.17231],"tcp_to_object_dist_end":0.15705,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.44268,0.04997,0.01602],"object_pos_start":[0.44268,0.04997,0.01602],"object_to_goal_dist_end":0.31204,"object_to_goal_dist_start":0.31204,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4827.0,"raw_peak_contact_force":200.65046,"tcp_end":[0.46086,0.0664,0.26496],"tcp_start":[0.46218,0.06658,0.17096],"tcp_to_object_dist_end":0.25015,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44227,0.05045,0.01602],"object_pos_start":[0.44268,0.04997,0.01602],"object_to_goal_dist_end":0.31194,"object_to_goal_dist_start":0.31204,"object_z_max":0.01609,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8512.0,"raw_peak_contact_force":447.83109,"subtask_id":"transport_arc","tcp_end":[0.48319,0.09428,0.12131],"tcp_start":[0.46086,0.0664,0.26496],"tcp_to_object_dist_end":0.12117,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":11.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44206,0.05158,0.01602],"object_pos_start":[0.44227,0.05045,0.01602],"object_to_goal_dist_end":0.3114,"object_to_goal_dist_start":0.31194,"object_z_max":0.02115,"peak_contact_force":218.00832,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9448.0,"raw_peak_contact_force":1161.25694,"tcp_end":[0.53839,0.16008,0.2888],"tcp_start":[0.48319,0.09428,0.12131],"tcp_to_object_dist_end":0.30897,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.44206,0.05158,0.01602],"object_pos_start":[0.44206,0.05158,0.01602],"object_to_goal_dist_end":0.3114,"object_to_goal_dist_start":0.3114,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1175.0,"raw_peak_contact_force":68.36497,"subtask_id":"release_1","tcp_end":[0.5386,0.16063,0.31702],"tcp_start":[0.53839,0.16008,0.2888],"tcp_to_object_dist_end":0.33438,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```