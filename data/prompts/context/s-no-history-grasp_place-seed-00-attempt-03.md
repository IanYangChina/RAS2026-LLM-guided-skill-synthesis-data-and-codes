## Search State

- **Seed**: 0
- **Iteration**: 4 / 15

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

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.5136961687321454, -0.02302132862361297, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5540973523936195, 0.15165276355285293, 0.22199053588004086) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=-0.186) — your mutation base

```yaml
skill: grasp_place
phases:
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  parameters:
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
- id: push_1
  type: push
  generator: impedance_motion
  control: position_control
  termination: time_limit
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
- id: insert_2
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0
- id: push_2
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2

```

## Design Metrics

- **Composite score**: -0.186
- **task_score** (E): 0.149
- **fitness_score**: 0.164  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.350

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1490 |
| descend_1 | 0.00 | 1.00 | 0.0592 |
| grasp_1 | 1.00 | 1.00 | 0.0006 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.418, -0.003, 0.177) | (0.497, 0.001, 0.030)→(0.455, -0.000, 0.016) | 0.263→0.287 | 1.00 / 5.000 | 199.984 | 1354.726 |
| descend_1 | descend | 0.00 / step_budget | (0.418, -0.003, 0.177)→(0.470, -0.000, 0.169) | (0.455, -0.000, 0.016)→(0.455, -0.000, 0.016) | 0.287→0.287 | 1.00 / 5.667 | 358.045 | 874.161 |
| grasp_1 | grasp | 1.00 / step_budget | (0.470, -0.000, 0.169)→(0.470, -0.000, 0.169) | (0.455, -0.000, 0.016)→(0.455, -0.000, 0.016) | 0.287→0.287 | 1.00 / 9.000 | 67.456 | 329.141 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.179
- phase_score: 0.097
- phase_breakdown.place_target_score: 0.000
- phase_breakdown.approach_target_score: 0.384
- phase_breakdown.grasp_target_score: 0.066
- grasp_place_fitness: 0.183

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.183
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.179
- **Median Q (composite search score)**: -0.188
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.364


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.5,"average_solve_count":38.0,"average_success_count":38.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12879,"descend_1.descend_offset":0.01523,"descend_place_1.place_offset_z":-0.00508,"lift_1.lift_height":0.21942},"optimized_scores":{"best_composite_score":-0.18804,"best_fitness_score":0.16196,"best_task_score":0.14896},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.63293,-0.00462,-0.00045],"force_p95":208.96297,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1333.55673,"mean_force":202.37241,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40615,-0.00495,0.14561]},{"body_a":"world","body_b":"link6","contact_count":965.0,"contact_point_centroid":[0.65626,-0.00641,-0.00021],"force_p95":368.07885,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":913.63883,"mean_force":295.05163,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45624,-0.01311,0.19262]},{"body_a":"world","body_b":"link5","contact_count":444.0,"contact_point_centroid":[0.63844,0.10902,-0.00013],"force_p95":108.8486,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":441.45274,"mean_force":78.56623,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47741,-0.01494,0.17297]},{"body_a":"world","body_b":"link5","contact_count":27.0,"contact_point_centroid":[0.63847,0.10893,-0.0009],"force_p95":415.69214,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":416.59333,"mean_force":374.53205,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47557,-0.01554,0.17042]},{"body_a":"link5","body_b":"hand","contact_count":278.0,"contact_point_centroid":[0.52018,0.07784,0.12367],"force_p95":162.43947,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":326.02089,"mean_force":76.68336,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47152,-0.0163,0.16784]},{"body_a":"link5","body_b":"hand","contact_count":77.0,"contact_point_centroid":[0.50238,0.07713,0.11176],"force_p95":54.40912,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":64.9083,"mean_force":15.25869,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47745,-0.01482,0.17332]},{"body_a":"grasp_target","body_b":"link7","contact_count":249.0,"contact_point_centroid":[0.49537,-0.02363,0.0407],"force_p95":2.21816,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.67612,"mean_force":0.62343,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38912,-0.00233,0.10196]},{"body_a":"grasp_target","body_b":"hand","contact_count":223.0,"contact_point_centroid":[0.48968,-0.03261,0.0543],"force_p95":2.17152,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.73906,"mean_force":0.59857,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38848,-0.00227,0.09904]},{"body_a":"world","body_b":"grasp_target","contact_count":3438.0,"contact_point_centroid":[0.48201,-0.02727,-0.00262],"force_p95":0.37745,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.363,"mean_force":0.18037,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.42035,-0.00483,0.15839]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.47192,-0.02834,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45681,-0.01319,0.19192]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47192,-0.02834,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47741,-0.01494,0.17298]},{"body_a":"left_finger","body_b":"right_finger","contact_count":353.0,"contact_point_centroid":[0.47951,-0.01471,0.17182],"force_p95":0.01373,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01474,"mean_force":0.01078,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47739,-0.0149,0.17286]},{"body_a":"world","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.53042,0.00228,-0.00304],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37492,-0.00202,0.05135]}],"total_contact_groups":13},"final_pose_error":0.1425,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.47192,-0.02834,0.01602],"final_tcp_position":[0.47724,-0.01494,0.17302],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":1333.55673,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47192,-0.02834,0.01602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.28561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":195.24631,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4815.0,"raw_peak_contact_force":1333.55673,"subtask_id":"approach_target","tcp_end":[0.43328,-0.00985,0.19685],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18583,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":7.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47192,-0.02834,0.01602],"object_pos_start":[0.47192,-0.02834,0.01602],"object_to_goal_dist_end":0.28561,"object_to_goal_dist_start":0.28561,"object_z_max":0.01602,"peak_contact_force":334.81733,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5270.0,"raw_peak_contact_force":913.63883,"subtask_id":"approach_target","tcp_end":[0.47724,-0.01494,0.17302],"tcp_start":[0.43328,-0.00985,0.19685],"tcp_to_object_dist_end":0.15766,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47192,-0.02834,0.01602],"object_pos_start":[0.47192,-0.02834,0.01602],"object_to_goal_dist_end":0.28561,"object_to_goal_dist_start":0.28561,"object_z_max":0.01602,"peak_contact_force":71.01158,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2674.0,"raw_peak_contact_force":441.45274,"subtask_id":"grasp_target","tcp_end":[0.47739,-0.01489,0.17285],"tcp_start":[0.47724,-0.01494,0.17302],"tcp_to_object_dist_end":0.15751,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.4359,"average_solve_count":39.0,"average_success_count":39.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.09662,"descend_1.descend_offset":0.02921,"descend_place_1.place_offset_z":-0.00106,"lift_1.lift_height":0.20306},"optimized_scores":{"best_composite_score":-0.16688,"best_fitness_score":0.18312,"best_task_score":0.17863},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.63143,0.00768,-0.00045],"force_p95":212.34623,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1332.00326,"mean_force":205.42015,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.40141,0.0075,0.14098]},{"body_a":"world","body_b":"link6","contact_count":987.0,"contact_point_centroid":[0.65141,0.02557,-0.00023],"force_p95":374.94132,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":915.87222,"mean_force":298.52286,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45208,0.02251,0.19194]},{"body_a":"world","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.52942,0.00775,-0.00293],"force_p95":20.36186,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":407.23728,"mean_force":20.36186,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37381,0.00253,0.05111]},{"body_a":"world","body_b":"link6","contact_count":441.0,"contact_point_centroid":[0.70066,0.0261,-0.00012],"force_p95":70.93545,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":220.36623,"mean_force":67.49639,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46938,0.02793,0.16101]},{"body_a":"grasp_target","body_b":"link7","contact_count":159.0,"contact_point_centroid":[0.49123,0.0278,0.03814],"force_p95":2.957,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.25491,"mean_force":0.65788,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38413,0.003,0.09211]},{"body_a":"grasp_target","body_b":"hand","contact_count":215.0,"contact_point_centroid":[0.47997,0.02917,0.05499],"force_p95":2.70636,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.47479,"mean_force":0.54914,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38641,0.00319,0.09766]},{"body_a":"world","body_b":"grasp_target","contact_count":3430.0,"contact_point_centroid":[0.46757,0.0488,-0.00251],"force_p95":0.2995,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.28706,"mean_force":0.1676,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.41577,0.00741,0.1538]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.45705,0.0496,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45225,0.02258,0.19171]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45705,0.0496,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46938,0.02793,0.16102]},{"body_a":"left_finger","body_b":"right_finger","contact_count":335.0,"contact_point_centroid":[0.47126,0.02797,0.15963],"force_p95":0.01467,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01129,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46937,0.02797,0.16094]}],"total_contact_groups":10},"final_pose_error":0.11878,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.45705,0.0496,0.01602],"final_tcp_position":[0.46931,0.02792,0.16137],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1332.00326,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45705,0.0496,0.01602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.25837,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":203.38745,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4710.0,"raw_peak_contact_force":1332.00326,"subtask_id":"approach_target","tcp_end":[0.42372,0.01523,0.18738],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17792,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45705,0.0496,0.01602],"object_pos_start":[0.45705,0.0496,0.01602],"object_to_goal_dist_end":0.25837,"object_to_goal_dist_start":0.25837,"object_z_max":0.01602,"peak_contact_force":281.87047,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4987.0,"raw_peak_contact_force":915.87222,"subtask_id":"approach_target","tcp_end":[0.46931,0.02792,0.16137],"tcp_start":[0.42372,0.01523,0.18738],"tcp_to_object_dist_end":0.14747,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45705,0.0496,0.01602],"object_pos_start":[0.45705,0.0496,0.01602],"object_to_goal_dist_end":0.25837,"object_to_goal_dist_start":0.25837,"object_z_max":0.01602,"peak_contact_force":64.71564,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2576.0,"raw_peak_contact_force":220.36623,"subtask_id":"grasp_target","tcp_end":[0.46937,0.02798,0.16094],"tcp_start":[0.46931,0.02792,0.16137],"tcp_to_object_dist_end":0.14704,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.725,"average_solve_count":40.0,"average_success_count":40.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18768,"descend_1.descend_offset":0.04951,"descend_place_1.place_offset_z":-0.01542,"lift_1.lift_height":0.27364},"optimized_scores":{"best_composite_score":-0.20337,"best_fitness_score":0.14663,"best_task_score":0.1201},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.63035,-0.00758,-0.00046],"force_p95":203.85218,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1398.61908,"mean_force":204.75123,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38783,-0.00739,0.12028]},{"body_a":"world","body_b":"link6","contact_count":990.0,"contact_point_centroid":[0.6407,-0.01599,-0.00026],"force_p95":383.69238,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":792.97132,"mean_force":271.71289,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.43468,-0.01518,0.17821]},{"body_a":"world","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.5252,0.00012,-0.00313],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":465.81075,"mean_force":22.18146,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.3712,-0.0035,0.04938]},{"body_a":"world","body_b":"link6","contact_count":450.0,"contact_point_centroid":[0.682,-0.01355,-0.00013],"force_p95":73.74464,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":325.60376,"mean_force":70.17002,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46456,-0.01428,0.17247]},{"body_a":"grasp_target","body_b":"hand","contact_count":39.0,"contact_point_centroid":[0.45509,-0.02169,0.03989],"force_p95":3.6248,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.98669,"mean_force":1.67508,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.38178,-0.00347,0.05174]},{"body_a":"grasp_target","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.48098,-0.00765,0.01028],"force_p95":0.57518,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.80237,"mean_force":0.37192,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.37183,-0.00351,0.05321]},{"body_a":"world","body_b":"grasp_target","contact_count":3933.0,"contact_point_centroid":[0.44074,-0.02111,-0.00215],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.15611,"mean_force":0.13924,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.39999,-0.00684,0.1301]},{"body_a":"world","body_b":"grasp_target","contact_count":4000.0,"contact_point_centroid":[0.4359,-0.02126,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.43497,-0.0152,0.17826]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.4359,-0.02126,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46456,-0.01428,0.17247]},{"body_a":"left_finger","body_b":"right_finger","contact_count":343.0,"contact_point_centroid":[0.46642,-0.01439,0.17094],"force_p95":0.01382,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01105,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46455,-0.0143,0.17234]}],"total_contact_groups":10},"final_pose_error":0.112,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.4359,-0.02126,0.01602],"final_tcp_position":[0.46463,-0.01407,0.17354],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1398.61908,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4359,-0.02126,0.01602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.31791,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":201.31824,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4908.0,"raw_peak_contact_force":1398.61908,"subtask_id":"approach_target","tcp_end":[0.39586,-0.01331,0.14767],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13784,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4359,-0.02126,0.01602],"object_pos_start":[0.4359,-0.02126,0.01602],"object_to_goal_dist_end":0.31791,"object_to_goal_dist_start":0.31791,"object_z_max":0.01602,"peak_contact_force":457.44856,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4990.0,"raw_peak_contact_force":792.97132,"subtask_id":"approach_target","tcp_end":[0.46463,-0.01407,0.17354],"tcp_start":[0.39586,-0.01331,0.14767],"tcp_to_object_dist_end":0.16028,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4359,-0.02126,0.01602],"object_pos_start":[0.4359,-0.02126,0.01602],"object_to_goal_dist_end":0.31791,"object_to_goal_dist_start":0.31791,"object_z_max":0.01602,"peak_contact_force":66.63968,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2593.0,"raw_peak_contact_force":325.60376,"subtask_id":"grasp_target","tcp_end":[0.46455,-0.01431,0.17233],"tcp_start":[0.46463,-0.01407,0.17354],"tcp_to_object_dist_end":0.15907,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```