## Search State

- **Seed**: 0
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.6574 | 1.00 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.6573 | 1.00 | ✅ accepted |
| 1 | approach → descend → grasp → lift → approach → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.3238 | 0.34 | ✅ accepted |
| 0 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | admittance_control | position_control | position_control | admittance_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.2704 | 0.17 | ✅ accepted |

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
| approach_1 | 1.00 | 1.00 | 0.0564 |
| descend_1 | 1.00 | 1.00 | 0.2113 |
| grasp_1 | 1.00 | 1.00 | 0.0124 |
| lift_1 | 1.00 | 1.00 | 0.1375 |
| transport_arc | 1.00 | 1.00 | 0.2723 |
| place_1 | 1.00 | 1.00 | 0.1315 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.005, 0.251) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.124 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.005, 0.251)→(0.492, 0.001, 0.040) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.124 |
| grasp_1 | grasp | 1.00 / step_budget | (0.492, 0.001, 0.040)→(0.484, 0.001, 0.031) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 | 1.00 / 43.000 | 0.150 | 0.206 |
| lift_1 | lift | 1.00 / step_budget | (0.484, 0.001, 0.031)→(0.492, 0.000, 0.168) | (0.497, 0.001, 0.026)→(0.506, 0.000, 0.164) | 0.266→0.208 | 1.00 / 38.667 | 0.083 | 0.647 |
| transport_arc | approach | 1.00 / step_budget | (0.492, 0.000, 0.168)→(0.577, 0.176, 0.336) | (0.506, 0.000, 0.164)→(0.587, 0.179, 0.326) | 0.208→0.141 | 1.00 / 37.000 | 0.080 | 0.127 |
| place_1 | descend | 1.00 / step_budget | (0.577, 0.176, 0.336)→(0.579, 0.182, 0.205) | (0.587, 0.179, 0.326)→(0.587, 0.186, 0.190) | 0.141→0.008 | 1.00 / 33.000 | 0.085 | 0.195 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.594
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 1.000
- phase_score: 0.471
- phase_breakdown.release_1_score: 0.672
- phase_breakdown.transport_arc_score: 0.253
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.807
- phase_breakdown.approach_1_score: 0.006
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
- **Final σ (mean)**: 0.328


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93119,"average_solve_count":218.0,"average_success_count":218.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19674,"descend_1.grasp_z_offset":0.00501,"lift_1.lift_height":0.20703,"transport_arc.transport_z_offset":0.23413},"optimized_scores":{"best_composite_score":0.65702,"best_fitness_score":0.97702,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":62.0,"contact_point_centroid":[0.51026,-0.02245,-0.00156],"force_p95":0.57655,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67312,"mean_force":0.31465,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49855,-0.02208,0.03083]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3121.0,"contact_point_centroid":[0.5013,-0.04146,0.10247],"force_p95":0.10084,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33157,"mean_force":0.06565,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50217,-0.02224,0.09979]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3871.0,"contact_point_centroid":[0.50324,-0.00323,0.10303],"force_p95":0.08948,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32412,"mean_force":0.05516,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5023,-0.02224,0.10121]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51373,-0.02303,-0.00208],"force_p95":0.14789,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.2044,"mean_force":0.12913,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.501,-0.02212,0.03115]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5313.0,"contact_point_centroid":[0.5491,0.16588,0.34522],"force_p95":0.09325,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17591,"mean_force":0.06561,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.55119,0.14699,0.34325]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5488.0,"contact_point_centroid":[0.55815,0.12927,0.34219],"force_p95":0.08846,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16875,"mean_force":0.06392,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.55119,0.14705,0.34091]},{"body_a":"world","body_b":"grasp_target","contact_count":488.0,"contact_point_centroid":[0.5137,-0.02302,-0.00174],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12363,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50329,-0.00365,0.27205]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5288.0,"contact_point_centroid":[0.50069,-0.00305,0.03172],"force_p95":0.0653,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12995,"mean_force":0.0412,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49975,-0.0221,0.0298]},{"body_a":"world","body_b":"grasp_target","contact_count":2480.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5067,-0.01727,0.13929]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17203.0,"contact_point_centroid":[0.53268,0.045,0.31484],"force_p95":0.08472,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12117,"mean_force":0.05889,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52942,0.06376,0.31269]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18569.0,"contact_point_centroid":[0.52736,0.07815,0.30774],"force_p95":0.08569,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11834,"mean_force":0.0553,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52821,0.05921,0.30565]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4199.0,"contact_point_centroid":[0.49911,-0.04138,0.03265],"force_p95":0.07882,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08136,"mean_force":0.05178,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49976,-0.0221,0.02981]}],"total_contact_groups":12},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.56031,0.15301,0.22351],"final_tcp_position":[0.55127,0.15003,0.24171],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":0.67312,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":123.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.2656,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12256,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":488.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50747,-0.01234,0.24195],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.21628,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":620.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.2656,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2480.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.50843,-0.02223,0.03925],"tcp_start":[0.50747,-0.01234,0.24195],"tcp_to_object_dist_end":0.01427,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5136,-0.02258,0.0257],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26557,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.14676,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11287.0,"raw_peak_contact_force":0.2044,"subtask_id":"grasp_1","tcp_end":[0.49972,-0.0221,0.02977],"tcp_start":[0.50843,-0.02223,0.03925],"tcp_to_object_dist_end":0.01446,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":180.0,"n_steps_budget":1000.0,"object_pos_end":[0.52385,-0.02309,0.17966],"object_pos_start":[0.5136,-0.02258,0.0257],"object_to_goal_dist_end":0.18232,"object_to_goal_dist_start":0.26557,"object_z_max":0.17875,"peak_contact_force":0.08233,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7054.0,"raw_peak_contact_force":0.67312,"tcp_end":[0.50895,-0.02244,0.18301],"tcp_start":[0.49972,-0.0221,0.02977],"tcp_to_object_dist_end":0.01529,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":34.0,"n_steps":987.0,"n_steps_budget":1000.0,"object_pos_end":[0.5653,0.14766,0.42735],"object_pos_start":[0.52385,-0.02309,0.17966],"object_to_goal_dist_end":0.20571,"object_to_goal_dist_start":0.18232,"object_z_max":0.42714,"peak_contact_force":0.08882,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35772.0,"raw_peak_contact_force":0.12117,"subtask_id":"transport_arc","tcp_end":[0.55143,0.14426,0.438],"tcp_start":[0.50895,-0.02244,0.18301],"tcp_to_object_dist_end":0.01782,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":29.0,"n_steps":352.0,"n_steps_budget":1000.0,"object_pos_end":[0.56031,0.15301,0.22351],"object_pos_start":[0.5653,0.14766,0.42735],"object_to_goal_dist_end":0.00654,"object_to_goal_dist_start":0.20571,"object_z_max":0.42745,"peak_contact_force":0.0942,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10801.0,"raw_peak_contact_force":0.17591,"subtask_id":"release_1","tcp_end":[0.55127,0.15003,0.24171],"tcp_start":[0.55143,0.14426,0.438],"tcp_to_object_dist_end":0.02055,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92063,"average_solve_count":189.0,"average_success_count":189.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17813,"descend_1.grasp_z_offset":0.005,"lift_1.lift_height":0.14847,"transport_arc.transport_z_offset":0.1842},"optimized_scores":{"best_composite_score":0.65717,"best_fitness_score":0.97717,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":64.0,"contact_point_centroid":[0.49799,0.04357,-0.0016],"force_p95":0.54767,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6513,"mean_force":0.28441,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48649,0.0433,0.03146]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2022.0,"contact_point_centroid":[0.48868,0.06256,0.07419],"force_p95":0.14283,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33333,"mean_force":0.06792,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48899,0.04331,0.07174]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2515.0,"contact_point_centroid":[0.49036,0.02431,0.07324],"force_p95":0.11961,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30654,"mean_force":0.05672,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48902,0.04331,0.07194]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50126,0.04497,-0.00215],"force_p95":0.16392,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22794,"mean_force":0.13353,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4889,0.04354,0.03158]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5011.0,"contact_point_centroid":[0.48946,0.02443,0.03165],"force_p95":0.07656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19197,"mean_force":0.04314,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48767,0.04343,0.03029]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3983.0,"contact_point_centroid":[0.55451,0.25647,0.24797],"force_p95":0.09213,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17691,"mean_force":0.06657,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.55937,0.23821,0.24457]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4676.0,"contact_point_centroid":[0.56771,0.22118,0.24433],"force_p95":0.08972,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15637,"mean_force":0.05983,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.55937,0.2382,0.2447]},{"body_a":"world","body_b":"grasp_target","contact_count":664.0,"contact_point_centroid":[0.50118,0.04505,-0.00181],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12336,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49886,0.02132,0.2663]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18571.0,"contact_point_centroid":[0.53073,0.12238,0.22049],"force_p95":0.08022,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12742,"mean_force":0.0507,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52596,0.14075,0.21924]},{"body_a":"world","body_b":"grasp_target","contact_count":2300.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49605,0.04152,0.13169]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15334.0,"contact_point_centroid":[0.52326,0.16119,0.22447],"force_p95":0.08359,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11456,"mean_force":0.05889,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.52657,0.14249,0.22099]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4235.0,"contact_point_centroid":[0.48774,0.06275,0.03291],"force_p95":0.0851,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09383,"mean_force":0.05189,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48768,0.04343,0.03029]}],"total_contact_groups":12},"final_pose_error":0.01953,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.57118,0.24754,0.15066],"final_tcp_position":[0.56046,0.242,0.16569],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":0.6513,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":167.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":664.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.49843,0.03904,0.22649],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20058,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":575.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2300.0,"raw_peak_contact_force":0.12264,"subtask_id":"descend_1","tcp_end":[0.49621,0.04419,0.03939],"tcp_start":[0.49843,0.03904,0.22649],"tcp_to_object_dist_end":0.01429,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50118,0.04404,0.0255],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24298,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.16093,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11046.0,"raw_peak_contact_force":0.22794,"subtask_id":"grasp_1","tcp_end":[0.48764,0.04342,0.03025],"tcp_start":[0.49621,0.04419,0.03939],"tcp_to_object_dist_end":0.01436,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":116.0,"n_steps_budget":900.0,"object_pos_end":[0.50846,0.04431,0.12098],"object_pos_start":[0.50118,0.04404,0.0255],"object_to_goal_dist_end":0.2098,"object_to_goal_dist_start":0.24298,"object_z_max":0.12008,"peak_contact_force":0.08694,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4601.0,"raw_peak_contact_force":0.6513,"tcp_end":[0.49483,0.04357,0.12505],"tcp_start":[0.48764,0.04342,0.03025],"tcp_to_object_dist_end":0.01424,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":902.0,"n_steps_budget":1000.0,"object_pos_end":[0.57194,0.24059,0.30477],"object_pos_start":[0.50846,0.04431,0.12098],"object_to_goal_dist_end":0.15823,"object_to_goal_dist_start":0.2098,"object_z_max":0.3046,"peak_contact_force":0.08123,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33905.0,"raw_peak_contact_force":0.12742,"subtask_id":"transport_arc","tcp_end":[0.55935,0.23521,0.3144],"tcp_start":[0.49483,0.04357,0.12505],"tcp_to_object_dist_end":0.01674,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":265.0,"n_steps_budget":1000.0,"object_pos_end":[0.57118,0.24754,0.15066],"object_pos_start":[0.57194,0.24059,0.30477],"object_to_goal_dist_end":0.00824,"object_to_goal_dist_start":0.15823,"object_z_max":0.30483,"peak_contact_force":0.09102,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8659.0,"raw_peak_contact_force":0.17691,"subtask_id":"release_1","tcp_end":[0.56046,0.242,0.16569],"tcp_start":[0.55935,0.23521,0.3144],"tcp_to_object_dist_end":0.01927,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81383,"average_solve_count":188.0,"average_success_count":188.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.23917,"descend_1.grasp_z_offset":0.00516,"lift_1.lift_height":0.21874,"transport_arc.transport_z_offset":0.07916},"optimized_scores":{"best_composite_score":0.65813,"best_fitness_score":0.97813,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":60.0,"contact_point_centroid":[0.47335,-0.01957,-0.00151],"force_p95":0.55341,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61519,"mean_force":0.27626,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46252,-0.0194,0.03282]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3345.0,"contact_point_centroid":[0.46514,-0.03877,0.10984],"force_p95":0.08475,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30754,"mean_force":0.06294,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46594,-0.01954,0.10723]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4063.0,"contact_point_centroid":[0.46676,-0.00051,0.10894],"force_p95":0.08104,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30569,"mean_force":0.0539,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46595,-0.01954,0.10735]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1860.0,"contact_point_centroid":[0.61772,0.1701,0.23727],"force_p95":0.07234,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23281,"mean_force":0.05093,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.62205,0.1516,0.23437]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02016,-0.00206],"force_p95":0.14184,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18528,"mean_force":0.12734,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46492,-0.01944,0.03296]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1860.0,"contact_point_centroid":[0.62593,0.13276,0.23524],"force_p95":0.07205,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17935,"mean_force":0.05108,"phase_index":5.0,"phase_name":"place_1","phase_type":"descend","tcp_position_centroid":[0.62205,0.1516,0.23437]},{"body_a":"world","body_b":"grasp_target","contact_count":216.0,"contact_point_centroid":[0.47616,-0.02015,-0.0014],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12481,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49341,-0.00457,0.29336]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13146.0,"contact_point_centroid":[0.5521,0.05106,0.22853],"force_p95":0.0809,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13152,"mean_force":0.05495,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.55,0.07013,0.22663]},{"body_a":"world","body_b":"grasp_target","contact_count":2980.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12566,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47799,-0.01499,0.16039]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14658.0,"contact_point_centroid":[0.54408,0.08434,0.22735],"force_p95":0.07356,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12157,"mean_force":0.04958,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"approach","tcp_position_centroid":[0.5459,0.06549,0.2249]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5298.0,"contact_point_centroid":[0.46441,-0.00032,0.03332],"force_p95":0.06557,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11065,"mean_force":0.04122,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46372,-0.01941,0.03178]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4424.0,"contact_point_centroid":[0.46319,-0.03869,0.0345],"force_p95":0.07787,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08696,"mean_force":0.04919,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46373,-0.01941,0.03178]}],"total_contact_groups":12},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.62819,0.15612,0.1968],"final_tcp_position":[0.62477,0.15472,0.20816],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.61519,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":55.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02586],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28847,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12598,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":216.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.48602,-0.01047,0.28342],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.25793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":745.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02586],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28847,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2980.0,"raw_peak_contact_force":0.12566,"subtask_id":"descend_1","tcp_end":[0.47208,-0.01953,0.04012],"tcp_start":[0.48602,-0.01047,0.28342],"tcp_to_object_dist_end":0.0147,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47605,-0.01982,0.02578],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28837,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14147,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11522.0,"raw_peak_contact_force":0.18528,"subtask_id":"grasp_1","tcp_end":[0.46369,-0.01941,0.03175],"tcp_start":[0.47208,-0.01953,0.04012],"tcp_to_object_dist_end":0.01373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":188.0,"n_steps_budget":1000.0,"object_pos_end":[0.48675,-0.02032,0.19027],"object_pos_start":[0.47605,-0.01982,0.02578],"object_to_goal_dist_end":0.23056,"object_to_goal_dist_start":0.28837,"object_z_max":0.18936,"peak_contact_force":0.08085,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":7468.0,"raw_peak_contact_force":0.61519,"tcp_end":[0.47229,-0.01971,0.19555],"tcp_start":[0.46369,-0.01941,0.03175],"tcp_to_object_dist_end":0.0154,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":706.0,"n_steps_budget":1000.0,"object_pos_end":[0.62248,0.14967,0.24624],"object_pos_start":[0.48675,-0.02032,0.19027],"object_to_goal_dist_end":0.05772,"object_to_goal_dist_start":0.23056,"object_z_max":0.24618,"peak_contact_force":0.07022,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":27804.0,"raw_peak_contact_force":0.13152,"subtask_id":"transport_arc","tcp_end":[0.62002,0.14867,0.25686],"tcp_start":[0.47229,-0.01971,0.19555],"tcp_to_object_dist_end":0.01095,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":93.0,"n_steps_budget":1000.0,"object_pos_end":[0.62819,0.15612,0.1968],"object_pos_start":[0.62248,0.14967,0.24624],"object_to_goal_dist_end":0.00812,"object_to_goal_dist_start":0.05772,"object_z_max":0.24624,"peak_contact_force":0.0704,"phase_name":"place_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3720.0,"raw_peak_contact_force":0.23281,"subtask_id":"release_1","tcp_end":[0.62477,0.15472,0.20816],"tcp_start":[0.62002,0.14867,0.25686],"tcp_to_object_dist_end":0.01194,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```