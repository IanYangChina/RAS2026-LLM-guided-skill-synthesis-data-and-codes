## Search State

- **Seed**: 1
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.3438 | 0.34 | ✅ accepted |

**Proposal policy**: task_score is 0.34 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`
- Frozen object start: [0.5011821624700257, 0.045046369632593536, 0.03]
- Frozen task target: [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]
- Goal object position: (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5011821624700257, 0.045046369632593536, 0.03)
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
  frozen_object_start: [0.5012, 0.045, 0.03]
  frozen_task_target: [0.5644, 0.2449, 0.1468]
  frozen_object_starts: {'grasp_target': [0.5011821624700257, 0.045046369632593536, 0.03]}
  frozen_targets: {'place_target': [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb

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

## Current Skill (Q=0.344) — your mutation base

```yaml
skill: grasp_place
skill_type: arm_gripper
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  parameters:
    depth:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: grasp_1
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  parameters:
    grip_force:
      type: scalar
      range:
      - 5.0
      - 30.0
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: release_1
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open

```

## Design Metrics

- **Composite score**: 0.344
- **task_score** (E): 0.342
- **fitness_score**: 0.634  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.290

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1333 |
| descend_1 | 1.00 | 1.00 | 0.1192 |
| grasp_1 | 1.00 | 1.00 | 0.0118 |
| lift_1 | 0.00 | 1.00 | 0.1011 |
| release_1 | 0.00 | 1.00 | 0.1649 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.477, -0.001, 0.174) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.477, -0.001, 0.174)→(0.474, -0.001, 0.055) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.001, 0.055)→(0.466, -0.001, 0.046) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 45.333 | 0.146 | 0.187 |
| lift_1 | lift | 0.00 / step_budget | (0.466, -0.001, 0.046)→(0.469, -0.001, 0.147) | (0.479, -0.001, 0.026)→(0.475, -0.001, 0.121) | 0.278→0.252 | 1.00 / 38.000 | 0.080 | 0.378 |
| release_1 | release | 0.00 / step_budget | (0.469, -0.001, 0.147)→(0.553, 0.135, 0.170) | (0.475, -0.001, 0.121)→(0.545, 0.139, 0.023) | 0.252→0.163 | 1.00 / 3.667 | 0.143 | 1.390 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.425
- phase_score: 0.289
- phase_breakdown.descend_1_score: 0.872
- phase_breakdown.transport_arc_score: 0.000
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.334
- phase_breakdown.approach_1_score: 0.029
- grasp_place_fitness: 0.675

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.675
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.425
- **Median Q (composite search score)**: 0.325
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.181


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8110053be9072e64e15984c6424e4a66fe19af4b6c37a60139a43e94cc34ad53`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `46ef03f7b16015a0d14bf26d80c05d326b92c02b0bf759391930f5ab902d1933`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90152,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19976,"descend_1.depth":0.05764,"grasp_1.grip_force":13.93313,"lift_1.speed":0.07241},"optimized_scores":{"best_composite_score":0.38531,"best_fitness_score":0.67531,"best_task_score":0.42461},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":231.0,"contact_point_centroid":[0.53337,0.21111,-0.00537],"force_p95":0.97578,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.37221,"mean_force":0.3008,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54256,0.20044,0.15903]},{"body_a":"world","body_b":"grasp_target","contact_count":172.0,"contact_point_centroid":[0.49767,0.04226,-0.00128],"force_p95":0.25564,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43836,"mean_force":0.07868,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48647,0.04322,0.04718]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15920.0,"contact_point_centroid":[0.51286,0.13447,0.15243],"force_p95":0.10668,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30569,"mean_force":0.06146,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51533,0.11578,0.15187]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19905.0,"contact_point_centroid":[0.48792,0.06242,0.1049],"force_p95":0.07574,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27637,"mean_force":0.0508,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48834,0.04329,0.10239]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20321.0,"contact_point_centroid":[0.48992,0.0242,0.10324],"force_p95":0.07906,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26874,"mean_force":0.05019,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48832,0.04329,0.10225]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16301.0,"contact_point_centroid":[0.51918,0.09845,0.15003],"force_p95":0.10365,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24366,"mean_force":0.06266,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51572,0.11687,0.15176]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04506,-0.00214],"force_p95":0.16068,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21209,"mean_force":0.1329,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48912,0.04348,0.0468]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4856.0,"contact_point_centroid":[0.49006,0.02425,0.04647],"force_p95":0.07631,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16487,"mean_force":0.04535,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48793,0.04337,0.0455]},{"body_a":"world","body_b":"grasp_target","contact_count":1276.0,"contact_point_centroid":[0.50118,0.04505,-0.0019],"force_p95":0.13575,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12301,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49796,0.01882,0.25353]},{"body_a":"world","body_b":"grasp_target","contact_count":1884.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49572,0.04149,0.13016]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5026.0,"contact_point_centroid":[0.48739,0.06259,0.049],"force_p95":0.07509,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08234,"mean_force":0.04399,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48793,0.04337,0.04551]}],"total_contact_groups":11},"final_pose_error":0.04732,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.53335,0.21064,0.02689],"final_tcp_position":[0.54568,0.20155,0.14326],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.37221,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":320.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1276.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.49768,0.0391,0.20685],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.18096,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":471.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1884.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49625,0.04411,0.05464],"tcp_start":[0.49768,0.0391,0.20685],"tcp_to_object_dist_end":0.02906,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50122,0.04422,0.0255],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24282,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15955,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11682.0,"raw_peak_contact_force":0.21209,"tcp_end":[0.4879,0.04337,0.04547],"tcp_start":[0.49625,0.04411,0.05464],"tcp_to_object_dist_end":0.02402,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49933,0.04452,0.13781],"object_pos_start":[0.50122,0.04422,0.0255],"object_to_goal_dist_end":0.21085,"object_to_goal_dist_start":0.24282,"object_z_max":0.13771,"peak_contact_force":0.07882,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40398.0,"raw_peak_contact_force":0.43836,"tcp_end":[0.49322,0.04361,0.1639],"tcp_start":[0.4879,0.04337,0.04547],"tcp_to_object_dist_end":0.02682,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53335,0.21064,0.02689],"object_pos_start":[0.49933,0.04452,0.13781],"object_to_goal_dist_end":0.12849,"object_to_goal_dist_start":0.21085,"object_z_max":0.13784,"peak_contact_force":0.2054,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":32452.0,"raw_peak_contact_force":1.37221,"tcp_end":[0.54247,0.20037,0.17023],"tcp_start":[0.49322,0.04361,0.1639],"tcp_to_object_dist_end":0.144,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1efc3ad2e58ea1c47cd56203c4986b53dab7b80d759e458b85d233ccc9cc04bd`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62879,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15389,"descend_1.depth":0.02104,"grasp_1.grip_force":11.76759,"lift_1.speed":0.05735},"optimized_scores":{"best_composite_score":0.32132,"best_fitness_score":0.61132,"best_task_score":0.29689},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":259.0,"contact_point_centroid":[0.56612,0.1142,-0.00531],"force_p95":1.00244,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.51782,"mean_force":0.2745,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57148,0.10039,0.18414]},{"body_a":"world","body_b":"grasp_target","contact_count":173.0,"contact_point_centroid":[0.47191,-0.0191,-0.00114],"force_p95":0.23591,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36504,"mean_force":0.07218,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46192,-0.01967,0.0479]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":14886.0,"contact_point_centroid":[0.51218,0.05337,0.14935],"force_p95":0.10289,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26548,"mean_force":0.06635,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51302,0.03449,0.15037]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20178.0,"contact_point_centroid":[0.46293,-0.03887,0.09507],"force_p95":0.07178,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24299,"mean_force":0.04965,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46279,-0.01971,0.0929]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20489.0,"contact_point_centroid":[0.46396,-0.00059,0.09315],"force_p95":0.07284,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23761,"mean_force":0.04949,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46275,-0.01971,0.09217]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16214.0,"contact_point_centroid":[0.51655,0.01823,0.14985],"force_p95":0.09707,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21417,"mean_force":0.06137,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51527,0.03693,0.15098]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02022,-0.00204],"force_p95":0.1369,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17007,"mean_force":0.12623,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46452,-0.01971,0.04749]},{"body_a":"world","body_b":"grasp_target","contact_count":1644.0,"contact_point_centroid":[0.47616,-0.02015,-0.00192],"force_p95":0.13462,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12292,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48687,-0.00871,0.23241]},{"body_a":"world","body_b":"grasp_target","contact_count":1380.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47195,-0.0189,0.1087]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5095.0,"contact_point_centroid":[0.46488,-0.00052,0.0476],"force_p95":0.06738,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09713,"mean_force":0.04336,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46336,-0.01969,0.04631]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4882.0,"contact_point_centroid":[0.46354,-0.03893,0.0492],"force_p95":0.07128,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08502,"mean_force":0.04465,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46336,-0.01969,0.04631]}],"total_contact_groups":11},"final_pose_error":0.08459,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.56753,0.11188,0.02612],"final_tcp_position":[0.57454,0.10094,0.16706],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.51782,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":412.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1644.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.47491,-0.01804,0.16358],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13758,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":345.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1380.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47148,-0.01983,0.05464],"tcp_start":[0.47491,-0.01804,0.16358],"tcp_to_object_dist_end":0.02901,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47609,-0.02007,0.02582],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28848,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13695,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11777.0,"raw_peak_contact_force":0.17007,"tcp_end":[0.46333,-0.01969,0.04628],"tcp_start":[0.47148,-0.01983,0.05464],"tcp_to_object_dist_end":0.02411,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47201,-0.02034,0.11475],"object_pos_start":[0.47609,-0.02007,0.02582],"object_to_goal_dist_end":0.25161,"object_to_goal_dist_start":0.28848,"object_z_max":0.11466,"peak_contact_force":0.07504,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40840.0,"raw_peak_contact_force":0.36504,"tcp_end":[0.46639,-0.01981,0.14103],"tcp_start":[0.46333,-0.01969,0.04628],"tcp_to_object_dist_end":0.02689,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56753,0.11188,0.02612],"object_pos_start":[0.47201,-0.02034,0.11475],"object_to_goal_dist_end":0.18216,"object_to_goal_dist_start":0.25161,"object_z_max":0.13362,"peak_contact_force":0.10182,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":31359.0,"raw_peak_contact_force":1.51782,"tcp_end":[0.57139,0.10035,0.19387],"tcp_start":[0.46639,-0.01981,0.14103],"tcp_to_object_dist_end":0.16819,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `37495cb43897015e78e007c86af160d11c8460c1ce7249e5c03dce38206c0daf`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55034,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14125,"descend_1.depth":0.02724,"grasp_1.grip_force":21.30224,"lift_1.speed":0.0375},"optimized_scores":{"best_composite_score":0.32479,"best_fitness_score":0.61479,"best_task_score":0.30477},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":732.0,"contact_point_centroid":[0.53479,0.09363,-0.00282],"force_p95":0.48253,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.28122,"mean_force":0.16484,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54469,0.10529,0.1244]},{"body_a":"world","body_b":"grasp_target","contact_count":169.0,"contact_point_centroid":[0.45447,-0.02521,-0.00117],"force_p95":0.26492,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33132,"mean_force":0.076,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44474,-0.0256,0.04834]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13493.0,"contact_point_centroid":[0.48898,0.0114,0.12457],"force_p95":0.09696,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23603,"mean_force":0.0659,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.48826,0.02992,0.12623]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11508.0,"contact_point_centroid":[0.48576,0.04619,0.12483],"force_p95":0.11445,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22209,"mean_force":0.07721,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.48633,0.02736,0.12658]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20305.0,"contact_point_centroid":[0.44527,-0.0448,0.09355],"force_p95":0.07129,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21477,"mean_force":0.0492,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44539,-0.02564,0.09148]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20818.0,"contact_point_centroid":[0.44651,-0.00652,0.09089],"force_p95":0.07315,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20365,"mean_force":0.04861,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4453,-0.02564,0.09018]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02638,-0.00206],"force_p95":0.14018,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17874,"mean_force":0.12716,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44729,-0.02568,0.04799]},{"body_a":"world","body_b":"grasp_target","contact_count":1824.0,"contact_point_centroid":[0.45856,-0.02632,-0.00192],"force_p95":0.13359,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4789,-0.01153,0.22594]},{"body_a":"world","body_b":"grasp_target","contact_count":1232.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45517,-0.02479,0.10254]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5321.0,"contact_point_centroid":[0.44744,-0.00647,0.04794],"force_p95":0.06746,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1221,"mean_force":0.0416,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44615,-0.02564,0.04688]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4892.0,"contact_point_centroid":[0.44616,-0.0449,0.04963],"force_p95":0.07353,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07981,"mean_force":0.04471,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44615,-0.02564,0.04688]}],"total_contact_groups":11},"final_pose_error":0.1316,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.53461,0.09412,0.01602],"final_tcp_position":[0.54728,0.10602,0.11732],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.28122,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":457.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1824.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.4586,-0.02381,0.15085],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12485,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":308.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1232.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45411,-0.02587,0.0547],"tcp_start":[0.4586,-0.02381,0.15085],"tcp_to_object_dist_end":0.02903,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02614,0.02578],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30361,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14011,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12013.0,"raw_peak_contact_force":0.17874,"tcp_end":[0.44612,-0.02564,0.04685],"tcp_start":[0.45411,-0.02587,0.0547],"tcp_to_object_dist_end":0.02445,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45405,-0.02643,0.11008],"object_pos_start":[0.45851,-0.02614,0.02578],"object_to_goal_dist_end":0.29339,"object_to_goal_dist_start":0.30361,"object_z_max":0.11,"peak_contact_force":0.08467,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41292.0,"raw_peak_contact_force":0.33132,"tcp_end":[0.44868,-0.02577,0.13674],"tcp_start":[0.44612,-0.02564,0.04685],"tcp_to_object_dist_end":0.0272,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53461,0.09412,0.01602],"object_pos_start":[0.45405,-0.02643,0.11008],"object_to_goal_dist_end":0.17823,"object_to_goal_dist_start":0.29339,"object_z_max":0.11009,"peak_contact_force":0.1226,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":25733.0,"raw_peak_contact_force":1.28122,"tcp_end":[0.54371,0.10532,0.14471],"tcp_start":[0.44868,-0.02577,0.13674],"tcp_to_object_dist_end":0.12949,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```