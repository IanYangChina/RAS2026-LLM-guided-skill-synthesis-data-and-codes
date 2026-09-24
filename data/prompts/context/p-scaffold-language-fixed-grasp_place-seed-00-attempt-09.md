## Search State

- **Seed**: 0
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.6572 | 1.00 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.6573 | 1.00 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.6574 | 1.00 | ❌ rejected |
| 6 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.5600 | 1.00 | ❌ rejected |
| 5 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.6574 | 1.00 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.657) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
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
    tolerance: 0.01
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.005
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
    tolerance: 0.01
  subtask_id: grasp_1
- id: lift_1
  type: lift
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
    tolerance: 0.05
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
- id: transport_arc
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
    - 0.15
    tolerance: 0.02
  parameters:
    transport_z_offset:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: transport_arc
- id: place_1
  type: descend
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
    tolerance: 0.02
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
- **grasp_1** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - parameter_bindings: none
- **lift_1** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.05
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
- **transport_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - parameter_bindings:
    - transport_z_offset: status=consumed; consumers=target.offset.z (replace)
- **place_1** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.657
- **task_score** (E): 1.000
- **fitness_score**: 0.977  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.320

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1075 |
| descend_1 | 1.00 | 1.00 | 0.1586 |
| grasp_1 | 1.00 | 1.00 | 0.0124 |
| lift_1 | 1.00 | 1.00 | 0.1478 |
| transport_arc | 1.00 | 1.00 | 0.2616 |
| place_1 | 1.00 | 1.00 | 0.1470 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.007, 0.198) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.122 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.494, 0.007, 0.198)→(0.492, 0.001, 0.039) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.492, 0.001, 0.039)→(0.483, 0.001, 0.030) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 42.667 | 0.147 | 0.199 |
| lift_1 | lift | 1.00 / step_budget | (0.483, 0.001, 0.030)→(0.492, 0.001, 0.178) | (0.497, 0.001, 0.026)→(0.507, 0.001, 0.174) | 0.265→0.212 | 1.00 / 39.667 | 0.084 | 0.646 |
| transport_arc | approach | 1.00 / step_budget | (0.492, 0.001, 0.178)→(0.574, 0.172, 0.351) | (0.507, 0.001, 0.174)→(0.588, 0.176, 0.342) | 0.212→0.156 | 1.00 / 34.333 | 0.102 | 0.143 |
| place_1 | descend | 1.00 / step_budget | (0.574, 0.172, 0.351)→(0.579, 0.182, 0.205) | (0.588, 0.176, 0.342)→(0.591, 0.186, 0.190) | 0.156→0.009 | 1.00 / 29.333 | 0.113 | 0.242 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.645
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.361
- phase_breakdown.release_1_score: 0.676
- phase_breakdown.transport_arc_score: 0.051
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.796
- phase_breakdown.approach_1_score: 0.049
- grasp_place_fitness: 0.978

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.978
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.657
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Parameters at lower bound**: descend_1.grasp_z_offset
- **Final σ (mean)**: 0.354


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81006,"average_solve_count":179.0,"average_success_count":179.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.22277,"descend_1.grasp_z_offset":0.005,"lift_1.lift_height":0.21962,"transport_arc.transport_z_offset":0.09863},"optimized_scores":{"best_composite_score":0.65709,"best_fitness_score":0.97709,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":62.0,"contact_point_centroid":[0.51021,-0.02254,-0.00152],"force_p95":0.57388,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67006,"mean_force":0.31327,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49859,-0.02232,0.03092]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3363.0,"contact_point_centroid":[0.50159,-0.04169,0.10889],"force_p95":0.09151,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33015,"mean_force":0.06509,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50238,-0.02247,0.1062]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4180.0,"contact_point_centroid":[0.50344,-0.00346,0.10957],"force_p95":0.0847,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3251,"mean_force":0.05461,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50251,-0.02247,0.10773]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1654.0,"contact_point_centroid":[0.55677,0.12555,0.27687],"force_p95":0.11017,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21926,"mean_force":0.07744,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.54936,0.14336,0.27611]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51371,-0.02306,-0.00206],"force_p95":0.1419,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18286,"mean_force":0.12748,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50104,-0.02236,0.03124]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2040.0,"contact_point_centroid":[0.54742,0.16189,0.27735],"force_p95":0.09272,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17629,"mean_force":0.06278,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.54935,0.14338,0.2759]},{"body_a":"world","body_b":"grasp_target","contact_count":316.0,"contact_point_centroid":[0.5137,-0.02302,-0.0016],"force_p95":0.13825,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12436,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50354,-0.00747,0.28686]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":10330.0,"contact_point_centroid":[0.53178,0.04197,0.25265],"force_p95":0.09537,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12996,"mean_force":0.06171,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52843,0.06084,0.25038]},{"body_a":"world","body_b":"grasp_target","contact_count":2796.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.1226,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50675,-0.01893,0.15285]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12082.0,"contact_point_centroid":[0.52766,0.07948,0.25232],"force_p95":0.07862,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10871,"mean_force":0.052,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52838,0.06065,0.25025]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5299.0,"contact_point_centroid":[0.50072,-0.00328,0.03181],"force_p95":0.06686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10859,"mean_force":0.04121,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49979,-0.02234,0.0299]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4178.0,"contact_point_centroid":[0.49913,-0.04161,0.03274],"force_p95":0.0797,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08712,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49979,-0.02234,0.0299]}],"total_contact_groups":12},"final_pose_error":0.01987,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.56502,0.15136,0.22916],"final_tcp_position":[0.55024,0.14746,0.24102],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":0.67006,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":80.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02596],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26565,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12218,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":316.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50735,-0.01539,0.26966],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.2439,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":699.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02596],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26565,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2796.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.50847,-0.02248,0.03936],"tcp_start":[0.50735,-0.01539,0.26966],"tcp_to_object_dist_end":0.01434,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51358,-0.02278,0.02578],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26565,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.1415,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11277.0,"raw_peak_contact_force":0.18286,"subtask_id":"grasp_1","tcp_end":[0.49976,-0.02234,0.02986],"tcp_start":[0.50847,-0.02248,0.03936],"tcp_to_object_dist_end":0.01442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":194.0,"n_steps_budget":1000.0,"object_pos_end":[0.52436,-0.02329,0.19262],"object_pos_start":[0.51358,-0.02278,0.02578],"object_to_goal_dist_end":0.17987,"object_to_goal_dist_start":0.26565,"object_z_max":0.19172,"peak_contact_force":0.08121,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7605.0,"raw_peak_contact_force":0.67006,"tcp_end":[0.50928,-0.02266,0.19595],"tcp_start":[0.49976,-0.02234,0.02986],"tcp_to_object_dist_end":0.01545,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":605.0,"n_steps_budget":1000.0,"object_pos_end":[0.56395,0.14319,0.29714],"object_pos_start":[0.52436,-0.02329,0.19262],"object_to_goal_dist_end":0.07626,"object_to_goal_dist_start":0.17987,"object_z_max":0.29699,"peak_contact_force":0.10794,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22412.0,"raw_peak_contact_force":0.12996,"subtask_id":"transport_arc","tcp_end":[0.54893,0.13966,0.30552],"tcp_start":[0.50928,-0.02266,0.19595],"tcp_to_object_dist_end":0.01756,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":123.0,"n_steps_budget":1000.0,"object_pos_end":[0.56502,0.15136,0.22916],"object_pos_start":[0.56395,0.14319,0.29714],"object_to_goal_dist_end":0.01307,"object_to_goal_dist_start":0.07626,"object_z_max":0.2972,"peak_contact_force":0.10833,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3694.0,"raw_peak_contact_force":0.21926,"subtask_id":"release_1","tcp_end":[0.55024,0.14746,0.24102],"tcp_start":[0.54893,0.13966,0.30552],"tcp_to_object_dist_end":0.01935,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93363,"average_solve_count":226.0,"average_success_count":226.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09347,"descend_1.grasp_z_offset":0.005,"lift_1.lift_height":0.2334,"transport_arc.transport_z_offset":0.2824},"optimized_scores":{"best_composite_score":0.65698,"best_fitness_score":0.97698,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":62.0,"contact_point_centroid":[0.49778,0.04434,-0.00156],"force_p95":0.5575,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6558,"mean_force":0.31475,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48622,0.04378,0.03137]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3572.0,"contact_point_centroid":[0.49005,0.06308,0.11601],"force_p95":0.09264,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33606,"mean_force":0.06511,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49027,0.04383,0.11348]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4473.0,"contact_point_centroid":[0.49182,0.02486,0.11566],"force_p95":0.08887,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31292,"mean_force":0.05386,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49032,0.04383,0.11414]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5139.0,"contact_point_centroid":[0.557,0.25766,0.29435],"force_p95":0.11878,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29302,"mean_force":0.08527,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.56043,0.23879,0.29199]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6809.0,"contact_point_centroid":[0.56947,0.22248,0.29377],"force_p95":0.09737,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21142,"mean_force":0.06407,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.56042,0.23874,0.29406]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50123,0.04502,-0.0021],"force_p95":0.15103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20394,"mean_force":0.12997,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48867,0.04402,0.03159]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5031.0,"contact_point_centroid":[0.48927,0.02491,0.03167],"force_p95":0.07506,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17373,"mean_force":0.04316,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48744,0.04391,0.0303]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14589.0,"contact_point_centroid":[0.52469,0.15753,0.31004],"force_p95":0.11165,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15872,"mean_force":0.06573,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52711,0.13855,0.30743]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18002.0,"contact_point_centroid":[0.53295,0.12246,0.31072],"force_p95":0.08858,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15778,"mean_force":0.05343,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52773,0.1403,0.30937]},{"body_a":"world","body_b":"grasp_target","contact_count":1272.0,"contact_point_centroid":[0.50118,0.04505,-0.0019],"force_p95":0.13583,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49807,0.03002,0.22546]},{"body_a":"world","body_b":"grasp_target","contact_count":1284.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49542,0.04508,0.09034]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4198.0,"contact_point_centroid":[0.48759,0.06321,0.03298],"force_p95":0.08612,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09683,"mean_force":0.05189,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48744,0.04391,0.0303]}],"total_contact_groups":12},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.56976,0.24746,0.14637],"final_tcp_position":[0.56086,0.24256,0.16623],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.6558,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":319.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1272.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49763,0.04572,0.14297],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.117,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":321.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1284.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.49597,0.0447,0.0394],"tcp_start":[0.49763,0.04572,0.14297],"tcp_to_object_dist_end":0.01436,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50114,0.04444,0.02566],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24257,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.14993,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11029.0,"raw_peak_contact_force":0.20394,"subtask_id":"grasp_1","tcp_end":[0.48741,0.0439,0.03027],"tcp_start":[0.49597,0.0447,0.0394],"tcp_to_object_dist_end":0.01449,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":207.0,"n_steps_budget":1000.0,"object_pos_end":[0.51259,0.04503,0.206],"object_pos_start":[0.50114,0.04444,0.02566],"object_to_goal_dist_end":0.21477,"object_to_goal_dist_start":0.24257,"object_z_max":0.20509,"peak_contact_force":0.09166,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":8107.0,"raw_peak_contact_force":0.6558,"tcp_end":[0.49725,0.04412,0.20963],"tcp_start":[0.48741,0.0439,0.03027],"tcp_to_object_dist_end":0.01579,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":915.0,"n_steps_budget":1000.0,"object_pos_end":[0.57494,0.24128,0.4015],"object_pos_start":[0.51259,0.04503,0.206],"object_to_goal_dist_end":0.25496,"object_to_goal_dist_start":0.21477,"object_z_max":0.40132,"peak_contact_force":0.11615,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32591.0,"raw_peak_contact_force":0.15872,"subtask_id":"transport_arc","tcp_end":[0.56049,0.23553,0.41194],"tcp_start":[0.49725,0.04412,0.20963],"tcp_to_object_dist_end":0.01874,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":431.0,"n_steps_budget":1000.0,"object_pos_end":[0.56976,0.24746,0.14637],"object_pos_start":[0.57494,0.24128,0.4015],"object_to_goal_dist_end":0.00596,"object_to_goal_dist_start":0.25496,"object_z_max":0.40155,"peak_contact_force":0.14299,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":11948.0,"raw_peak_contact_force":0.29302,"subtask_id":"release_1","tcp_end":[0.56086,0.24256,0.16623],"tcp_start":[0.56049,0.23553,0.41194],"tcp_to_object_dist_end":0.0223,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92105,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13383,"descend_1.grasp_z_offset":0.005,"lift_1.lift_height":0.15242,"transport_arc.transport_z_offset":0.17915},"optimized_scores":{"best_composite_score":0.65768,"best_fitness_score":0.97768,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":59.0,"contact_point_centroid":[0.473,-0.01911,-0.00156],"force_p95":0.53051,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61362,"mean_force":0.31577,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46217,-0.01909,0.0323]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2106.0,"contact_point_centroid":[0.46358,-0.03846,0.07714],"force_p95":0.14537,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30524,"mean_force":0.06638,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46455,-0.01922,0.07452]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2567.0,"contact_point_centroid":[0.46511,-0.00015,0.07606],"force_p95":0.13348,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30365,"mean_force":0.05674,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46455,-0.01922,0.07464]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4080.0,"contact_point_centroid":[0.61501,0.16595,0.27942],"force_p95":0.08757,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21287,"mean_force":0.05893,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.6185,0.14732,0.27626]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47619,-0.02012,-0.00209],"force_p95":0.1498,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20929,"mean_force":0.12947,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46443,-0.01913,0.03246]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4271.0,"contact_point_centroid":[0.62335,0.12896,0.27573],"force_p95":0.08526,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18599,"mean_force":0.05726,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.61864,0.14749,0.27454]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18673.0,"contact_point_centroid":[0.54601,0.04597,0.23854],"force_p95":0.0783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14,"mean_force":0.05489,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.54399,0.06498,0.23647]},{"body_a":"world","body_b":"grasp_target","contact_count":928.0,"contact_point_centroid":[0.47616,-0.02015,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12315,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48828,0.00066,0.24147]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19674.0,"contact_point_centroid":[0.53816,0.07929,0.233],"force_p95":0.07727,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13691,"mean_force":0.0522,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53982,0.06039,0.23042]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5046.0,"contact_point_centroid":[0.4644,-3e-05,0.03282],"force_p95":0.06548,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12977,"mean_force":0.04307,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46323,-0.0191,0.03128]},{"body_a":"world","body_b":"grasp_target","contact_count":1780.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47295,-0.01485,0.10943]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4453.0,"contact_point_centroid":[0.46281,-0.03838,0.03404],"force_p95":0.07678,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08435,"mean_force":0.04907,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46324,-0.0191,0.03129]}],"total_contact_groups":12},"final_pose_error":0.01954,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63709,0.15864,0.19426],"final_tcp_position":[0.62531,0.15512,0.20813],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.61362,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":233.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":928.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47694,-0.01054,0.18092],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1552,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":445.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1780.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47157,-0.01921,0.0396],"tcp_start":[0.47694,-0.01054,0.18092],"tcp_to_object_dist_end":0.01436,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47607,-0.01955,0.02569],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28825,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14839,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11299.0,"raw_peak_contact_force":0.20929,"subtask_id":"grasp_1","tcp_end":[0.4632,-0.0191,0.03125],"tcp_start":[0.47157,-0.01921,0.0396],"tcp_to_object_dist_end":0.01403,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":117.0,"n_steps_budget":930.0,"object_pos_end":[0.48279,-0.01993,0.12383],"object_pos_start":[0.47607,-0.01955,0.02569],"object_to_goal_dist_end":0.24198,"object_to_goal_dist_start":0.28825,"object_z_max":0.12291,"peak_contact_force":0.07998,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4732.0,"raw_peak_contact_force":0.61362,"tcp_end":[0.47014,-0.01939,0.12851],"tcp_start":[0.4632,-0.0191,0.03125],"tcp_to_object_dist_end":0.0135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62647,0.14394,0.32724],"object_pos_start":[0.48279,-0.01993,0.12383],"object_to_goal_dist_end":0.13815,"object_to_goal_dist_start":0.24198,"object_z_max":0.32705,"peak_contact_force":0.08081,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":38347.0,"raw_peak_contact_force":0.14,"subtask_id":"transport_arc","tcp_end":[0.61342,0.1408,0.33688],"tcp_start":[0.47014,-0.01939,0.12851],"tcp_to_object_dist_end":0.01653,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":230.0,"n_steps_budget":1000.0,"object_pos_end":[0.63709,0.15864,0.19426],"object_pos_start":[0.62647,0.14394,0.32724],"object_to_goal_dist_end":0.0071,"object_to_goal_dist_start":0.13815,"object_z_max":0.3273,"peak_contact_force":0.08895,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8351.0,"raw_peak_contact_force":0.21287,"subtask_id":"release_1","tcp_end":[0.62531,0.15512,0.20813],"tcp_start":[0.61342,0.1408,0.33688],"tcp_to_object_dist_end":0.01853,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```