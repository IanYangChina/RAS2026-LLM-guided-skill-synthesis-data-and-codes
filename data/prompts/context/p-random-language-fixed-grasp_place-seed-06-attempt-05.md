## Search State

- **Seed**: 6
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 8 | 0.1050 | 0.30 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | -0.0191 | 0.31 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 8 | 0.2021 | 0.49 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 8 | -0.1415 | 0.25 | ✅ accepted |
| 1 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1417 | 0.25 | ❌ rejected |

**Proposal policy**: task_score is 0.30 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.105) — your mutation base

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

- **Composite score**: 0.105
- **task_score** (E): 0.296
- **fitness_score**: 0.625  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_object | 1.00 | 1.00 | 0.2652 |
| descend_to_grasp | 1.00 | 1.00 | 0.0046 |
| grasp_object | 1.00 | 1.00 | 0.0124 |
| lift_object | 0.33 | 1.00 | 0.1540 |
| transport_to_goal | 1.00 | 1.00 | 0.2005 |
| release_at_goal | 1.00 | 1.00 | 0.0218 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, 0.023, 0.038) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.495, 0.023, 0.038)→(0.494, 0.023, 0.034) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.494, 0.023, 0.034)→(0.485, 0.023, 0.025) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.025) | 0.271→0.273 | 1.00 / 42.000 | 0.176 | 0.251 |
| lift_object | lift | 0.33 / step_budget | (0.485, 0.023, 0.025)→(0.482, 0.022, 0.179) | (0.500, 0.023, 0.025)→(0.494, 0.023, 0.167) | 0.273→0.217 | 1.00 / 32.333 | 0.103 | 0.741 |
| transport_to_goal | approach | 1.00 / step_budget | (0.482, 0.022, 0.179)→(0.586, 0.178, 0.206) | (0.494, 0.023, 0.167)→(0.589, 0.180, 0.184) | 0.217→0.033 | 1.00 / 32.333 | 0.103 | 0.350 |
| release_at_goal | release | 1.00 / step_budget | (0.586, 0.178, 0.206)→(0.581, 0.177, 0.227) | (0.589, 0.180, 0.184)→(0.581, 0.178, 0.018) | 0.033→0.192 | 1.00 / 3.667 | 0.142 | 1.678 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.448
- phase_score: 0.793
- phase_breakdown.transport_arc_score: 0.819
- phase_breakdown.release_1_score: 0.544
- phase_breakdown.approach_1_score: 0.822
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.699
- grasp_place_fitness: 0.700

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.700
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.448
- **Median Q (composite search score)**: 0.079
- **K-run variance**: 0.0029
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.355


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93805,"average_solve_count":113.0,"average_success_count":113.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.07682,"descend_to_grasp.speed":0.05247,"grasp_object.max_time":0.55938,"lift_object.lift_height":0.23015,"lift_object.speed":0.03522,"release_at_goal.max_time":0.54014,"transport_to_goal.arc_height":0.28429,"transport_to_goal.speed":0.14146},"optimized_scores":{"best_composite_score":0.05587,"best_fitness_score":0.57587,"best_task_score":0.19781},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":141.0,"contact_point_centroid":[0.57451,0.15522,-0.00919],"force_p95":1.585,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.03782,"mean_force":0.57969,"phase_index":5.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.56473,0.15618,0.25477]},{"body_a":"world","body_b":"grasp_target","contact_count":151.0,"contact_point_centroid":[0.4981,-0.01448,-0.00116],"force_p95":0.51986,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73779,"mean_force":0.13236,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48762,-0.01495,0.0263]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17623.0,"contact_point_centroid":[0.48545,-0.03409,0.08507],"force_p95":0.07962,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3206,"mean_force":0.05712,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48486,-0.01492,0.08257]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1188.0,"contact_point_centroid":[0.56378,0.17584,0.23763],"force_p95":0.07923,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31616,"mean_force":0.05243,"phase_index":5.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.56778,0.15725,0.23538]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20238.0,"contact_point_centroid":[0.48631,0.00407,0.08157],"force_p95":0.07567,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3128,"mean_force":0.05096,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48487,-0.01492,0.07975]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1289.0,"contact_point_centroid":[0.57274,0.13876,0.2352],"force_p95":0.07678,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27419,"mean_force":0.049,"phase_index":5.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.56774,0.15723,0.2353]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18412.0,"contact_point_centroid":[0.52725,0.04957,0.20133],"force_p95":0.08605,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22428,"mean_force":0.05574,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.524,0.06828,0.20068]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17763.0,"contact_point_centroid":[0.52194,0.08439,0.20068],"force_p95":0.08465,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19265,"mean_force":0.05683,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52255,0.06546,0.19912]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50383,-0.01566,-0.00205],"force_p95":0.141,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18408,"mean_force":0.12715,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49049,-0.01497,0.02607]},{"body_a":"world","body_b":"grasp_target","contact_count":2956.0,"contact_point_centroid":[0.50382,-0.01567,-0.00195],"force_p95":0.12834,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.49836,-0.00736,0.16848]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49794,-0.01491,0.0364]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5293.0,"contact_point_centroid":[0.49024,0.00408,0.02687],"force_p95":0.06399,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10187,"mean_force":0.04106,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48924,-0.01496,0.02478]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4185.0,"contact_point_centroid":[0.48899,-0.03426,0.02757],"force_p95":0.07755,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08851,"mean_force":0.05192,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48925,-0.01496,0.02478]}],"total_contact_groups":13},"final_pose_error":0.03633,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.57515,0.1576,0.00718],"final_tcp_position":[0.56921,0.15722,0.23849],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":2.03782,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":740.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2956.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.4988,-0.01484,0.03849],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01347,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":23.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":92.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49785,-0.01501,0.03382],"tcp_start":[0.4988,-0.01484,0.03849],"tcp_to_object_dist_end":0.00985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50367,-0.01534,0.0258],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31221,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.14039,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11278.0,"raw_peak_contact_force":0.18408,"subtask_id":"grasp_1","tcp_end":[0.48921,-0.01496,0.02474],"tcp_start":[0.49785,-0.01501,0.03382],"tcp_to_object_dist_end":0.0145,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49683,-0.01526,0.13181],"object_pos_start":[0.50367,-0.01534,0.0258],"object_to_goal_dist_end":0.25046,"object_to_goal_dist_start":0.31221,"object_z_max":0.13173,"peak_contact_force":0.08061,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38012.0,"raw_peak_contact_force":0.73779,"tcp_end":[0.48517,-0.01492,0.14001],"tcp_start":[0.48921,-0.01496,0.02474],"tcp_to_object_dist_end":0.01426,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57493,0.15948,0.22303],"object_pos_start":[0.49683,-0.01526,0.13181],"object_to_goal_dist_end":0.03944,"object_to_goal_dist_start":0.25046,"object_z_max":0.223,"peak_contact_force":0.08247,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36175.0,"raw_peak_contact_force":0.22428,"subtask_id":"transport_arc","tcp_end":[0.56921,0.15722,0.23849],"tcp_start":[0.48517,-0.01492,0.14001],"tcp_to_object_dist_end":0.01664,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.57515,0.1576,0.00718],"object_pos_start":[0.57493,0.15948,0.22303],"object_to_goal_dist_end":0.24307,"object_to_goal_dist_start":0.03944,"object_z_max":0.22303,"peak_contact_force":0.11278,"phase_name":"release_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2618.0,"raw_peak_contact_force":2.03782,"subtask_id":"release_1","tcp_end":[0.56469,0.15618,0.26043],"tcp_start":[0.56921,0.15722,0.23849],"tcp_to_object_dist_end":0.25348,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.98095,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.09423,"descend_to_grasp.speed":0.01009,"grasp_object.max_time":0.10278,"lift_object.lift_height":0.19285,"lift_object.speed":0.05985,"release_at_goal.max_time":0.38798,"transport_to_goal.arc_height":0.06097,"transport_to_goal.speed":0.18317},"optimized_scores":{"best_composite_score":0.1799,"best_fitness_score":0.6999,"best_task_score":0.44814},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":249.0,"contact_point_centroid":[0.6071,0.17096,-0.00494],"force_p95":0.98334,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.34451,"mean_force":0.27344,"phase_index":5.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.61608,0.16845,0.16301]},{"body_a":"world","body_b":"grasp_target","contact_count":179.0,"contact_point_centroid":[0.50882,0.03598,-0.00145],"force_p95":0.46937,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76879,"mean_force":0.11444,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49555,0.0369,0.02599]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10209.0,"contact_point_centroid":[0.56272,0.08483,0.21978],"force_p95":0.15101,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.53161,"mean_force":0.09791,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5559,0.10204,0.22248]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":778.0,"contact_point_centroid":[0.62689,0.15255,0.1435],"force_p95":0.1258,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.46049,"mean_force":0.08733,"phase_index":5.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.61999,0.16961,0.14848]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9855.0,"contact_point_centroid":[0.55844,0.12244,0.22105],"force_p95":0.15577,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44832,"mean_force":0.09599,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5577,0.10388,0.22253]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":781.0,"contact_point_centroid":[0.61863,0.18844,0.14618],"force_p95":0.12432,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43991,"mean_force":0.08549,"phase_index":5.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.61998,0.16961,0.14847]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11996.0,"contact_point_centroid":[0.49673,0.05584,0.10843],"force_p95":0.11087,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39947,"mean_force":0.07897,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49342,0.03674,0.10627]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15615.0,"contact_point_centroid":[0.49753,0.01833,0.10456],"force_p95":0.10281,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30934,"mean_force":0.06339,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49341,0.03674,0.10387]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51271,0.03949,-0.00226],"force_p95":0.19547,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.27973,"mean_force":0.14202,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49873,0.03716,0.02543]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5176.0,"contact_point_centroid":[0.49909,0.01826,0.02602],"force_p95":0.06593,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21102,"mean_force":0.0409,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49747,0.03706,0.02409]},{"body_a":"world","body_b":"grasp_target","contact_count":2932.0,"contact_point_centroid":[0.51251,0.03972,-0.00195],"force_p95":0.12867,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.50248,0.0186,0.16761]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50617,0.03749,0.03578]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3959.0,"contact_point_centroid":[0.49885,0.05657,0.02688],"force_p95":0.09473,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.107,"mean_force":0.05896,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49748,0.03706,0.0241]}],"total_contact_groups":13},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.60896,0.17131,0.02608],"final_tcp_position":[0.62237,0.17025,0.15323],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.34451,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":734.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2932.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50697,0.03738,0.03771],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01315,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":22.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":88.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50611,0.0377,0.0334],"tcp_start":[0.50697,0.03738,0.03771],"tcp_to_object_dist_end":0.00998,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51264,0.03776,0.02512],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21388,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.18736,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10935.0,"raw_peak_contact_force":0.27973,"subtask_id":"grasp_1","tcp_end":[0.49744,0.03706,0.02406],"tcp_start":[0.50611,0.0377,0.0334],"tcp_to_object_dist_end":0.01525,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":26.0,"n_steps":957.0,"n_steps_budget":1000.0,"object_pos_end":[0.50757,0.03804,0.18772],"object_pos_start":[0.51264,0.03776,0.02512],"object_to_goal_dist_end":0.18523,"object_to_goal_dist_start":0.21388,"object_z_max":0.18758,"peak_contact_force":0.10926,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27790.0,"raw_peak_contact_force":0.76879,"tcp_end":[0.49406,0.03679,0.20351],"tcp_start":[0.49744,0.03706,0.02406],"tcp_to_object_dist_end":0.02081,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":977.0,"n_steps_budget":1000.0,"object_pos_end":[0.62426,0.17281,0.12004],"object_pos_start":[0.50757,0.03804,0.18772],"object_to_goal_dist_end":0.02521,"object_to_goal_dist_start":0.18523,"object_z_max":0.22605,"peak_contact_force":0.13633,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20064.0,"raw_peak_contact_force":0.53161,"subtask_id":"transport_arc","tcp_end":[0.62237,0.17025,0.15323],"tcp_start":[0.49406,0.03679,0.20351],"tcp_to_object_dist_end":0.03335,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.60896,0.17131,0.02608],"object_pos_start":[0.62426,0.17281,0.12004],"object_to_goal_dist_end":0.1204,"object_to_goal_dist_start":0.02521,"object_z_max":0.12004,"peak_contact_force":0.12088,"phase_name":"release_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1808.0,"raw_peak_contact_force":1.34451,"subtask_id":"release_1","tcp_end":[0.616,0.16844,0.17285],"tcp_start":[0.62237,0.17025,0.15323],"tcp_to_object_dist_end":0.14697,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72269,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.06578,"descend_to_grasp.speed":0.08243,"grasp_object.max_time":0.68815,"lift_object.lift_height":0.25533,"lift_object.speed":0.05124,"release_at_goal.max_time":0.67933,"transport_to_goal.arc_height":0.26984,"transport_to_goal.speed":0.19093},"optimized_scores":{"best_composite_score":0.07926,"best_fitness_score":0.59926,"best_task_score":0.24169},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":176.0,"contact_point_centroid":[0.55028,0.19928,-0.00816],"force_p95":1.43416,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.6531,"mean_force":0.43181,"phase_index":5.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.56184,0.2063,0.24216]},{"body_a":"world","body_b":"grasp_target","contact_count":152.0,"contact_point_centroid":[0.4789,0.0438,-0.00146],"force_p95":0.44719,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.7156,"mean_force":0.11427,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46763,0.04532,0.02786]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16956.0,"contact_point_centroid":[0.46577,0.06434,0.1104],"force_p95":0.10493,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33677,"mean_force":0.06179,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4653,0.04511,0.10823]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20969.0,"contact_point_centroid":[0.51885,0.10836,0.22147],"force_p95":0.08929,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29349,"mean_force":0.04787,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51472,0.12661,0.22034]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20627.0,"contact_point_centroid":[0.4678,0.02645,0.10823],"force_p95":0.08436,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29118,"mean_force":0.04973,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46531,0.04511,0.10682]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48291,0.04842,-0.00232],"force_p95":0.20976,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28872,"mean_force":0.146,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.47052,0.04561,0.0269]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1213.0,"contact_point_centroid":[0.5597,0.22594,0.22866],"force_p95":0.08409,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27732,"mean_force":0.04463,"phase_index":5.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.56495,0.20766,0.22433]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1448.0,"contact_point_centroid":[0.57085,0.18919,0.22603],"force_p95":0.08073,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22141,"mean_force":0.03823,"phase_index":5.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.56497,0.20767,0.22436]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4919.0,"contact_point_centroid":[0.47128,0.02658,0.02699],"force_p95":0.07847,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20995,"mean_force":0.04328,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4693,0.04549,0.02568]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15191.0,"contact_point_centroid":[0.51409,0.14771,0.22286],"force_p95":0.11717,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20411,"mean_force":0.06913,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51609,0.12876,0.22064]},{"body_a":"world","body_b":"grasp_target","contact_count":3144.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12742,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12278,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.48838,0.02272,0.16838]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47792,0.04594,0.03671]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4137.0,"contact_point_centroid":[0.46965,0.065,0.02817],"force_p95":0.09518,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09885,"mean_force":0.0548,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46932,0.04549,0.0257]}],"total_contact_groups":13},"final_pose_error":0.02628,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.55823,0.20475,0.02016],"final_tcp_position":[0.5664,0.20783,0.22748],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.6531,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":787.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3144.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47881,0.04579,0.03871],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01359,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":23.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":92.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.4777,0.04624,0.03417],"tcp_start":[0.47881,0.04579,0.03871],"tcp_to_object_dist_end":0.00988,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48279,0.04623,0.02493],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29227,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.20011,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10856.0,"raw_peak_contact_force":0.28872,"subtask_id":"grasp_1","tcp_end":[0.46928,0.04549,0.02566],"tcp_start":[0.4777,0.04624,0.03417],"tcp_to_object_dist_end":0.01355,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47798,0.04608,0.18088],"object_pos_start":[0.48279,0.04623,0.02493],"object_to_goal_dist_end":0.21601,"object_to_goal_dist_start":0.29227,"object_z_max":0.1807,"peak_contact_force":0.11817,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37735.0,"raw_peak_contact_force":0.7156,"tcp_end":[0.46577,0.04515,0.19295],"tcp_start":[0.46928,0.04549,0.02566],"tcp_to_object_dist_end":0.01719,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56728,0.20886,0.20851],"object_pos_start":[0.47798,0.04608,0.18088],"object_to_goal_dist_end":0.0331,"object_to_goal_dist_start":0.21601,"object_z_max":0.21467,"peak_contact_force":0.09145,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":36160.0,"raw_peak_contact_force":0.29349,"subtask_id":"transport_arc","tcp_end":[0.5664,0.20783,0.22748],"tcp_start":[0.46577,0.04515,0.19295],"tcp_to_object_dist_end":0.01902,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55823,0.20475,0.02016],"object_pos_start":[0.56728,0.20886,0.20851],"object_to_goal_dist_end":0.21301,"object_to_goal_dist_start":0.0331,"object_z_max":0.20851,"peak_contact_force":0.19356,"phase_name":"release_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2837.0,"raw_peak_contact_force":1.6531,"subtask_id":"release_1","tcp_end":[0.5618,0.2063,0.24911],"tcp_start":[0.5664,0.20783,0.22748],"tcp_to_object_dist_end":0.22898,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```