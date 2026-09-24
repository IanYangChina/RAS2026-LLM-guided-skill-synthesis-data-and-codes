## Search State

- **Seed**: 0
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | — | force_threshold_switch | admittance_control | position_control | position_control | admittance_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.2704 | 0.17 | ✅ accepted |

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

## Current Skill (Q=0.270) — your mutation base

```yaml
skill: grasp_place
skill_type: arm_gripper
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
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
  termination: contact_detected
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
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
- id: release_1
  type: release
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open

```

## Design Metrics

- **Composite score**: 0.270
- **task_score** (E): 0.169
- **fitness_score**: 0.560  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.290

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2317 |
| descend_1 | 1.00 | 1.00 | 0.0304 |
| grasp_1 | 1.00 | 1.00 | 0.0119 |
| lift_1 | 1.00 | 1.00 | 0.1270 |
| release_1 | 1.00 | 1.00 | 0.0257 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, 0.005, 0.072) | (0.497, 0.001, 0.030)→(0.497, 0.001, 0.026) | 0.263→0.265 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.493, 0.005, 0.072)→(0.492, 0.001, 0.042) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.265 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.492, 0.001, 0.042)→(0.484, 0.001, 0.033) | (0.497, 0.001, 0.026)→(0.497, 0.001, 0.026) | 0.265→0.266 | 1.00 / 42.667 | 0.142 | 0.178 |
| lift_1 | lift | 1.00 / step_budget | (0.484, 0.001, 0.033)→(0.492, 0.000, 0.160) | (0.497, 0.001, 0.026)→(0.503, 0.000, 0.146) | 0.266→0.214 | 1.00 / 37.000 | 0.080 | 0.593 |
| release_1 | release | 1.00 / step_budget | (0.492, 0.000, 0.160)→(0.487, 0.000, 0.185) | (0.503, 0.000, 0.146)→(0.488, 0.001, 0.027) | 0.214→0.268 | 1.00 / 2.000 | 0.180 | 1.555 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.195
- phase_score: 0.252
- phase_breakdown.release_1_score: 0.013
- phase_breakdown.transport_arc_score: 0.000
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.descend_1_score: 0.825
- phase_breakdown.approach_1_score: 0.357
- grasp_place_fitness: 0.573

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.573
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.195
- **Median Q (composite search score)**: 0.271
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.318


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69792,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06857,"descend_1.depth":0.06406,"grasp_1.grip_force":10.73441,"lift_1.lift_height":0.13603},"optimized_scores":{"best_composite_score":0.27123,"best_fitness_score":0.56123,"best_task_score":0.1701},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":202.0,"contact_point_centroid":[0.50046,-0.02344,-0.00656],"force_p95":1.18054,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.50372,"mean_force":0.34972,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50329,-0.02275,0.16306]},{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.51118,-0.02232,-0.00111],"force_p95":0.41256,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61524,"mean_force":0.07917,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49877,-0.02253,0.03408]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15757.0,"contact_point_centroid":[0.50352,-0.00367,0.09034],"force_p95":0.07474,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3177,"mean_force":0.04943,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50221,-0.02267,0.08853]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13237.0,"contact_point_centroid":[0.50234,-0.04186,0.09181],"force_p95":0.08022,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31683,"mean_force":0.05714,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50225,-0.02267,0.089]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5137,-0.0231,-0.00204],"force_p95":0.13718,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16607,"mean_force":0.12618,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50131,-0.02257,0.03368]},{"body_a":"world","body_b":"grasp_target","contact_count":2872.0,"contact_point_centroid":[0.5137,-0.02302,-0.00195],"force_p95":0.12878,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50316,0.0046,0.18498]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1059.0,"contact_point_centroid":[0.50796,-0.04208,0.15023],"force_p95":0.07837,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12537,"mean_force":0.04907,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50737,-0.02284,0.14749]},{"body_a":"world","body_b":"grasp_target","contact_count":2692.0,"contact_point_centroid":[0.5137,-0.02302,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50708,-0.02085,0.05135]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5166.0,"contact_point_centroid":[0.50114,-0.00349,0.03405],"force_p95":0.06961,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10659,"mean_force":0.0424,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50005,-0.02255,0.03232]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1224.0,"contact_point_centroid":[0.50934,-0.00385,0.14904],"force_p95":0.07447,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10471,"mean_force":0.04342,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5074,-0.02284,0.14753]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4158.0,"contact_point_centroid":[0.49925,-0.04179,0.03509],"force_p95":0.08017,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09025,"mean_force":0.05178,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.50005,-0.02255,0.03232]}],"total_contact_groups":11},"final_pose_error":0.01307,"key_states":{"actual_goal_position":[0.5541,0.15165,0.22199],"final_object_position":[0.50429,-0.02281,0.02787],"final_tcp_position":[0.50893,-0.02288,0.14965],"realised_goal_position":[0.5541,0.15165,0.22199],"realised_object_initial_position":[0.5137,-0.02302,0.03]},"peak_contact_force":1.50372,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":719.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.03],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26269,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2872.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50842,-0.01728,0.07482],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.04943,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":673.0,"n_steps_budget":1000.0,"object_pos_end":[0.5137,-0.02302,0.02602],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26561,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2692.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50839,-0.0227,0.04143],"tcp_start":[0.50842,-0.01728,0.07482],"tcp_to_object_dist_end":0.0163,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51358,-0.023,0.02584],"object_pos_start":[0.5137,-0.02302,0.02602],"object_to_goal_dist_end":0.26574,"object_to_goal_dist_start":0.26561,"object_z_max":0.02602,"peak_contact_force":0.1371,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11124.0,"raw_peak_contact_force":0.16607,"tcp_end":[0.50002,-0.02255,0.03228],"tcp_start":[0.50839,-0.0227,0.04143],"tcp_to_object_dist_end":0.01502,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.51976,-0.02349,0.13733],"object_pos_start":[0.51358,-0.023,0.02584],"object_to_goal_dist_end":0.19754,"object_to_goal_dist_start":0.26574,"object_z_max":0.13722,"peak_contact_force":0.07966,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":29139.0,"raw_peak_contact_force":0.61524,"tcp_end":[0.50893,-0.02288,0.14965],"tcp_start":[0.50002,-0.02255,0.03228],"tcp_to_object_dist_end":0.01641,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50429,-0.02281,0.02787],"object_pos_start":[0.51976,-0.02349,0.13733],"object_to_goal_dist_end":0.2657,"object_to_goal_dist_start":0.19754,"object_z_max":0.13737,"peak_contact_force":0.17493,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2485.0,"raw_peak_contact_force":1.50372,"tcp_end":[0.50318,-0.02274,0.17436],"tcp_start":[0.50893,-0.02288,0.14965],"tcp_to_object_dist_end":0.14649,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69474,"average_solve_count":95.0,"average_success_count":95.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07275,"descend_1.depth":0.09129,"grasp_1.grip_force":22.94202,"lift_1.lift_height":0.1322},"optimized_scores":{"best_composite_score":0.28314,"best_fitness_score":0.57314,"best_task_score":0.19485},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":203.0,"contact_point_centroid":[0.48838,0.0439,-0.00637],"force_p95":1.14502,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.45185,"mean_force":0.34399,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49089,0.04357,0.15951]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.49868,0.04334,-0.00118],"force_p95":0.37763,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.594,"mean_force":0.07762,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48654,0.04377,0.03494]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12291.0,"contact_point_centroid":[0.49004,0.06301,0.09117],"force_p95":0.08499,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32823,"mean_force":0.05888,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49005,0.0438,0.0884]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15210.0,"contact_point_centroid":[0.49178,0.02487,0.08945],"force_p95":0.07928,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30214,"mean_force":0.04911,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48998,0.0438,0.08783]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50123,0.04503,-0.00209],"force_p95":0.14999,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19618,"mean_force":0.12972,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48901,0.04402,0.03443]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5036.0,"contact_point_centroid":[0.48954,0.0249,0.03446],"force_p95":0.07507,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17288,"mean_force":0.04316,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48777,0.04391,0.03311]},{"body_a":"world","body_b":"grasp_target","contact_count":2832.0,"contact_point_centroid":[0.50118,0.04505,-0.00195],"force_p95":0.12892,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1228,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49726,0.03561,0.19409]},{"body_a":"world","body_b":"grasp_target","contact_count":2732.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49492,0.04524,0.05412]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1226.0,"contact_point_centroid":[0.49748,0.02504,0.14518],"force_p95":0.0779,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11455,"mean_force":0.0436,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49497,0.04397,0.14382]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1057.0,"contact_point_centroid":[0.49499,0.06321,0.14664],"force_p95":0.081,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1101,"mean_force":0.04925,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49494,0.04397,0.14379]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4193.0,"contact_point_centroid":[0.4878,0.0632,0.03571],"force_p95":0.08635,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09497,"mean_force":0.05192,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48778,0.04391,0.03312]}],"total_contact_groups":11},"final_pose_error":0.01288,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.49042,0.04359,0.02761],"final_tcp_position":[0.4965,0.0441,0.14587],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.45185,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":709.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2832.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.4967,0.04672,0.08126],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.05545,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":683.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2732.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49598,0.04465,0.04189],"tcp_start":[0.4967,0.04672,0.08126],"tcp_to_object_dist_end":0.01671,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50115,0.04449,0.02567],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24253,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.14889,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11029.0,"raw_peak_contact_force":0.19618,"tcp_end":[0.48774,0.0439,0.03308],"tcp_start":[0.49598,0.04465,0.04189],"tcp_to_object_dist_end":0.01533,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.50721,0.04496,0.13291],"object_pos_start":[0.50115,0.04449,0.02567],"object_to_goal_dist_end":0.20839,"object_to_goal_dist_start":0.24253,"object_z_max":0.13279,"peak_contact_force":0.08102,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27645.0,"raw_peak_contact_force":0.594,"tcp_end":[0.4965,0.0441,0.14587],"tcp_start":[0.48774,0.0439,0.03308],"tcp_to_object_dist_end":0.01684,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.49042,0.04359,0.02761],"object_pos_start":[0.50721,0.04496,0.13291],"object_to_goal_dist_end":0.24533,"object_to_goal_dist_start":0.20839,"object_z_max":0.13294,"peak_contact_force":0.16702,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2486.0,"raw_peak_contact_force":1.45185,"tcp_end":[0.49078,0.04357,0.17092],"tcp_start":[0.4965,0.0441,0.14587],"tcp_to_object_dist_end":0.14331,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54717,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05179,"descend_1.depth":0.04171,"grasp_1.grip_force":17.67092,"lift_1.lift_height":0.16971},"optimized_scores":{"best_composite_score":0.25683,"best_fitness_score":0.54683,"best_task_score":0.14247},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":178.0,"contact_point_centroid":[0.46067,-0.02054,-0.0081],"force_p95":1.35253,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.70952,"mean_force":0.4144,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.46698,-0.01972,0.20049]},{"body_a":"world","body_b":"grasp_target","contact_count":134.0,"contact_point_centroid":[0.47376,-0.01909,-0.00112],"force_p95":0.33994,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5684,"mean_force":0.06767,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46177,-0.01951,0.03581]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19543.0,"contact_point_centroid":[0.46666,-0.00064,0.10845],"force_p95":0.07309,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30347,"mean_force":0.04905,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46524,-0.01964,0.10666]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16707.0,"contact_point_centroid":[0.46544,-0.03883,0.10959],"force_p95":0.07949,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2995,"mean_force":0.05591,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46526,-0.01964,0.10688]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02019,-0.00205],"force_p95":0.13895,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17062,"mean_force":0.12662,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4642,-0.01954,0.03517]},{"body_a":"world","body_b":"grasp_target","contact_count":2996.0,"contact_point_centroid":[0.47616,-0.02015,-0.00195],"force_p95":0.12823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48522,0.00706,0.17738]},{"body_a":"world","body_b":"grasp_target","contact_count":1660.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47063,-0.01821,0.04596]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1063.0,"contact_point_centroid":[0.47136,-0.03906,0.18446],"force_p95":0.07855,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12085,"mean_force":0.04875,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.47054,-0.0198,0.18186]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5067.0,"contact_point_centroid":[0.46424,-0.00047,0.03551],"force_p95":0.06793,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11081,"mean_force":0.04307,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.463,-0.01952,0.03397]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1217.0,"contact_point_centroid":[0.47262,-0.00082,0.18342],"force_p95":0.07273,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09867,"mean_force":0.04341,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.47059,-0.0198,0.18191]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4270.0,"contact_point_centroid":[0.46236,-0.03877,0.03654],"force_p95":0.07851,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08815,"mean_force":0.05072,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.463,-0.01952,0.03397]}],"total_contact_groups":11},"final_pose_error":0.01243,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.46821,-0.01834,0.02485],"final_tcp_position":[0.47197,-0.01984,0.18379],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.70952,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":750.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2996.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.4727,-0.01449,0.05901],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.03365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":415.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1660.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.471,-0.01965,0.04196],"tcp_start":[0.4727,-0.01449,0.05901],"tcp_to_object_dist_end":0.01677,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47606,-0.01994,0.02582],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28842,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13888,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11137.0,"raw_peak_contact_force":0.17062,"tcp_end":[0.46297,-0.01952,0.03394],"tcp_start":[0.471,-0.01965,0.04196],"tcp_to_object_dist_end":0.01541,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":933.0,"n_steps_budget":1000.0,"object_pos_end":[0.48169,-0.02042,0.16835],"object_pos_start":[0.47606,-0.01994,0.02582],"object_to_goal_dist_end":0.23484,"object_to_goal_dist_start":0.28842,"object_z_max":0.16823,"peak_contact_force":0.07964,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36384.0,"raw_peak_contact_force":0.5684,"tcp_end":[0.47197,-0.01984,0.18379],"tcp_start":[0.46297,-0.01952,0.03394],"tcp_to_object_dist_end":0.01826,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46821,-0.01834,0.02485],"object_pos_start":[0.48169,-0.02042,0.16835],"object_to_goal_dist_end":0.29229,"object_to_goal_dist_start":0.23484,"object_z_max":0.16839,"peak_contact_force":0.19659,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2458.0,"raw_peak_contact_force":1.70952,"tcp_end":[0.46689,-0.01971,0.20943],"tcp_start":[0.47197,-0.01984,0.18379],"tcp_to_object_dist_end":0.18459,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```