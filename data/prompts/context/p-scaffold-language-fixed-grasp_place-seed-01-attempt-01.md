## Search State

- **Seed**: 1
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.3429 | 0.34 | ❌ rejected |
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

## Current Skill (Q=0.343) — your mutation base

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

- **Composite score**: 0.343
- **task_score** (E): 0.340
- **fitness_score**: 0.633  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.290

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1174 |
| descend_1 | 1.00 | 1.00 | 0.1374 |
| grasp_1 | 1.00 | 1.00 | 0.0118 |
| lift_1 | 0.00 | 1.00 | 0.1032 |
| release_1 | 0.00 | 1.00 | 0.1645 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.479, -0.000, 0.192) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.479, -0.000, 0.192)→(0.474, -0.001, 0.055) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.001, 0.055)→(0.466, -0.001, 0.046) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 45.333 | 0.146 | 0.188 |
| lift_1 | lift | 0.00 / step_budget | (0.466, -0.001, 0.046)→(0.470, -0.001, 0.149) | (0.479, -0.001, 0.026)→(0.475, -0.001, 0.123) | 0.278→0.251 | 1.00 / 38.333 | 0.079 | 0.383 |
| release_1 | release | 0.00 / step_budget | (0.470, -0.001, 0.149)→(0.553, 0.135, 0.170) | (0.475, -0.001, 0.123)→(0.544, 0.138, 0.023) | 0.251→0.164 | 1.00 / 3.667 | 0.124 | 1.374 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.424
- phase_score: 0.289
- phase_breakdown.descend_1_score: 0.875
- phase_breakdown.transport_arc_score: 0.000
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.334
- phase_breakdown.approach_1_score: 0.034
- grasp_place_fitness: 0.675

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.675
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.424
- **Median Q (composite search score)**: 0.322
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.227


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90076,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19209,"descend_1.depth":0.03274,"grasp_1.grip_force":14.50825,"lift_1.speed":0.07277},"optimized_scores":{"best_composite_score":0.3854,"best_fitness_score":0.6754,"best_task_score":0.42423},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":238.0,"contact_point_centroid":[0.53312,0.21192,-0.00525],"force_p95":0.95884,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.36013,"mean_force":0.29321,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54258,0.20045,0.15884]},{"body_a":"world","body_b":"grasp_target","contact_count":172.0,"contact_point_centroid":[0.49766,0.04229,-0.00127],"force_p95":0.25652,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44105,"mean_force":0.07878,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48644,0.04324,0.04693]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16792.0,"contact_point_centroid":[0.51363,0.13699,0.1523],"force_p95":0.0996,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31215,"mean_force":0.05911,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5162,0.11827,0.15157]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19905.0,"contact_point_centroid":[0.48789,0.06244,0.10489],"force_p95":0.0756,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27664,"mean_force":0.05079,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48832,0.04331,0.10228]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20437.0,"contact_point_centroid":[0.48994,0.02422,0.10315],"force_p95":0.07865,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26973,"mean_force":0.04994,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4883,0.0433,0.10207]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17476.0,"contact_point_centroid":[0.52045,0.10167,0.14987],"force_p95":0.09891,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2208,"mean_force":0.0592,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51684,0.12011,0.15138]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04506,-0.00214],"force_p95":0.16109,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21206,"mean_force":0.13285,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48909,0.04349,0.04654]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4854.0,"contact_point_centroid":[0.49001,0.02423,0.04625],"force_p95":0.07634,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16583,"mean_force":0.04547,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4879,0.04339,0.04525]},{"body_a":"world","body_b":"grasp_target","contact_count":1360.0,"contact_point_centroid":[0.50118,0.04505,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4979,0.01902,0.24977]},{"body_a":"world","body_b":"grasp_target","contact_count":1792.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49567,0.04168,0.12619]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5148.0,"contact_point_centroid":[0.48719,0.06259,0.04898],"force_p95":0.07347,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07972,"mean_force":0.04296,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4879,0.04339,0.04525]}],"total_contact_groups":11},"final_pose_error":0.04731,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.5317,0.21207,0.02678],"final_tcp_position":[0.54569,0.20156,0.14325],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.36013,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":341.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1360.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.49762,0.03946,0.19926],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":448.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1792.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49621,0.04413,0.05437],"tcp_start":[0.49762,0.03946,0.19926],"tcp_to_object_dist_end":0.0288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50122,0.04424,0.0255],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.2428,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15965,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11802.0,"raw_peak_contact_force":0.21206,"tcp_end":[0.48787,0.04338,0.04522],"tcp_start":[0.49621,0.04413,0.05437],"tcp_to_object_dist_end":0.02383,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49944,0.04453,0.13801],"object_pos_start":[0.50122,0.04424,0.0255],"object_to_goal_dist_end":0.21079,"object_to_goal_dist_start":0.2428,"object_z_max":0.13791,"peak_contact_force":0.07874,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40514.0,"raw_peak_contact_force":0.44105,"tcp_end":[0.49321,0.04363,0.16383],"tcp_start":[0.48787,0.04338,0.04522],"tcp_to_object_dist_end":0.02657,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5317,0.21207,0.02678],"object_pos_start":[0.49944,0.04453,0.13801],"object_to_goal_dist_end":0.12862,"object_to_goal_dist_start":0.21079,"object_z_max":0.13804,"peak_contact_force":0.15118,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":34506.0,"raw_peak_contact_force":1.36013,"tcp_end":[0.54248,0.20038,0.17022],"tcp_start":[0.49321,0.04363,0.16383],"tcp_to_object_dist_end":0.14431,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70149,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1161,"descend_1.depth":0.03249,"grasp_1.grip_force":20.92976,"lift_1.speed":0.06037},"optimized_scores":{"best_composite_score":0.32129,"best_fitness_score":0.61129,"best_task_score":0.29677},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":256.0,"contact_point_centroid":[0.56628,0.11505,-0.00536],"force_p95":1.03243,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.50601,"mean_force":0.2803,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57161,0.10039,0.1858]},{"body_a":"world","body_b":"grasp_target","contact_count":159.0,"contact_point_centroid":[0.47236,-0.01949,-0.00113],"force_p95":0.24382,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.37254,"mean_force":0.07165,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46186,-0.01964,0.04777]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15186.0,"contact_point_centroid":[0.51231,0.05336,0.15276],"force_p95":0.10384,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27287,"mean_force":0.06526,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51326,0.03448,0.15373]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20141.0,"contact_point_centroid":[0.46306,-0.03885,0.09741],"force_p95":0.07189,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24748,"mean_force":0.04981,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46288,-0.01969,0.0952]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20526.0,"contact_point_centroid":[0.46409,-0.00057,0.09559],"force_p95":0.07281,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24256,"mean_force":0.04947,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46284,-0.01969,0.09454]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16245.0,"contact_point_centroid":[0.51677,0.01811,0.15327],"force_p95":0.09914,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21853,"mean_force":0.06125,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51542,0.03684,0.15425]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02021,-0.00204],"force_p95":0.13727,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17114,"mean_force":0.12631,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46438,-0.01968,0.04737]},{"body_a":"world","body_b":"grasp_target","contact_count":2096.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13221,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12286,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48623,-0.00904,0.21284]},{"body_a":"world","body_b":"grasp_target","contact_count":920.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47153,-0.01912,0.0898]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5091.0,"contact_point_centroid":[0.46476,-0.00049,0.04752],"force_p95":0.06724,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09724,"mean_force":0.04338,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46321,-0.01966,0.04619]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4886.0,"contact_point_centroid":[0.46342,-0.0389,0.04911],"force_p95":0.07125,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08295,"mean_force":0.04463,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46321,-0.01966,0.04619]}],"total_contact_groups":11},"final_pose_error":0.08409,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.56729,0.11226,0.02604],"final_tcp_position":[0.57467,0.10095,0.16862],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.50601,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":525.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2096.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.47401,-0.0185,0.12545],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09947,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":230.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":920.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47133,-0.01979,0.05452],"tcp_start":[0.47401,-0.0185,0.12545],"tcp_to_object_dist_end":0.02891,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47609,-0.02004,0.02582],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28847,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.1373,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11777.0,"raw_peak_contact_force":0.17114,"tcp_end":[0.46318,-0.01966,0.04616],"tcp_start":[0.47133,-0.01979,0.05452],"tcp_to_object_dist_end":0.02409,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47248,-0.02031,0.1197],"object_pos_start":[0.47609,-0.02004,0.02582],"object_to_goal_dist_end":0.24986,"object_to_goal_dist_start":0.28847,"object_z_max":0.1196,"peak_contact_force":0.07548,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40826.0,"raw_peak_contact_force":0.37254,"tcp_end":[0.46672,-0.0198,0.14589],"tcp_start":[0.46318,-0.01966,0.04616],"tcp_to_object_dist_end":0.02681,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56729,0.11226,0.02604],"object_pos_start":[0.47248,-0.02031,0.1197],"object_to_goal_dist_end":0.18222,"object_to_goal_dist_start":0.24986,"object_z_max":0.13531,"peak_contact_force":0.09913,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":31687.0,"raw_peak_contact_force":1.50601,"tcp_end":[0.57153,0.10036,0.19542],"tcp_start":[0.46672,-0.0198,0.14589],"tcp_to_object_dist_end":0.16986,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58784,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.24473,"descend_1.depth":0.07556,"grasp_1.grip_force":25.36138,"lift_1.speed":0.04251},"optimized_scores":{"best_composite_score":0.32196,"best_fitness_score":0.61196,"best_task_score":0.299},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":836.0,"contact_point_centroid":[0.53293,0.09065,-0.00275],"force_p95":0.45464,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.25445,"mean_force":0.16009,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54454,0.10464,0.1242]},{"body_a":"world","body_b":"grasp_target","contact_count":168.0,"contact_point_centroid":[0.45481,-0.02508,-0.00116],"force_p95":0.26522,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3351,"mean_force":0.07487,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4451,-0.02557,0.04851]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10838.0,"contact_point_centroid":[0.4855,0.0455,0.12582],"force_p95":0.11752,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2798,"mean_force":0.0791,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.48601,0.02667,0.12773]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13048.0,"contact_point_centroid":[0.48772,0.0098,0.12573],"force_p95":0.09731,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24953,"mean_force":0.06625,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.48719,0.02828,0.12747]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20373.0,"contact_point_centroid":[0.44546,-0.04477,0.09437],"force_p95":0.0706,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21913,"mean_force":0.04906,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44571,-0.02562,0.09236]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20885.0,"contact_point_centroid":[0.44664,-0.00649,0.09134],"force_p95":0.07369,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20602,"mean_force":0.04859,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4456,-0.02561,0.09078]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02638,-0.00206],"force_p95":0.14073,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17974,"mean_force":0.12731,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44765,-0.02565,0.04814]},{"body_a":"world","body_b":"grasp_target","contact_count":784.0,"contact_point_centroid":[0.45856,-0.02632,-0.00184],"force_p95":0.13755,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12325,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48241,-0.00979,0.27585]},{"body_a":"world","body_b":"grasp_target","contact_count":2460.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45819,-0.02338,0.15208]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5340.0,"contact_point_centroid":[0.44775,-0.00643,0.04803],"force_p95":0.06798,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1201,"mean_force":0.04147,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44651,-0.02561,0.04703]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4986.0,"contact_point_centroid":[0.44657,-0.04487,0.04985],"force_p95":0.07342,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08085,"mean_force":0.04391,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44651,-0.02561,0.04703]}],"total_contact_groups":11},"final_pose_error":0.13153,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.5328,0.09117,0.01602],"final_tcp_position":[0.5474,0.10603,0.11791],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.25445,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":197.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":784.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.46406,-0.021,0.25082],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22494,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":615.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2460.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45448,-0.02584,0.05487],"tcp_start":[0.46406,-0.021,0.25082],"tcp_to_object_dist_end":0.02914,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02611,0.02577],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30359,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14061,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12126.0,"raw_peak_contact_force":0.17974,"tcp_end":[0.44648,-0.02561,0.047],"tcp_start":[0.45448,-0.02584,0.05487],"tcp_to_object_dist_end":0.02441,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45411,-0.02636,0.11139],"object_pos_start":[0.45851,-0.02611,0.02577],"object_to_goal_dist_end":0.29329,"object_to_goal_dist_start":0.30359,"object_z_max":0.1113,"peak_contact_force":0.08224,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41426.0,"raw_peak_contact_force":0.3351,"tcp_end":[0.44893,-0.02574,0.1381],"tcp_start":[0.44648,-0.02561,0.047],"tcp_to_object_dist_end":0.02722,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5328,0.09117,0.01602],"object_pos_start":[0.45411,-0.02636,0.11139],"object_to_goal_dist_end":0.1811,"object_to_goal_dist_start":0.29329,"object_z_max":0.1114,"peak_contact_force":0.12262,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":24722.0,"raw_peak_contact_force":1.25445,"tcp_end":[0.54384,0.10533,0.1453],"tcp_start":[0.44893,-0.02574,0.1381],"tcp_to_object_dist_end":0.13052,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```