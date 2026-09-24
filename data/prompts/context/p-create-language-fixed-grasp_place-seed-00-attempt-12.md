## Search State

- **Seed**: 0
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1748 | 0.31 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.3365 | 0.57 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1875 | 0.33 | ✅ accepted |
| 9 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | -0.1181 | 0.32 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2618 | 0.32 | ❌ rejected |

**Proposal policy**: task_score is 0.31 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.175) — your mutation base

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

- **Composite score**: 0.175
- **task_score** (E): 0.314
- **fitness_score**: 0.625  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.450

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0879 |
| descend_1 | 1.00 | 1.00 | 0.1696 |
| grasp_1 | 1.00 | 1.00 | 0.0117 |
| lift_vertical | 1.00 | 1.00 | 0.1496 |
| transport | 1.00 | 1.00 | 0.2191 |
| place_approach | 1.00 | 1.00 | 0.0798 |
| release_1 | 1.00 | 1.00 | 0.0213 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, -0.001, 0.220) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.495, -0.001, 0.220)→(0.492, 0.001, 0.051) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.492, 0.001, 0.051)→(0.484, 0.000, 0.042) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 | 1.00 / 45.000 | 0.142 | 0.191 |
| lift_vertical | lift | 1.00 / step_budget | (0.484, 0.000, 0.042)→(0.481, 0.000, 0.192) | (0.497, 0.001, 0.026)→(0.494, 0.001, 0.170) | 0.266→0.214 | 1.00 / 29.000 | 0.096 | 0.488 |
| transport | approach | 1.00 / step_budget | (0.481, 0.000, 0.192)→(0.575, 0.173, 0.273) | (0.494, 0.001, 0.170)→(0.567, 0.157, 0.100) | 0.214→0.136 | 1.00 / 16.333 | 91004.286 | 1.369 |
| place_approach | descend | 1.00 / step_budget | (0.575, 0.173, 0.273)→(0.579, 0.182, 0.194) | (0.567, 0.157, 0.100)→(0.564, 0.160, 0.078) | 0.136→0.116 | 1.00 / 14.333 | 91001.874 | 0.266 |
| release_1 | release | 1.00 / step_budget | (0.579, 0.182, 0.194)→(0.573, 0.180, 0.215) | (0.564, 0.160, 0.078)→(0.563, 0.156, 0.016) | 0.116→0.177 | 1.00 / 3.667 | 0.157 | 0.618 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.417
- phase_score: 0.415
- phase_breakdown.approach_1_score: 0.009
- phase_breakdown.descend_1_score: 0.908
- phase_breakdown.transport_arc_score: 0.169
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.536
- grasp_place_fitness: 0.676

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.676
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.417
- **Median Q (composite search score)**: 0.157
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.386


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4375,"average_solve_count":208.0,"average_success_count":208.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1338,"descend_1.grasp_z_offset":0.01894,"lift_vertical.lift_height":0.25548,"lift_vertical.lift_speed":0.05027,"place_approach.place_speed":0.43148,"transport.transport_speed":0.13512},"optimized_scores":{"best_composite_score":0.14145,"best_fitness_score":0.59145,"best_task_score":0.25284},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":151.0,"contact_point_centroid":[0.53361,0.12411,-0.00926],"force_p95":1.4857,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.60764,"mean_force":0.49886,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54533,0.1468,0.24607]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.51009,-0.02266,-0.00143],"force_p95":0.42061,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44487,"mean_force":0.15202,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.49955,-0.02243,0.0454]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17268.0,"contact_point_centroid":[0.49728,-0.04146,0.15896],"force_p95":0.07489,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27821,"mean_force":0.05097,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.49721,-0.02235,0.15686]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15599.0,"contact_point_centroid":[0.49732,-0.00318,0.1614],"force_p95":0.07843,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2759,"mean_force":0.05541,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.49722,-0.02235,0.15905]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":967.0,"contact_point_centroid":[0.54697,0.12899,0.22472],"force_p95":0.1111,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24772,"mean_force":0.06408,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54824,0.14775,0.22652]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":691.0,"contact_point_centroid":[0.5483,0.16654,0.22451],"force_p95":0.11281,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23454,"mean_force":0.07236,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54839,0.1478,0.22681]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3718.0,"contact_point_centroid":[0.5475,0.16008,0.27491],"force_p95":0.10407,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19818,"mean_force":0.06438,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.54788,0.14127,0.27521]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5137,-0.02294,-0.00205],"force_p95":0.136,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17201,"mean_force":0.12662,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50177,-0.02248,0.04559]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4026.0,"contact_point_centroid":[0.54739,0.12256,0.27269],"force_p95":0.10297,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16942,"mean_force":0.06548,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.54797,0.1416,0.27277]},{"body_a":"world","body_b":"grasp_target","contact_count":1608.0,"contact_point_centroid":[0.5137,-0.02302,-0.00191],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12293,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50334,-0.01,0.23606]},{"body_a":"world","body_b":"grasp_target","contact_count":1472.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50745,-0.02157,0.11219]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8559.0,"contact_point_centroid":[0.52312,0.03826,0.29519],"force_p95":0.07737,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10887,"mean_force":0.05199,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52193,0.05735,0.29384]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8522.0,"contact_point_centroid":[0.52243,0.07635,0.29455],"force_p95":0.07849,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09814,"mean_force":0.0519,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52191,0.05727,0.29382]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5070.0,"contact_point_centroid":[0.50071,-0.00328,0.04746],"force_p95":0.06574,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09574,"mean_force":0.04269,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5006,-0.02245,0.0443]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4902.0,"contact_point_centroid":[0.50118,-0.04172,0.04613],"force_p95":0.0696,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08838,"mean_force":0.04508,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50061,-0.02245,0.04431]}],"total_contact_groups":15},"final_pose_error":0.0099,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.53792,0.13394,0.01714],"final_tcp_position":[0.55007,0.14816,0.23033],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":1.60764,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":403.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1608.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50876,-0.0206,0.1719],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.14599,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":368.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1472.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50869,-0.02264,0.05336],"tcp_start":[0.50876,-0.0206,0.1719],"tcp_to_object_dist_end":0.02779,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51361,-0.0226,0.0258],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26551,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.13465,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11772.0,"raw_peak_contact_force":0.17201,"subtask_id":"grasp_1","tcp_end":[0.50057,-0.02245,0.04427],"tcp_start":[0.50869,-0.02264,0.05336],"tcp_to_object_dist_end":0.0226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":822.0,"n_steps_budget":1000.0,"object_pos_end":[0.50454,-0.02238,0.256],"object_pos_start":[0.51361,-0.0226,0.0258],"object_to_goal_dist_end":0.18412,"object_to_goal_dist_start":0.26551,"object_z_max":0.25573,"peak_contact_force":0.07615,"phase_name":"lift_vertical","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":32951.0,"raw_peak_contact_force":0.44487,"tcp_end":[0.49804,-0.02237,0.28004],"tcp_start":[0.50057,-0.02245,0.04427],"tcp_to_object_dist_end":0.0249,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":453.0,"n_steps_budget":1000.0,"object_pos_end":[0.55154,0.13614,0.28491],"object_pos_start":[0.50454,-0.02238,0.256],"object_to_goal_dist_end":0.06485,"object_to_goal_dist_start":0.18412,"object_z_max":0.28486,"peak_contact_force":0.09418,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17081.0,"raw_peak_contact_force":0.10887,"subtask_id":"transport_arc","tcp_end":[0.54732,0.13618,0.31147],"tcp_start":[0.49804,-0.02237,0.28004],"tcp_to_object_dist_end":0.02689,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":234.0,"n_steps_budget":1000.0,"object_pos_end":[0.54353,0.1475,0.20204],"object_pos_start":[0.55154,0.13614,0.28491],"object_to_goal_dist_end":0.02296,"object_to_goal_dist_start":0.06485,"object_z_max":0.28491,"peak_contact_force":0.11451,"phase_name":"place_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7744.0,"raw_peak_contact_force":0.19818,"tcp_end":[0.55007,0.14816,0.23033],"tcp_start":[0.54732,0.13618,0.31147],"tcp_to_object_dist_end":0.02905,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53792,0.13394,0.01714],"object_pos_start":[0.54353,0.1475,0.20204],"object_to_goal_dist_end":0.20625,"object_to_goal_dist_start":0.02296,"object_z_max":0.20204,"peak_contact_force":0.22498,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1809.0,"raw_peak_contact_force":1.60764,"subtask_id":"release_1","tcp_end":[0.54529,0.1468,0.25229],"tcp_start":[0.55007,0.14816,0.23033],"tcp_to_object_dist_end":0.23561,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01562,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.23514,"descend_1.grasp_z_offset":0.01653,"lift_vertical.lift_height":0.14056,"lift_vertical.lift_speed":0.27187,"place_approach.place_speed":0.3199,"transport.transport_speed":0.23071},"optimized_scores":{"best_composite_score":0.22552,"best_fitness_score":0.67552,"best_task_score":0.41669},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":69.0,"contact_point_centroid":[0.57519,0.24124,-0.00808],"force_p95":1.62679,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.96686,"mean_force":0.82044,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55603,0.22881,0.23326]},{"body_a":"world","body_b":"grasp_target","contact_count":74.0,"contact_point_centroid":[0.49918,0.04336,-0.00149],"force_p95":0.43412,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.51109,"mean_force":0.10973,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.48744,0.04323,0.04393]},{"body_a":"world","body_b":"grasp_target","contact_count":912.0,"contact_point_centroid":[0.57572,0.24068,-0.00275],"force_p95":0.15041,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47688,"mean_force":0.12158,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.55741,0.2357,0.19471]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5785.0,"contact_point_centroid":[0.48739,0.062,0.09513],"force_p95":0.11001,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32118,"mean_force":0.06661,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.48529,0.04303,0.09314]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5394.0,"contact_point_centroid":[0.48777,0.02409,0.09812],"force_p95":0.10822,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31588,"mean_force":0.07009,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.48529,0.04303,0.09569]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4905.0,"contact_point_centroid":[0.5165,0.09432,0.18846],"force_p95":0.14585,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25789,"mean_force":0.0879,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51046,0.11301,0.18768]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5726.0,"contact_point_centroid":[0.51868,0.13696,0.18988],"force_p95":0.11758,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22864,"mean_force":0.07775,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.51259,0.11854,0.18979]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50123,0.04489,-0.00214],"force_p95":0.16113,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22526,"mean_force":0.13304,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48977,0.04345,0.04375]},{"body_a":"world","body_b":"grasp_target","contact_count":764.0,"contact_point_centroid":[0.50118,0.04505,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12327,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4984,0.01709,0.28295]},{"body_a":"world","body_b":"grasp_target","contact_count":2652.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4963,0.03978,0.15788]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57576,0.24075,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5551,0.23893,0.15527]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5045.0,"contact_point_centroid":[0.48847,0.0241,0.04553],"force_p95":0.0697,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11497,"mean_force":0.04297,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48864,0.04335,0.04252]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5520.0,"contact_point_centroid":[0.4883,0.06267,0.04496],"force_p95":0.06995,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0724,"mean_force":0.04085,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48864,0.04335,0.04253]},{"body_a":"left_finger","body_b":"right_finger","contact_count":836.0,"contact_point_centroid":[0.55803,0.23624,0.19137],"force_p95":0.01316,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01645,"mean_force":0.01082,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.55751,0.23621,0.18922]},{"body_a":"left_finger","body_b":"right_finger","contact_count":217.0,"contact_point_centroid":[0.55803,0.2402,0.15304],"force_p95":0.01103,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01104,"mean_force":0.01027,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55767,0.24016,0.15093]}],"total_contact_groups":15},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.57576,0.24075,0.01602],"final_tcp_position":[0.55947,0.24085,0.15446],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.96686,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":192.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":764.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49819,0.03566,0.26679],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.24097,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":663.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2652.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.4966,0.04406,0.05119],"tcp_start":[0.49819,0.03566,0.26679],"tcp_to_object_dist_end":0.02561,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50114,0.04383,0.02551],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24316,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15579,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12365.0,"raw_peak_contact_force":0.22526,"subtask_id":"grasp_1","tcp_end":[0.48861,0.04335,0.04249],"tcp_start":[0.4966,0.04406,0.05119],"tcp_to_object_dist_end":0.02112,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":354.0,"n_steps_budget":600.0,"object_pos_end":[0.50166,0.04349,0.14035],"object_pos_start":[0.50114,0.04383,0.02551],"object_to_goal_dist_end":0.21102,"object_to_goal_dist_start":0.24316,"object_z_max":0.14009,"peak_contact_force":0.10324,"phase_name":"lift_vertical","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":11253.0,"raw_peak_contact_force":0.51109,"tcp_end":[0.48527,0.04303,0.16351],"tcp_start":[0.48861,0.04335,0.04249],"tcp_to_object_dist_end":0.02837,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":553.0,"n_steps_budget":1000.0,"object_pos_end":[0.57665,0.24284,-0.00239],"object_pos_start":[0.50166,0.04349,0.14035],"object_to_goal_dist_end":0.14968,"object_to_goal_dist_start":0.21102,"object_z_max":0.18453,"peak_contact_force":0.51379,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":10700.0,"raw_peak_contact_force":1.96686,"subtask_id":"transport_arc","tcp_end":[0.55697,0.23145,0.23425],"tcp_start":[0.48527,0.04303,0.16351],"tcp_to_object_dist_end":0.23773,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":228.0,"n_steps_budget":1000.0,"object_pos_end":[0.57576,0.24075,0.01602],"object_pos_start":[0.57665,0.24284,-0.00239],"object_to_goal_dist_end":0.13131,"object_to_goal_dist_start":0.14968,"object_z_max":0.01667,"peak_contact_force":0.12263,"phase_name":"place_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1748.0,"raw_peak_contact_force":0.47688,"tcp_end":[0.55947,0.24085,0.15446],"tcp_start":[0.55697,0.23145,0.23425],"tcp_to_object_dist_end":0.1394,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57576,0.24075,0.01602],"object_pos_start":[0.57576,0.24075,0.01602],"object_to_goal_dist_end":0.13131,"object_to_goal_dist_start":0.13131,"object_z_max":0.01602,"peak_contact_force":0.12262,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.55356,0.23818,0.17521],"tcp_start":[0.55947,0.24085,0.15446],"tcp_to_object_dist_end":0.16075,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.17797,"average_solve_count":118.0,"average_success_count":118.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18287,"descend_1.grasp_z_offset":0.01278,"lift_vertical.lift_height":0.11125,"lift_vertical.lift_speed":0.41441,"place_approach.place_speed":0.29006,"transport.transport_speed":0.33304},"optimized_scores":{"best_composite_score":0.1574,"best_fitness_score":0.6074,"best_task_score":0.27269},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1149.0,"contact_point_centroid":[0.57428,0.09247,-0.00287],"force_p95":0.44063,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.03184,"mean_force":0.16397,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.58931,0.11702,0.24566]},{"body_a":"world","body_b":"grasp_target","contact_count":73.0,"contact_point_centroid":[0.47367,-0.01963,-0.00134],"force_p95":0.49186,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.50751,"mean_force":0.12458,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.46308,-0.01959,0.04134]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3666.0,"contact_point_centroid":[0.50283,0.03926,0.1641],"force_p95":0.12521,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.41969,"mean_force":0.08385,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.49702,0.0209,0.16328]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3091.0,"contact_point_centroid":[0.49931,-0.00134,0.16167],"force_p95":0.16408,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33924,"mean_force":0.09671,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.49368,0.0173,0.16032]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4608.0,"contact_point_centroid":[0.46241,-0.00044,0.08324],"force_p95":0.10685,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30269,"mean_force":0.06426,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.46102,-0.01953,0.08072]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5005.0,"contact_point_centroid":[0.46251,-0.03853,0.08228],"force_p95":0.1014,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29112,"mean_force":0.06051,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.46101,-0.01953,0.08049]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02007,-0.00204],"force_p95":0.13613,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17647,"mean_force":0.1263,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46537,-0.01964,0.04113]},{"body_a":"world","body_b":"grasp_target","contact_count":968.0,"contact_point_centroid":[0.47616,-0.02015,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12313,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48847,-0.0079,0.26191]},{"body_a":"world","body_b":"grasp_target","contact_count":2196.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47338,-0.01823,0.13409]},{"body_a":"world","body_b":"grasp_target","contact_count":824.0,"contact_point_centroid":[0.57421,0.09253,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.62334,0.15347,0.23707]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.57421,0.09253,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62214,0.15544,0.19758]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4836.0,"contact_point_centroid":[0.4643,-0.0004,0.0424],"force_p95":0.0676,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09783,"mean_force":0.04488,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46427,-0.01961,0.04003]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5149.0,"contact_point_centroid":[0.46416,-0.03883,0.04193],"force_p95":0.06631,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08399,"mean_force":0.04292,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46427,-0.01961,0.04003]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1002.0,"contact_point_centroid":[0.59569,0.12333,0.25339],"force_p95":0.01256,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01647,"mean_force":0.01073,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.59545,0.12333,0.25111]},{"body_a":"left_finger","body_b":"right_finger","contact_count":894.0,"contact_point_centroid":[0.62377,0.15347,0.23957],"force_p95":0.01089,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01262,"mean_force":0.01029,"phase_index":5.0,"phase_name":"place_approach","phase_type":"descend","tcp_position_centroid":[0.62333,0.15346,0.23724]},{"body_a":"left_finger","body_b":"right_finger","contact_count":226.0,"contact_point_centroid":[0.62485,0.1562,0.19642],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01093,"mean_force":0.00992,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62456,0.15619,0.19404]}],"total_contact_groups":16},"final_pose_error":0.00991,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.57421,0.09253,0.01602],"final_tcp_position":[0.62624,0.15659,0.19805],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273012.2492,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":243.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":968.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47716,-0.01677,0.22212],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19613,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":549.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2196.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47198,-0.01979,0.04784],"tcp_start":[0.47716,-0.01677,0.22212],"tcp_to_object_dist_end":0.02222,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47607,-0.01971,0.02583],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28827,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13449,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11785.0,"raw_peak_contact_force":0.17647,"subtask_id":"grasp_1","tcp_end":[0.46424,-0.01961,0.04],"tcp_start":[0.47198,-0.01979,0.04784],"tcp_to_object_dist_end":0.01846,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":274.0,"n_steps_budget":600.0,"object_pos_end":[0.47704,-0.01941,0.11358],"object_pos_start":[0.47607,-0.01971,0.02583],"object_to_goal_dist_end":0.24814,"object_to_goal_dist_start":0.28827,"object_z_max":0.1133,"peak_contact_force":0.10737,"phase_name":"lift_vertical","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9686.0,"raw_peak_contact_force":0.50751,"tcp_end":[0.46071,-0.0195,0.13184],"tcp_start":[0.46424,-0.01961,0.04],"tcp_to_object_dist_end":0.0245,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":683.0,"n_steps_budget":1000.0,"object_pos_end":[0.57421,0.09253,0.01602],"object_pos_start":[0.47704,-0.01941,0.11358],"object_to_goal_dist_end":0.19491,"object_to_goal_dist_start":0.24814,"object_z_max":0.16782,"peak_contact_force":273012.2492,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8908.0,"raw_peak_contact_force":2.03184,"subtask_id":"transport_arc","tcp_end":[0.62199,0.15095,0.27459],"tcp_start":[0.46071,-0.0195,0.13184],"tcp_to_object_dist_end":0.26935,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":206.0,"n_steps_budget":1000.0,"object_pos_end":[0.57421,0.09253,0.01602],"object_pos_start":[0.57421,0.09253,0.01602],"object_to_goal_dist_end":0.19491,"object_to_goal_dist_start":0.19491,"object_z_max":0.01602,"peak_contact_force":273005.38591,"phase_name":"place_approach","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1718.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62624,0.15659,0.19805],"tcp_start":[0.62199,0.15095,0.27459],"tcp_to_object_dist_end":0.19986,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57421,0.09253,0.01602],"object_pos_start":[0.57421,0.09253,0.01602],"object_to_goal_dist_end":0.19491,"object_to_goal_dist_start":0.19491,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1026.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.62073,0.15498,0.21697],"tcp_start":[0.62624,0.15659,0.19805],"tcp_to_object_dist_end":0.21551,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```