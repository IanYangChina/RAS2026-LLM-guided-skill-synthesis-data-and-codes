## Search State

- **Seed**: 0
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.0590 | 0.19 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 6 | 0.1378 | 0.24 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.0352 | 0.18 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | 0.0204 | 0.22 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2553 | 0.32 | ✅ accepted |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.059) — your mutation base

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

- **Composite score**: 0.059
- **task_score** (E): 0.190
- **fitness_score**: 0.559  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0326 |
| descend_1 | 1.00 | 1.00 | 0.2410 |
| grasp_1 | 1.00 | 1.00 | 0.0117 |
| lift_vertical | 0.33 | 0.33 | 0.0382 |
| transport_to_goal | 0.33 | 1.00 | 0.1662 |
| descend_to_goal | 1.00 | 1.00 | 0.0806 |
| release_1 | 1.00 | 1.00 | 0.0216 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.001, 0.295) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.494, 0.001, 0.295)→(0.492, 0.001, 0.054) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.492, 0.001, 0.054)→(0.485, 0.000, 0.045) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 | 1.00 / 43.333 | 0.148 | 0.191 |
| lift_vertical | lift | 0.33 / guard_failure | (0.487, 0.000, 0.122)→(0.489, 0.000, 0.160) | (0.497, 0.001, 0.026)→(0.505, 0.002, 0.130) | 0.266→0.214 | 0.33 / 6.667 | 0.045 | 0.450 |
| transport_to_goal | approach | 0.33 / step_budget | (0.489, 0.000, 0.160)→(0.545, 0.130, 0.240) | (0.506, 0.002, 0.129)→(0.523, 0.020, 0.016) | 0.213→0.250 | 1.00 / 8.667 | 0.123 | 1.509 |
| descend_to_goal | descend | 1.00 / step_budget | (0.545, 0.130, 0.240)→(0.577, 0.178, 0.206) | (0.523, 0.020, 0.016)→(0.523, 0.020, 0.016) | 0.250→0.250 | 1.00 / 8.667 | 94252.281 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.577, 0.178, 0.206)→(0.572, 0.176, 0.226) | (0.523, 0.020, 0.016)→(0.523, 0.020, 0.016) | 0.250→0.250 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.221
- phase_score: 0.377
- phase_breakdown.approach_1_score: 0.007
- phase_breakdown.descend_1_score: 0.831
- phase_breakdown.transport_arc_score: 0.180
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.294
- grasp_place_fitness: 0.569

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.569
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.221
- **Median Q (composite search score)**: 0.056
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.394


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86719,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.26059,"descend_1.grasp_z_offset":0.02381,"descend_to_goal.place_speed":0.42058,"descend_to_goal.place_z_offset":-0.01874,"lift_vertical.lift_height":0.15235,"lift_vertical.lift_speed":0.15462,"transport_to_goal.transport_speed":0.20357},"optimized_scores":{"best_composite_score":0.05135,"best_fitness_score":0.55135,"best_task_score":0.18489},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2803.0,"contact_point_centroid":[0.53168,0.00732,-0.00239],"force_p95":0.18894,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.59141,"mean_force":0.14525,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52717,0.05964,0.23217]},{"body_a":"world","body_b":"grasp_target","contact_count":152.0,"contact_point_centroid":[0.51234,-0.0223,-0.00117],"force_p95":0.219,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37758,"mean_force":0.05119,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.49952,-0.02226,0.05113]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7597.0,"contact_point_centroid":[0.50434,-0.00349,0.09384],"force_p95":0.1306,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29421,"mean_force":0.07301,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.5019,-0.02227,0.09419]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7955.0,"contact_point_centroid":[0.50419,-0.04097,0.09325],"force_p95":0.12808,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28002,"mean_force":0.07103,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.50186,-0.02227,0.09359]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1448.0,"contact_point_centroid":[0.51585,0.00981,0.1687],"force_p95":0.13882,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23215,"mean_force":0.10621,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50996,-0.00817,0.1721]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1497.0,"contact_point_centroid":[0.51538,-0.02837,0.16758],"force_p95":0.17738,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19795,"mean_force":0.10452,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50967,-0.01037,0.17057]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51371,-0.02297,-0.00206],"force_p95":0.14132,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18314,"mean_force":0.12755,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50196,-0.02232,0.05075]},{"body_a":"world","body_b":"grasp_target","contact_count":432.0,"contact_point_centroid":[0.5137,-0.02302,-0.00171],"force_p95":0.13814,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12378,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50298,-0.00758,0.29407]},{"body_a":"world","body_b":"grasp_target","contact_count":2796.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50695,-0.01915,0.17232]},{"body_a":"world","body_b":"grasp_target","contact_count":1092.0,"contact_point_centroid":[0.53145,0.00615,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.54279,0.12239,0.23723]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53145,0.00615,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54479,0.14299,0.20782]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4352.0,"contact_point_centroid":[0.50128,-0.00311,0.05018],"force_p95":0.07326,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11615,"mean_force":0.04949,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50081,-0.02229,0.04947]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4909.0,"contact_point_centroid":[0.50124,-0.04143,0.05009],"force_p95":0.06965,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.083,"mean_force":0.04451,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50082,-0.02229,0.04947]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2916.0,"contact_point_centroid":[0.52786,0.06108,0.23576],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01611,"mean_force":0.0105,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52756,0.06108,0.23347]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1183.0,"contact_point_centroid":[0.54312,0.1223,0.23954],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01269,"mean_force":0.01031,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.54278,0.12229,0.2374]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.54776,0.14376,0.20531],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01263,"mean_force":0.01009,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54709,0.14374,0.20298]}],"total_contact_groups":16},"final_pose_error":0.00991,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.53145,0.00615,0.01602],"final_tcp_position":[0.5486,0.14382,0.20582],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":9748.97695,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":109.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12239,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":432.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50708,-0.01588,0.28849],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.26265,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":699.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2796.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.50888,-0.02248,0.05856],"tcp_start":[0.50708,-0.01588,0.28849],"tcp_to_object_dist_end":0.0329,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51363,-0.02251,0.02576],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26548,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.14004,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11061.0,"raw_peak_contact_force":0.18314,"subtask_id":"grasp_1","tcp_end":[0.50079,-0.02229,0.04943],"tcp_start":[0.50888,-0.02248,0.05856],"tcp_to_object_dist_end":0.02693,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":20.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.51737,-0.02238,0.13059],"object_pos_start":[0.51363,-0.02251,0.02576],"object_to_goal_dist_end":0.19998,"object_to_goal_dist_start":0.26548,"object_z_max":0.13043,"peak_contact_force":0.13636,"phase_name":"lift_vertical","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15704.0,"raw_peak_contact_force":0.37758,"tcp_end":[0.50902,-0.02239,0.16332],"tcp_start":[0.50079,-0.02229,0.04943],"tcp_to_object_dist_end":0.03379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53145,0.00615,0.01602],"object_pos_start":[0.51737,-0.02238,0.13059],"object_to_goal_dist_end":0.2532,"object_to_goal_dist_start":0.19998,"object_z_max":0.14479,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8664.0,"raw_peak_contact_force":1.59141,"subtask_id":"transport_arc","tcp_end":[0.53878,0.10236,0.27096],"tcp_start":[0.50902,-0.02239,0.16332],"tcp_to_object_dist_end":0.2726,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":273.0,"n_steps_budget":1000.0,"object_pos_end":[0.53145,0.00615,0.01602],"object_pos_start":[0.53145,0.00615,0.01602],"object_to_goal_dist_end":0.2532,"object_to_goal_dist_start":0.2532,"object_z_max":0.01602,"peak_contact_force":9748.97695,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2275.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.5486,0.14382,0.20582],"tcp_start":[0.53878,0.10236,0.27096],"tcp_to_object_dist_end":0.2351,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53145,0.00615,0.01602],"object_pos_start":[0.53145,0.00615,0.01602],"object_to_goal_dist_end":0.2532,"object_to_goal_dist_start":0.2532,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.54345,0.14257,0.22814],"tcp_start":[0.5486,0.14382,0.20582],"tcp_to_object_dist_end":0.25249,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79032,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.24812,"descend_1.grasp_z_offset":0.02336,"descend_to_goal.place_speed":0.3522,"descend_to_goal.place_z_offset":0.03484,"lift_vertical.lift_height":0.20152,"lift_vertical.lift_speed":0.33197,"transport_to_goal.transport_speed":0.29569},"optimized_scores":{"best_composite_score":0.06941,"best_fitness_score":0.56941,"best_task_score":0.22116},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3746.0,"contact_point_centroid":[0.52398,0.06457,-0.00219],"force_p95":0.12703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.33984,"mean_force":0.13383,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52343,0.13879,0.18947]},{"body_a":"world","body_b":"grasp_target","contact_count":109.0,"contact_point_centroid":[0.49952,0.04144,-0.00131],"force_p95":0.24574,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39404,"mean_force":0.03633,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.48763,0.04325,0.05142]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4405.0,"contact_point_centroid":[0.49082,0.02427,0.08525],"force_p95":0.15133,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36397,"mean_force":0.07816,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.4881,0.04315,0.0856]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5177.0,"contact_point_centroid":[0.49139,0.06156,0.08911],"force_p95":0.11788,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27715,"mean_force":0.06982,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.48836,0.04316,0.08887]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50126,0.045,-0.00215],"force_p95":0.16904,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21669,"mean_force":0.1339,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48989,0.04348,0.05053]},{"body_a":"world","body_b":"grasp_target","contact_count":748.0,"contact_point_centroid":[0.50118,0.04505,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12328,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49839,0.01738,0.28777]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4183.0,"contact_point_centroid":[0.48902,0.02416,0.05011],"force_p95":0.09027,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13055,"mean_force":0.05467,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48876,0.04338,0.0493]},{"body_a":"world","body_b":"grasp_target","contact_count":2688.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49638,0.03981,0.16644]},{"body_a":"world","body_b":"grasp_target","contact_count":648.0,"contact_point_centroid":[0.52406,0.06459,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.55538,0.22916,0.20658]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.52406,0.06459,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55466,0.23623,0.18627]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5078.0,"contact_point_centroid":[0.48891,0.0624,0.05005],"force_p95":0.07274,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07552,"mean_force":0.04276,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48877,0.04338,0.04931]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3690.0,"contact_point_centroid":[0.52605,0.14481,0.19455],"force_p95":0.01105,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01616,"mean_force":0.01057,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52558,0.14479,0.19227]},{"body_a":"left_finger","body_b":"right_finger","contact_count":700.0,"contact_point_centroid":[0.55603,0.22915,0.20908],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01259,"mean_force":0.01032,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.55537,0.22911,0.20671]},{"body_a":"left_finger","body_b":"right_finger","contact_count":220.0,"contact_point_centroid":[0.55722,0.23745,0.1843],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01101,"mean_force":0.01012,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55703,0.23741,0.18205]}],"total_contact_groups":14},"final_pose_error":0.00983,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.52406,0.06459,0.01602],"final_tcp_position":[0.55858,0.23786,0.18529],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.33984,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":188.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":748.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49822,0.03572,0.27708],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25125,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":672.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2688.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49665,0.04408,0.05799],"tcp_start":[0.49822,0.03572,0.27708],"tcp_to_object_dist_end":0.0323,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50121,0.04385,0.02534],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.2432,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.17128,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11061.0,"raw_peak_contact_force":0.21669,"subtask_id":"grasp_1","tcp_end":[0.48874,0.04337,0.04927],"tcp_start":[0.49665,0.04408,0.05799],"tcp_to_object_dist_end":0.02699,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":348.0,"n_steps_budget":600.0,"object_pos_end":[0.50799,0.04773,0.11217],"object_pos_start":[0.50121,0.04385,0.02534],"object_to_goal_dist_end":0.20795,"object_to_goal_dist_start":0.2432,"object_z_max":0.11235,"peak_contact_force":0.0,"phase_name":"lift_vertical","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9691.0,"raw_peak_contact_force":0.39404,"tcp_end":[0.49229,0.04331,0.14891],"tcp_start":[0.49228,0.0433,0.14881],"tcp_to_object_dist_end":0.0402,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52406,0.06459,0.01602],"object_pos_start":[0.50878,0.04859,0.11069],"object_to_goal_dist_end":0.22633,"object_to_goal_dist_start":0.20718,"object_z_max":0.11069,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7436.0,"raw_peak_contact_force":1.33984,"subtask_id":"transport_arc","tcp_end":[0.5537,0.22156,0.22863],"tcp_start":[0.49229,0.04331,0.14891],"tcp_to_object_dist_end":0.26593,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":162.0,"n_steps_budget":1000.0,"object_pos_end":[0.52406,0.06459,0.01602],"object_pos_start":[0.52406,0.06459,0.01602],"object_to_goal_dist_end":0.22633,"object_to_goal_dist_start":0.22633,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1348.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.55858,0.23786,0.18529],"tcp_start":[0.5537,0.22156,0.22863],"tcp_to_object_dist_end":0.24468,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.52406,0.06459,0.01602],"object_pos_start":[0.52406,0.06459,0.01602],"object_to_goal_dist_end":0.22633,"object_to_goal_dist_start":0.22633,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1020.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.55327,0.23554,0.20618],"tcp_start":[0.55858,0.23786,0.18529],"tcp_to_object_dist_end":0.25736,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90299,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.29811,"descend_1.grasp_z_offset":0.01003,"descend_to_goal.place_speed":0.15979,"descend_to_goal.place_z_offset":0.04481,"lift_vertical.lift_height":0.29858,"lift_vertical.lift_speed":0.44878,"transport_to_goal.transport_speed":0.14441},"optimized_scores":{"best_composite_score":0.0563,"best_fitness_score":0.5563,"best_task_score":0.16463},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3710.0,"contact_point_centroid":[0.51192,-0.01022,-0.00224],"force_p95":0.12492,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.59724,"mean_force":0.13456,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50839,0.02931,0.19577]},{"body_a":"world","body_b":"grasp_target","contact_count":125.0,"contact_point_centroid":[0.47418,-0.01944,-0.0011],"force_p95":0.37474,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57938,"mean_force":0.05989,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.46296,-0.01969,0.03918]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4449.0,"contact_point_centroid":[0.46571,-0.00068,0.08669],"force_p95":0.12783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35016,"mean_force":0.07308,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.46313,-0.01964,0.08435]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4774.0,"contact_point_centroid":[0.46566,-0.03854,0.0849],"force_p95":0.12601,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.305,"mean_force":0.06914,"phase_index":3.0,"phase_name":"lift_vertical","phase_type":"lift","tcp_position_centroid":[0.46306,-0.01964,0.08317]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02007,-0.00204],"force_p95":0.13442,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17191,"mean_force":0.12585,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46531,-0.01975,0.0384]},{"body_a":"world","body_b":"grasp_target","contact_count":988.0,"contact_point_centroid":[0.47616,-0.02015,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12312,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48717,-0.00903,0.30858]},{"body_a":"world","body_b":"grasp_target","contact_count":3408.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47368,-0.0185,0.18035]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.51204,-0.01023,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.58354,0.11157,0.22041]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51204,-0.01023,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61934,0.1516,0.22558]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4842.0,"contact_point_centroid":[0.46425,-0.00051,0.0397],"force_p95":0.06731,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09537,"mean_force":0.04485,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4642,-0.01972,0.0373]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5139.0,"contact_point_centroid":[0.46411,-0.03894,0.03924],"force_p95":0.06597,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0826,"mean_force":0.04293,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46421,-0.01972,0.0373]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3680.0,"contact_point_centroid":[0.51163,0.03251,0.20013],"force_p95":0.01107,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01625,"mean_force":0.01052,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51133,0.03251,0.19786]},{"body_a":"left_finger","body_b":"right_finger","contact_count":4302.0,"contact_point_centroid":[0.58401,0.11159,0.22269],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01285,"mean_force":0.01037,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.58356,0.11158,0.22042]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.62192,0.15235,0.22446],"force_p95":0.0109,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01092,"mean_force":0.00996,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62156,0.15234,0.22216]}],"total_contact_groups":14},"final_pose_error":0.01442,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.51204,-0.01023,0.01602],"final_tcp_position":[0.62282,0.15244,0.22542],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273007.74486,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":248.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":988.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47728,-0.01717,0.3187],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.2927,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":852.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3408.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47195,-0.0199,0.0451],"tcp_start":[0.47728,-0.01717,0.3187],"tcp_to_object_dist_end":0.01954,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47606,-0.01978,0.02585],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28831,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13301,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11781.0,"raw_peak_contact_force":0.17191,"subtask_id":"grasp_1","tcp_end":[0.46418,-0.01972,0.03727],"tcp_start":[0.47195,-0.0199,0.0451],"tcp_to_object_dist_end":0.01648,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":316.0,"n_steps_budget":600.0,"object_pos_end":[0.48876,-0.01963,0.14588],"object_pos_start":[0.47606,-0.01978,0.02585],"object_to_goal_dist_end":0.23298,"object_to_goal_dist_start":0.28831,"object_z_max":0.14632,"peak_contact_force":0.0,"phase_name":"lift_vertical","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9348.0,"raw_peak_contact_force":0.57938,"tcp_end":[0.46659,-0.01963,0.16788],"tcp_start":[0.46663,-0.01963,0.16769],"tcp_to_object_dist_end":0.03124,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51204,-0.01023,0.01602],"object_pos_start":[0.49062,-0.01887,0.14457],"object_to_goal_dist_end":0.27061,"object_to_goal_dist_start":0.23151,"object_z_max":0.14457,"peak_contact_force":0.12263,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7390.0,"raw_peak_contact_force":1.59724,"subtask_id":"transport_arc","tcp_end":[0.54295,0.06642,0.22045],"tcp_start":[0.46659,-0.01963,0.16788],"tcp_to_object_dist_end":0.22051,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51204,-0.01023,0.01602],"object_pos_start":[0.51204,-0.01023,0.01602],"object_to_goal_dist_end":0.27061,"object_to_goal_dist_start":0.27061,"object_z_max":0.01602,"peak_contact_force":273007.74486,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8302.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.62282,0.15244,0.22542],"tcp_start":[0.54295,0.06642,0.22045],"tcp_to_object_dist_end":0.28737,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51204,-0.01023,0.01602],"object_pos_start":[0.51204,-0.01023,0.01602],"object_to_goal_dist_end":0.27061,"object_to_goal_dist_start":0.27061,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61808,0.15117,0.24495],"tcp_start":[0.62282,0.15244,0.22542],"tcp_to_object_dist_end":0.29951,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```