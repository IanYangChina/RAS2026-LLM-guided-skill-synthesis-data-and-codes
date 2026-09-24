## Search State

- **Seed**: 6
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → grasp → lift → approach → descend → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 10 | -0.0191 | 0.31 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 8 | 0.2021 | 0.49 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → release | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | — | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | time_limit | 8 | -0.1415 | 0.25 | ✅ accepted |
| 1 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1417 | 0.25 | ❌ rejected |
| 0 | align → lift → push → approach → approach → descend → grasp → rotate | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | impedance_motion | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 6 | -0.1416 | 0.25 | ❌ rejected |

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

## Current Skill (Q=-0.019) — your mutation base

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

- **Composite score**: -0.019
- **task_score** (E): 0.306
- **fitness_score**: 0.631  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.650

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_object | 1.00 | 1.00 | 0.1665 |
| descend_to_grasp | 1.00 | 1.00 | 0.1041 |
| grasp_object | 1.00 | 1.00 | 0.0125 |
| lift_object | 0.67 | 1.00 | 0.1371 |
| transport_to_goal | 0.67 | 1.00 | 0.1894 |
| descend_to_place | 1.00 | 1.00 | 0.0469 |
| release_at_goal | 1.00 | 1.00 | 0.0161 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.022, 0.138) | (0.500, 0.024, 0.030)→(0.500, 0.024, 0.026) | 0.269→0.271 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.496, 0.022, 0.138)→(0.494, 0.024, 0.034) | (0.500, 0.024, 0.026)→(0.500, 0.024, 0.026) | 0.271→0.271 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_object | grasp | 1.00 / step_budget | (0.494, 0.024, 0.034)→(0.486, 0.023, 0.025) | (0.500, 0.024, 0.026)→(0.500, 0.023, 0.026) | 0.271→0.272 | 1.00 / 42.667 | 0.153 | 0.210 |
| lift_object | lift | 0.67 / step_budget | (0.486, 0.023, 0.025)→(0.482, 0.023, 0.162) | (0.500, 0.023, 0.026)→(0.496, 0.023, 0.152) | 0.272→0.220 | 1.00 / 30.667 | 0.113 | 0.757 |
| transport_to_goal | approach | 0.67 / step_budget | (0.482, 0.023, 0.162)→(0.576, 0.163, 0.228) | (0.496, 0.023, 0.152)→(0.581, 0.165, 0.209) | 0.220→0.043 | 1.00 / 30.000 | 3253.496 | 0.252 |
| descend_to_place | descend | 1.00 / step_budget | (0.576, 0.163, 0.228)→(0.593, 0.191, 0.206) | (0.581, 0.165, 0.209)→(0.598, 0.194, 0.117) | 0.043→0.092 | 1.00 / 31.000 | 3248.870 | 0.831 |
| release_at_goal | release | 1.00 / step_budget | (0.593, 0.191, 0.206)→(0.588, 0.190, 0.218) | (0.598, 0.194, 0.117)→(0.593, 0.191, 0.022) | 0.092→0.186 | 1.00 / 4.000 | 0.145 | 0.972 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.459
- phase_score: 0.547
- phase_breakdown.transport_arc_score: 0.424
- phase_breakdown.release_1_score: 0.576
- phase_breakdown.approach_1_score: 0.115
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.715
- grasp_place_fitness: 0.707

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.707
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.459
- **Median Q (composite search score)**: -0.048
- **K-run variance**: 0.0029
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.287


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86087,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.05435,"descend_to_grasp.speed":0.0565,"descend_to_place.speed":0.06523,"descend_to_place.tolerance":0.01043,"grasp_object.max_time":0.40604,"lift_object.lift_height":0.13965,"lift_object.speed":0.06775,"release_at_goal.max_time":0.58542,"transport_to_goal.speed":0.13879,"transport_to_goal.tolerance":0.01113},"optimized_scores":{"best_composite_score":-0.06584,"best_fitness_score":0.58416,"best_task_score":0.21277},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":241.0,"contact_point_centroid":[0.5955,0.18616,-0.00791],"force_p95":1.19182,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.15335,"mean_force":0.35416,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57809,0.17602,0.24785]},{"body_a":"world","body_b":"grasp_target","contact_count":151.0,"contact_point_centroid":[0.50102,-0.01554,-0.00112],"force_p95":0.48243,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.75731,"mean_force":0.11371,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.4881,-0.0154,0.02682]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8822.0,"contact_point_centroid":[0.48776,-0.03444,0.08032],"force_p95":0.10791,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33191,"mean_force":0.06951,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48556,-0.01537,0.07793]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10405.0,"contact_point_centroid":[0.48844,0.00338,0.07766],"force_p95":0.10129,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32736,"mean_force":0.06076,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.48558,-0.01537,0.07611]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10808.0,"contact_point_centroid":[0.5304,0.04987,0.20351],"force_p95":0.14216,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32608,"mean_force":0.08976,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52425,0.06766,0.20527]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11201.0,"contact_point_centroid":[0.52624,0.0851,0.20368],"force_p95":0.12772,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3033,"mean_force":0.08663,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.52368,0.06646,0.20447]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":163.0,"contact_point_centroid":[0.57024,0.17376,0.26305],"force_p95":0.18193,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28843,"mean_force":0.07864,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56938,0.15726,0.26713]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":26.0,"contact_point_centroid":[0.58125,0.14167,0.26251],"force_p95":0.18955,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21577,"mean_force":0.12688,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.56897,0.1562,0.26835]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5038,-0.01575,-0.00203],"force_p95":0.13289,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15815,"mean_force":0.12511,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49099,-0.01542,0.02642]},{"body_a":"world","body_b":"grasp_target","contact_count":1952.0,"contact_point_centroid":[0.50382,-0.01567,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.49876,-0.00698,0.21961]},{"body_a":"world","body_b":"grasp_target","contact_count":200.0,"contact_point_centroid":[0.59594,0.18632,-0.00177],"force_p95":0.12524,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12534,"mean_force":0.11038,"phase_index":6.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.57915,0.18002,0.242]},{"body_a":"world","body_b":"grasp_target","contact_count":1292.0,"contact_point_centroid":[0.50382,-0.01567,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.49765,-0.01488,0.08587]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4148.0,"contact_point_centroid":[0.48932,-0.03468,0.02779],"force_p95":0.07893,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09458,"mean_force":0.05186,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48975,-0.01541,0.02512]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5325.0,"contact_point_centroid":[0.4906,0.00365,0.02711],"force_p95":0.06668,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09403,"mean_force":0.0411,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.48975,-0.01541,0.02512]},{"body_a":"left_finger","body_b":"right_finger","contact_count":86.0,"contact_point_centroid":[0.57927,0.17857,0.24827],"force_p95":0.01548,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01647,"mean_force":0.01308,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.57962,0.17881,0.2458]},{"body_a":"left_finger","body_b":"right_finger","contact_count":217.0,"contact_point_centroid":[0.57943,0.17997,0.24413],"force_p95":0.01167,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01179,"mean_force":0.01051,"phase_index":6.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.57913,0.18002,0.24197]}],"total_contact_groups":16},"final_pose_error":0.01035,"key_states":{"actual_goal_position":[0.58691,0.18745,0.24812],"final_object_position":[0.59594,0.1863,0.01617],"final_tcp_position":[0.58034,0.18015,0.24484],"realised_goal_position":[0.58691,0.18745,0.24812],"realised_object_initial_position":[0.50382,-0.01567,0.03]},"peak_contact_force":9760.30694,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":489.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.03],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.30942,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1952.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49958,-0.01433,0.1387],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":323.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,-0.01567,0.02602],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31223,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1292.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.4984,-0.01547,0.03424],"tcp_start":[0.49958,-0.01433,0.1387],"tcp_to_object_dist_end":0.00984,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50366,-0.01575,0.02589],"object_pos_start":[0.50382,-0.01567,0.02602],"object_to_goal_dist_end":0.31242,"object_to_goal_dist_start":0.31223,"object_z_max":0.02602,"peak_contact_force":0.13301,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11273.0,"raw_peak_contact_force":0.15815,"subtask_id":"grasp_1","tcp_end":[0.48972,-0.01541,0.02509],"tcp_start":[0.4984,-0.01547,0.03424],"tcp_to_object_dist_end":0.01397,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":602.0,"n_steps_budget":660.0,"object_pos_end":[0.50399,-0.01599,0.14003],"object_pos_start":[0.50366,-0.01575,0.02589],"object_to_goal_dist_end":0.24484,"object_to_goal_dist_start":0.31242,"object_z_max":0.13988,"peak_contact_force":0.11798,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":19378.0,"raw_peak_contact_force":0.75731,"tcp_end":[0.48586,-0.01536,0.15055],"tcp_start":[0.48972,-0.01541,0.02509],"tcp_to_object_dist_end":0.02097,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":13.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57552,0.15873,0.24351],"object_pos_start":[0.50399,-0.01599,0.14003],"object_to_goal_dist_end":0.03124,"object_to_goal_dist_start":0.24484,"object_z_max":0.24354,"peak_contact_force":9760.30694,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22009.0,"raw_peak_contact_force":0.32608,"subtask_id":"transport_arc","tcp_end":[0.56893,0.15588,0.26834],"tcp_start":[0.48586,-0.01536,0.15055],"tcp_to_object_dist_end":0.02584,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":169.0,"n_steps_budget":1000.0,"object_pos_end":[0.596,0.18636,0.01556],"object_pos_start":[0.57552,0.15873,0.24351],"object_to_goal_dist_end":0.23274,"object_to_goal_dist_start":0.03124,"object_z_max":0.24351,"peak_contact_force":9746.45264,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":516.0,"raw_peak_contact_force":2.15335,"tcp_end":[0.58034,0.18015,0.24484],"tcp_start":[0.56893,0.15588,0.26834],"tcp_to_object_dist_end":0.22989,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59594,0.1863,0.01617],"object_pos_start":[0.596,0.18636,0.01556],"object_to_goal_dist_end":0.23213,"object_to_goal_dist_start":0.23274,"object_z_max":0.01679,"peak_contact_force":0.1253,"phase_name":"release_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":417.0,"raw_peak_contact_force":0.12534,"subtask_id":"release_1","tcp_end":[0.57827,0.17966,0.23984],"tcp_start":[0.58034,0.18015,0.24484],"tcp_to_object_dist_end":0.22446,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36158,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.03005,"descend_to_grasp.speed":0.02897,"descend_to_place.speed":0.06677,"descend_to_place.tolerance":0.00806,"grasp_object.max_time":0.66394,"lift_object.lift_height":0.21009,"lift_object.speed":0.05148,"release_at_goal.max_time":0.32782,"transport_to_goal.speed":0.10375,"transport_to_goal.tolerance":0.01362},"optimized_scores":{"best_composite_score":0.05667,"best_fitness_score":0.70667,"best_task_score":0.45865},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.61374,0.16792,-0.00844],"force_p95":1.14196,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.20232,"mean_force":0.48339,"phase_index":6.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.615,0.16799,0.15828]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.50758,0.0371,-0.00127],"force_p95":0.56524,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.79745,"mean_force":0.13108,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49664,0.03806,0.02652]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16678.0,"contact_point_centroid":[0.49492,0.05709,0.10662],"force_p95":0.11042,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.35063,"mean_force":0.06288,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49411,0.03786,0.10457]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20496.0,"contact_point_centroid":[0.49635,0.01921,0.10673],"force_p95":0.08469,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32837,"mean_force":0.05032,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.49412,0.03786,0.10525]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15046.0,"contact_point_centroid":[0.56425,0.08907,0.18762],"force_p95":0.08801,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26385,"mean_force":0.05092,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.56077,0.10755,0.18686]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51258,0.03959,-0.00213],"force_p95":0.16227,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23103,"mean_force":0.13293,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49949,0.0383,0.02614]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11346.0,"contact_point_centroid":[0.56103,0.12813,0.18932],"force_p95":0.11269,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21369,"mean_force":0.06742,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5623,0.1091,0.18685]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1344.0,"contact_point_centroid":[0.62309,0.15041,0.1459],"force_p95":0.08059,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21289,"mean_force":0.04077,"phase_index":6.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.61924,0.16924,0.1452]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1105.0,"contact_point_centroid":[0.61509,0.18783,0.14936],"force_p95":0.08247,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21244,"mean_force":0.04687,"phase_index":6.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.61923,0.16924,0.14519]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2926.0,"contact_point_centroid":[0.623,0.14911,0.16877],"force_p95":0.08094,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19331,"mean_force":0.04668,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61929,0.16791,0.16791]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2394.0,"contact_point_centroid":[0.61516,0.18648,0.17179],"force_p95":0.08412,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18568,"mean_force":0.05424,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61929,0.16791,0.16791]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5233.0,"contact_point_centroid":[0.49966,0.01919,0.02653],"force_p95":0.06804,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17887,"mean_force":0.04119,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49824,0.0382,0.0248]},{"body_a":"world","body_b":"grasp_target","contact_count":2252.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.50254,0.01771,0.21885]},{"body_a":"world","body_b":"grasp_target","contact_count":1408.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.50572,0.03745,0.08556]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4242.0,"contact_point_centroid":[0.49869,0.05755,0.02761],"force_p95":0.08271,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09561,"mean_force":0.05199,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.49825,0.0382,0.02481]}],"total_contact_groups":15},"final_pose_error":0.00806,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.61692,0.16836,0.02866],"final_tcp_position":[0.62125,0.16976,0.14919],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.20232,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":564.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2252.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50749,0.03625,0.1379],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11205,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":352.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1408.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50693,0.0389,0.0342],"tcp_start":[0.50749,0.03625,0.1379],"tcp_to_object_dist_end":0.00994,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51243,0.03865,0.02554],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.2132,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.15962,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11275.0,"raw_peak_contact_force":0.23103,"subtask_id":"grasp_1","tcp_end":[0.49821,0.03819,0.02477],"tcp_start":[0.50693,0.0389,0.0342],"tcp_to_object_dist_end":0.01425,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50768,0.03855,0.18095],"object_pos_start":[0.51243,0.03865,0.02554],"object_to_goal_dist_end":0.18334,"object_to_goal_dist_start":0.2132,"object_z_max":0.1808,"peak_contact_force":0.14072,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37318.0,"raw_peak_contact_force":0.79745,"tcp_end":[0.49467,0.03791,0.19181],"tcp_start":[0.49821,0.03819,0.02477],"tcp_to_object_dist_end":0.01696,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":743.0,"n_steps_budget":1000.0,"object_pos_end":[0.62065,0.16755,0.17026],"object_pos_start":[0.50768,0.03855,0.18095],"object_to_goal_dist_end":0.02664,"object_to_goal_dist_start":0.18334,"object_z_max":0.18103,"peak_contact_force":0.08585,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26392.0,"raw_peak_contact_force":0.26385,"subtask_id":"transport_arc","tcp_end":[0.61887,0.1665,0.18657],"tcp_start":[0.49467,0.03791,0.19181],"tcp_to_object_dist_end":0.01643,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":133.0,"n_steps_budget":1000.0,"object_pos_end":[0.62342,0.17117,0.13229],"object_pos_start":[0.62065,0.16755,0.17026],"object_to_goal_dist_end":0.01346,"object_to_goal_dist_start":0.02664,"object_z_max":0.17026,"peak_contact_force":0.0836,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5320.0,"raw_peak_contact_force":0.19331,"tcp_end":[0.62125,0.16976,0.14919],"tcp_start":[0.61887,0.1665,0.18657],"tcp_to_object_dist_end":0.0171,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61692,0.16836,0.02866],"object_pos_start":[0.62342,0.17117,0.13229],"object_to_goal_dist_end":0.11692,"object_to_goal_dist_start":0.01346,"object_z_max":0.13229,"peak_contact_force":0.16128,"phase_name":"release_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2595.0,"raw_peak_contact_force":1.20232,"subtask_id":"release_1","tcp_end":[0.6149,0.16797,0.16908],"tcp_start":[0.62125,0.16976,0.14919],"tcp_to_object_dist_end":0.14043,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05581,"average_solve_count":215.0,"average_success_count":215.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.speed":0.0691,"descend_to_grasp.speed":0.01019,"descend_to_place.speed":0.03952,"descend_to_place.tolerance":0.01071,"grasp_object.max_time":0.60311,"lift_object.lift_height":0.22204,"lift_object.speed":0.03604,"release_at_goal.max_time":0.63162,"transport_to_goal.speed":0.09884,"transport_to_goal.tolerance":0.01078},"optimized_scores":{"best_composite_score":-0.04803,"best_fitness_score":0.60197,"best_task_score":0.24716},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":175.0,"contact_point_centroid":[0.55666,0.21635,-0.00804],"force_p95":1.47775,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.58968,"mean_force":0.43744,"phase_index":6.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.57182,0.22249,0.23605]},{"body_a":"world","body_b":"grasp_target","contact_count":161.0,"contact_point_centroid":[0.47795,0.04541,-0.00129],"force_p95":0.49172,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71625,"mean_force":0.12174,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46749,0.04676,0.02777]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17000.0,"contact_point_centroid":[0.4649,0.06572,0.08757],"force_p95":0.08423,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32611,"mean_force":0.05869,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46493,0.04652,0.08489]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20862.0,"contact_point_centroid":[0.46708,0.02762,0.0856],"force_p95":0.07898,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3006,"mean_force":0.04928,"phase_index":3.0,"phase_name":"lift_object","phase_type":"lift","tcp_position_centroid":[0.46493,0.04652,0.08412]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4828,0.04858,-0.00216],"force_p95":0.16904,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23966,"mean_force":0.13495,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.4704,0.04705,0.02722]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4984.0,"contact_point_centroid":[0.47118,0.02796,0.02727],"force_p95":0.07896,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19696,"mean_force":0.04321,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46918,0.04693,0.026]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20855.0,"contact_point_centroid":[0.5072,0.09178,0.1878],"force_p95":0.07528,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16674,"mean_force":0.04783,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50306,0.11023,0.18687]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11903.0,"contact_point_centroid":[0.56472,0.18077,0.22399],"force_p95":0.0762,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14686,"mean_force":0.0462,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55942,0.19916,0.22296]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16341.0,"contact_point_centroid":[0.5,0.12749,0.18834],"force_p95":0.09311,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14234,"mean_force":0.06303,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.50193,0.10845,0.18559]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1272.0,"contact_point_centroid":[0.56942,0.24199,0.22451],"force_p95":0.07381,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14023,"mean_force":0.0403,"phase_index":6.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.57502,0.22389,0.21937]},{"body_a":"world","body_b":"grasp_target","contact_count":1968.0,"contact_point_centroid":[0.4827,0.04873,-0.00193],"force_p95":0.13308,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12287,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.4893,0.02167,0.21939]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1458.0,"contact_point_centroid":[0.58095,0.20538,0.22088],"force_p95":0.06286,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13261,"mean_force":0.03697,"phase_index":6.0,"phase_name":"release_at_goal","phase_type":"release","tcp_position_centroid":[0.57501,0.22389,0.21936]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":9784.0,"contact_point_centroid":[0.55446,0.21785,0.2271],"force_p95":0.0825,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12738,"mean_force":0.05373,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.55972,0.19961,0.22293]},{"body_a":"world","body_b":"grasp_target","contact_count":1536.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47741,0.04594,0.08643]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4252.0,"contact_point_centroid":[0.4692,0.06628,0.0285],"force_p95":0.08587,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10088,"mean_force":0.05207,"phase_index":2.0,"phase_name":"grasp_object","phase_type":"grasp","tcp_position_centroid":[0.46919,0.04694,0.02601]}],"total_contact_groups":15},"final_pose_error":0.0107,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.56678,0.2198,0.02157],"final_tcp_position":[0.57636,0.22429,0.22252],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.58968,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":493.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1968.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48021,0.04446,0.13847],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11255,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":384.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1536.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47759,0.04775,0.03451],"tcp_start":[0.48021,0.04446,0.13847],"tcp_to_object_dist_end":0.00996,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4827,0.04747,0.02545],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29116,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.16533,"phase_name":"grasp_object","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11036.0,"raw_peak_contact_force":0.23966,"subtask_id":"grasp_1","tcp_end":[0.46916,0.04693,0.02597],"tcp_start":[0.47759,0.04775,0.03451],"tcp_to_object_dist_end":0.01356,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47608,0.04755,0.13558],"object_pos_start":[0.4827,0.04747,0.02545],"object_to_goal_dist_end":0.23037,"object_to_goal_dist_start":0.29116,"object_z_max":0.13549,"peak_contact_force":0.08035,"phase_name":"lift_object","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38023.0,"raw_peak_contact_force":0.71625,"tcp_end":[0.46523,0.04655,0.14457],"tcp_start":[0.46916,0.04693,0.02597],"tcp_to_object_dist_end":0.01413,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5457,0.1698,0.21377],"object_pos_start":[0.47608,0.04755,0.13558],"object_to_goal_dist_end":0.07124,"object_to_goal_dist_start":0.23037,"object_z_max":0.21372,"peak_contact_force":0.09585,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":37196.0,"raw_peak_contact_force":0.16674,"subtask_id":"transport_arc","tcp_end":[0.54019,0.16779,0.22879],"tcp_start":[0.46523,0.04655,0.14457],"tcp_to_object_dist_end":0.01613,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":540.0,"n_steps_budget":1000.0,"object_pos_end":[0.57371,0.22474,0.20365],"object_pos_start":[0.5457,0.1698,0.21377],"object_to_goal_dist_end":0.02835,"object_to_goal_dist_start":0.07124,"object_z_max":0.21377,"peak_contact_force":0.07412,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":21687.0,"raw_peak_contact_force":0.14686,"tcp_end":[0.57636,0.22429,0.22252],"tcp_start":[0.54019,0.16779,0.22879],"tcp_to_object_dist_end":0.01906,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.56678,0.2198,0.02157],"object_pos_start":[0.57371,0.22474,0.20365],"object_to_goal_dist_end":0.20966,"object_to_goal_dist_start":0.02835,"object_z_max":0.20365,"peak_contact_force":0.14749,"phase_name":"release_at_goal","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2905.0,"raw_peak_contact_force":1.58968,"subtask_id":"release_1","tcp_end":[0.57177,0.22248,0.24374],"tcp_start":[0.57636,0.22429,0.22252],"tcp_to_object_dist_end":0.22224,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```