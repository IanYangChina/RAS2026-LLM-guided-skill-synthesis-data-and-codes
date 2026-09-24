## Search State

- **Seed**: 0
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.6369 | 1.00 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.6073 | 1.00 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.6571 | 1.00 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.6572 | 1.00 | ❌ rejected |
| 8 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.6573 | 1.00 | ❌ rejected |

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

## Current Skill (Q=0.637) — your mutation base

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

- **Composite score**: 0.637
- **task_score** (E): 1.000
- **fitness_score**: 0.957  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.320

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0993 |
| descend_1 | 1.00 | 1.00 | 0.1443 |
| grasp_1 | 1.00 | 1.00 | 0.0143 |
| lift_1 | 1.00 | 1.00 | 0.1419 |
| transport_arc | 1.00 | 1.00 | 0.2326 |
| place_1 | 1.00 | 1.00 | 0.1021 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.499, 0.004, 0.204) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.125 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.499, 0.004, 0.204)→(0.494, 0.002, 0.061) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 19.588 | 0.125 |
| grasp_1 | grasp | 1.00 / step_budget | (0.494, 0.002, 0.061)→(0.484, 0.002, 0.050) | (0.497, 0.001, 0.026)→(0.497, 0.002, 0.025) | 0.265→0.266 | 1.00 / 37.000 | 0.207 | 0.263 |
| lift_1 | lift | 1.00 / step_budget | (0.484, 0.002, 0.050)→(0.493, 0.002, 0.192) | (0.497, 0.002, 0.025)→(0.507, 0.001, 0.166) | 0.266→0.212 | 1.00 / 30.667 | 0.132 | 0.428 |
| transport_arc | approach | 1.00 / step_budget | (0.493, 0.002, 0.192)→(0.568, 0.155, 0.333) | (0.507, 0.001, 0.166)→(0.583, 0.159, 0.305) | 0.212→0.122 | 1.00 / 19.000 | 0.137 | 0.246 |
| place_1 | descend | 1.00 / step_budget | (0.568, 0.155, 0.333)→(0.577, 0.174, 0.234) | (0.583, 0.159, 0.305)→(0.589, 0.178, 0.202) | 0.122→0.018 | 1.00 / 16.333 | 0.134 | 0.480 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.144
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.305
- phase_breakdown.release_1_score: 0.375
- phase_breakdown.transport_arc_score: 0.033
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.794
- phase_breakdown.approach_1_score: 0.009
- grasp_place_fitness: 0.958

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.958
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.638
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.573


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.925,"average_solve_count":200.0,"average_success_count":200.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05181,"descend_1.grasp_z_offset":0.00656,"lift_1.lift_height":0.18374,"transport_arc.transport_z_offset":0.20524},"optimized_scores":{"best_composite_score":0.63566,"best_fitness_score":0.95566,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":871.0,"contact_point_centroid":[0.55207,0.15521,0.32828],"force_p95":0.18437,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44141,"mean_force":0.12626,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.55041,0.1362,0.33026]},{"body_a":"world","body_b":"grasp_target","contact_count":69.0,"contact_point_centroid":[0.51173,-0.01848,-0.00208],"force_p95":0.33672,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43827,"mean_force":0.1386,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49798,-0.01718,0.05125]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1636.0,"contact_point_centroid":[0.50426,0.00117,0.09585],"force_p95":0.17131,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34326,"mean_force":0.095,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50136,-0.01782,0.09787]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1087.0,"contact_point_centroid":[0.55885,0.11908,0.33412],"force_p95":0.19629,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29813,"mean_force":0.10935,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.55025,0.13558,0.33533]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51388,-0.02277,-0.00243],"force_p95":0.24264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29004,"mean_force":0.15291,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50043,-0.01718,0.05099]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2482.0,"contact_point_centroid":[0.50228,-0.03627,0.09981],"force_p95":0.12618,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28841,"mean_force":0.07012,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50152,-0.01785,0.09938]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2947.0,"contact_point_centroid":[0.52667,0.06579,0.25544],"force_p95":0.14923,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23351,"mean_force":0.10548,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52526,0.04676,0.2582]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5011.0,"contact_point_centroid":[0.52862,0.0291,0.25814],"force_p95":0.13677,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22737,"mean_force":0.07069,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52528,0.04687,0.25834]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3002.0,"contact_point_centroid":[0.50233,0.0018,0.04781],"force_p95":0.11487,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16834,"mean_force":0.07228,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49927,-0.01716,0.04972]},{"body_a":"world","body_b":"grasp_target","contact_count":652.0,"contact_point_centroid":[0.5137,-0.02302,-0.0018],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12338,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50467,0.00423,0.21815]},{"body_a":"world","body_b":"grasp_target","contact_count":364.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50792,-0.01151,0.09396]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5027.0,"contact_point_centroid":[0.50003,-0.03629,0.05021],"force_p95":0.0863,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09061,"mean_force":0.04432,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49929,-0.01716,0.04974]}],"total_contact_groups":12},"final_pose_error":0.0499,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.56242,0.14492,0.23802],"final_tcp_position":[0.55209,0.14365,0.2712],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":0.44141,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":164.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":652.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.5093,-0.00603,0.12768],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10316,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":91.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":364.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.50876,-0.01706,0.06093],"tcp_start":[0.5093,-0.00603,0.12768],"tcp_to_object_dist_end":0.03576,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51384,-0.01923,0.02438],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26433,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.2393,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9829.0,"raw_peak_contact_force":0.29004,"subtask_id":"grasp_1","tcp_end":[0.49924,-0.01716,0.04969],"tcp_start":[0.50876,-0.01706,0.06093],"tcp_to_object_dist_end":0.02929,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":133.0,"n_steps_budget":990.0,"object_pos_end":[0.52266,-0.02092,0.13325],"object_pos_start":[0.51384,-0.01923,0.02438],"object_to_goal_dist_end":0.19658,"object_to_goal_dist_start":0.26433,"object_z_max":0.13237,"peak_contact_force":0.14256,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4187.0,"raw_peak_contact_force":0.43827,"tcp_end":[0.50791,-0.01865,0.15936],"tcp_start":[0.49924,-0.01716,0.04969],"tcp_to_object_dist_end":0.03007,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":304.0,"n_steps_budget":1000.0,"object_pos_end":[0.56396,0.12939,0.35471],"object_pos_start":[0.52266,-0.02092,0.13325],"object_to_goal_dist_end":0.13493,"object_to_goal_dist_start":0.19658,"object_z_max":0.35399,"peak_contact_force":0.14853,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":7958.0,"raw_peak_contact_force":0.23351,"subtask_id":"transport_arc","tcp_end":[0.5481,0.12818,0.38377],"tcp_start":[0.50791,-0.01865,0.15936],"tcp_to_object_dist_end":0.03313,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":16.0,"n_steps":109.0,"n_steps_budget":1000.0,"object_pos_end":[0.56242,0.14492,0.23802],"object_pos_start":[0.56396,0.12939,0.35471],"object_to_goal_dist_end":0.01927,"object_to_goal_dist_start":0.13493,"object_z_max":0.35607,"peak_contact_force":0.13663,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1958.0,"raw_peak_contact_force":0.44141,"subtask_id":"release_1","tcp_end":[0.55209,0.14365,0.2712],"tcp_start":[0.5481,0.12818,0.38377],"tcp_to_object_dist_end":0.03478,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92386,"average_solve_count":197.0,"average_success_count":197.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18871,"descend_1.grasp_z_offset":0.00523,"lift_1.lift_height":0.21628,"transport_arc.transport_z_offset":0.1994},"optimized_scores":{"best_composite_score":0.63761,"best_fitness_score":0.95761,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":1087.0,"contact_point_centroid":[0.55537,0.24058,0.25754],"force_p95":0.22026,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.48745,"mean_force":0.11957,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.55656,0.22175,0.25736]},{"body_a":"world","body_b":"grasp_target","contact_count":67.0,"contact_point_centroid":[0.49846,0.04177,-0.00186],"force_p95":0.34043,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43599,"mean_force":0.1572,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48697,0.04058,0.0508]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":921.0,"contact_point_centroid":[0.56738,0.20617,0.25614],"force_p95":0.20411,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.38963,"mean_force":0.1298,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.55641,0.22129,0.25993]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2939.0,"contact_point_centroid":[0.4908,0.05994,0.11529],"force_p95":0.11243,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30283,"mean_force":0.07012,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49056,0.04105,0.11439]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2478.0,"contact_point_centroid":[0.49199,0.02216,0.11076],"force_p95":0.14189,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28968,"mean_force":0.07978,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4904,0.04103,0.11232]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50135,0.04488,-0.00233],"force_p95":0.21151,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26117,"mean_force":0.14566,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48941,0.0408,0.05062]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3599.0,"contact_point_centroid":[0.51911,0.13091,0.24217],"force_p95":0.14013,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21838,"mean_force":0.07925,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52028,0.11229,0.24163]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2914.0,"contact_point_centroid":[0.52812,0.1,0.24277],"force_p95":0.15436,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20915,"mean_force":0.09023,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52202,0.11754,0.24543]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3366.0,"contact_point_centroid":[0.49031,0.02177,0.04772],"force_p95":0.10336,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20412,"mean_force":0.06232,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48827,0.0407,0.0494]},{"body_a":"world","body_b":"grasp_target","contact_count":188.0,"contact_point_centroid":[0.50118,0.04505,-0.0013],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12447,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50047,0.00993,0.28567]},{"body_a":"world","body_b":"grasp_target","contact_count":1108.0,"contact_point_centroid":[0.50118,0.04505,-0.002],"force_p95":0.12403,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12823,"mean_force":0.12275,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49855,0.03198,0.1617]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4649.0,"contact_point_centroid":[0.48832,0.05984,0.05053],"force_p95":0.08208,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09159,"mean_force":0.04772,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48828,0.0407,0.04942]}],"total_contact_groups":12},"final_pose_error":0.04902,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.57039,0.24077,0.16229],"final_tcp_position":[0.56007,0.23332,0.19421],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.48745,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":48.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.0259],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24195,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12867,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":188.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50082,0.02266,0.26333],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23849,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":277.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.0259],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24195,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1108.0,"raw_peak_contact_force":0.12823,"subtask_id":"descend_1","tcp_end":[0.49771,0.04139,0.06035],"tcp_start":[0.50082,0.02266,0.26333],"tcp_to_object_dist_end":0.0347,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50142,0.04243,0.02487],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24456,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.20452,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9815.0,"raw_peak_contact_force":0.26117,"subtask_id":"grasp_1","tcp_end":[0.48824,0.04069,0.04937],"tcp_start":[0.49771,0.04139,0.06035],"tcp_to_object_dist_end":0.02787,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":167.0,"n_steps_budget":1000.0,"object_pos_end":[0.51174,0.04384,0.16673],"object_pos_start":[0.50142,0.04243,0.02487],"object_to_goal_dist_end":0.20877,"object_to_goal_dist_start":0.24456,"object_z_max":0.16583,"peak_contact_force":0.13274,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5484.0,"raw_peak_contact_force":0.43599,"tcp_end":[0.4969,0.04181,0.19143],"tcp_start":[0.48824,0.04069,0.04937],"tcp_to_object_dist_end":0.02889,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":240.0,"n_steps_budget":1000.0,"object_pos_end":[0.56763,0.21723,0.28497],"object_pos_start":[0.51174,0.04384,0.16673],"object_to_goal_dist_end":0.14097,"object_to_goal_dist_start":0.20877,"object_z_max":0.28447,"peak_contact_force":0.13437,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":6513.0,"raw_peak_contact_force":0.21838,"subtask_id":"transport_arc","tcp_end":[0.55277,0.21005,0.31272],"tcp_start":[0.4969,0.04181,0.19143],"tcp_to_object_dist_end":0.03228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":114.0,"n_steps_budget":1000.0,"object_pos_end":[0.57039,0.24077,0.16229],"object_pos_start":[0.56763,0.21723,0.28497],"object_to_goal_dist_end":0.01712,"object_to_goal_dist_start":0.14097,"object_z_max":0.28578,"peak_contact_force":0.12898,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2008.0,"raw_peak_contact_force":0.48745,"subtask_id":"release_1","tcp_end":[0.56007,0.23332,0.19421],"tcp_start":[0.55277,0.21005,0.31272],"tcp_to_object_dist_end":0.03437,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92228,"average_solve_count":193.0,"average_success_count":193.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14493,"descend_1.grasp_z_offset":0.00525,"lift_1.lift_height":0.24841,"transport_arc.transport_z_offset":0.14004},"optimized_scores":{"best_composite_score":0.63757,"best_fitness_score":0.95757,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"right_finger","body_b":"grasp_target","contact_count":581.0,"contact_point_centroid":[0.61203,0.15467,0.27459],"force_p95":0.22139,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.51254,"mean_force":0.13776,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.61087,0.13591,0.27636]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":604.0,"contact_point_centroid":[0.61893,0.11914,0.27344],"force_p95":0.23053,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.50473,"mean_force":0.13274,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.61083,0.13587,0.27651]},{"body_a":"world","body_b":"grasp_target","contact_count":65.0,"contact_point_centroid":[0.47373,-0.01833,-0.00172],"force_p95":0.36218,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41008,"mean_force":0.15068,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46396,-0.01738,0.05218]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3273.0,"contact_point_centroid":[0.4673,-0.0368,0.12958],"force_p95":0.10599,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30419,"mean_force":0.07138,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4672,-0.01782,0.13002]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3294.0,"contact_point_centroid":[0.53404,0.02703,0.25689],"force_p95":0.18719,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28554,"mean_force":0.08417,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53041,0.04518,0.2583]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2463.0,"contact_point_centroid":[0.53296,0.06475,0.25668],"force_p95":0.19977,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26495,"mean_force":0.10162,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.53124,0.04611,0.25892]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3167.0,"contact_point_centroid":[0.46844,0.0011,0.13246],"force_p95":0.11149,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26102,"mean_force":0.07232,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46748,-0.01784,0.13412]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47625,-0.0201,-0.00222],"force_p95":0.18292,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.23691,"mean_force":0.13846,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46642,-0.0174,0.05199]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3901.0,"contact_point_centroid":[0.46589,0.00163,0.04922],"force_p95":0.08432,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1619,"mean_force":0.05455,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4653,-0.01738,0.05087]},{"body_a":"world","body_b":"grasp_target","contact_count":312.0,"contact_point_centroid":[0.47616,-0.02015,-0.0016],"force_p95":0.13827,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12438,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49369,-0.0002,0.26518]},{"body_a":"world","body_b":"grasp_target","contact_count":880.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12256,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47925,-0.01142,0.14118]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4340.0,"contact_point_centroid":[0.46513,-0.03656,0.05079],"force_p95":0.08143,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08395,"mean_force":0.05098,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46531,-0.01738,0.05088]}],"total_contact_groups":12},"final_pose_error":0.04971,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63342,0.14915,0.20538],"final_tcp_position":[0.61915,0.14535,0.23615],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":58.51894,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":79.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02595],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28842,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12221,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":312.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48554,-0.00542,0.22168],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.19651,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":220.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02595],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28842,"object_z_max":0.02602,"peak_contact_force":58.51894,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":880.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.47449,-0.01742,0.06098],"tcp_start":[0.48554,-0.00542,0.22168],"tcp_to_object_dist_end":0.03511,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4762,-0.0186,0.02521],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28786,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.17847,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10041.0,"raw_peak_contact_force":0.23691,"subtask_id":"grasp_1","tcp_end":[0.46527,-0.01738,0.05084],"tcp_start":[0.47449,-0.01742,0.06098],"tcp_to_object_dist_end":0.0279,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":198.0,"n_steps_budget":1000.0,"object_pos_end":[0.48767,-0.01955,0.19831],"object_pos_start":[0.4762,-0.0186,0.02521],"object_to_goal_dist_end":0.22952,"object_to_goal_dist_start":0.28786,"object_z_max":0.19741,"peak_contact_force":0.12028,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6505.0,"raw_peak_contact_force":0.41008,"tcp_end":[0.47306,-0.01834,0.22393],"tcp_start":[0.46527,-0.01738,0.05084],"tcp_to_object_dist_end":0.02952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":234.0,"n_steps_budget":1000.0,"object_pos_end":[0.61782,0.13038,0.27429],"object_pos_start":[0.48767,-0.01955,0.19831],"object_to_goal_dist_end":0.0901,"object_to_goal_dist_start":0.22952,"object_z_max":0.27398,"peak_contact_force":0.12843,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5757.0,"raw_peak_contact_force":0.28554,"subtask_id":"transport_arc","tcp_end":[0.6038,0.12782,0.30388],"tcp_start":[0.47306,-0.01834,0.22393],"tcp_to_object_dist_end":0.03284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":71.0,"n_steps_budget":1000.0,"object_pos_end":[0.63342,0.14915,0.20538],"object_pos_start":[0.61782,0.13038,0.27429],"object_to_goal_dist_end":0.01846,"object_to_goal_dist_start":0.0901,"object_z_max":0.27475,"peak_contact_force":0.13768,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1185.0,"raw_peak_contact_force":0.51254,"subtask_id":"release_1","tcp_end":[0.61915,0.14535,0.23615],"tcp_start":[0.6038,0.12782,0.30388],"tcp_to_object_dist_end":0.03413,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```