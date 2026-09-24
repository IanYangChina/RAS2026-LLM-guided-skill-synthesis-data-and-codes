## Search State

- **Seed**: 1
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 4 | 0.3448 | 0.34 | ✅ accepted |
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

## Current Skill (Q=0.345) — your mutation base

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

- **Composite score**: 0.345
- **task_score** (E): 0.344
- **fitness_score**: 0.635  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.290

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1023 |
| descend_1 | 1.00 | 1.00 | 0.1538 |
| grasp_1 | 1.00 | 1.00 | 0.0118 |
| lift_1 | 0.00 | 1.00 | 0.0993 |
| release_1 | 0.00 | 1.00 | 0.1650 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.479, 0.001, 0.208) | (0.479, -0.000, 0.030)→(0.479, -0.000, 0.026) | 0.276→0.278 | 1.00 / 4.000 | 3.054 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.479, 0.001, 0.208)→(0.474, -0.000, 0.055) | (0.479, -0.000, 0.026)→(0.479, -0.000, 0.026) | 0.278→0.278 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.474, -0.000, 0.055)→(0.466, -0.001, 0.046) | (0.479, -0.000, 0.026)→(0.479, -0.001, 0.026) | 0.278→0.278 | 1.00 / 45.667 | 0.146 | 0.189 |
| lift_1 | lift | 0.00 / step_budget | (0.466, -0.001, 0.046)→(0.469, -0.001, 0.146) | (0.479, -0.001, 0.026)→(0.475, -0.001, 0.119) | 0.278→0.252 | 1.00 / 38.000 | 0.077 | 0.379 |
| release_1 | release | 0.00 / step_budget | (0.469, -0.001, 0.146)→(0.552, 0.135, 0.169) | (0.475, -0.001, 0.119)→(0.544, 0.145, 0.023) | 0.252→0.162 | 1.00 / 3.667 | 0.125 | 1.317 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.423
- phase_score: 0.290
- phase_breakdown.descend_1_score: 0.874
- phase_breakdown.transport_arc_score: 0.000
- phase_breakdown.grasp_1_score: 1.000
- phase_breakdown.release_1_score: 0.336
- phase_breakdown.approach_1_score: 0.044
- grasp_place_fitness: 0.675

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.675
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.423
- **Median Q (composite search score)**: 0.325
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.266


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81818,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17871,"descend_1.depth":0.02086,"grasp_1.grip_force":20.4201,"lift_1.speed":0.07052},"optimized_scores":{"best_composite_score":0.38495,"best_fitness_score":0.67495,"best_task_score":0.42342},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":245.0,"contact_point_centroid":[0.53356,0.21131,-0.00514],"force_p95":0.92853,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.36068,"mean_force":0.28232,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54244,0.20043,0.1578]},{"body_a":"world","body_b":"grasp_target","contact_count":178.0,"contact_point_centroid":[0.49775,0.04237,-0.00125],"force_p95":0.24837,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43469,"mean_force":0.07843,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48638,0.04323,0.047]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19867.0,"contact_point_centroid":[0.48774,0.06243,0.10289],"force_p95":0.07564,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27178,"mean_force":0.05085,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48813,0.04329,0.1003]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20385.0,"contact_point_centroid":[0.48978,0.02421,0.10124],"force_p95":0.07875,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26536,"mean_force":0.05001,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.48811,0.04329,0.10018]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16641.0,"contact_point_centroid":[0.51348,0.13694,0.1495],"force_p95":0.09934,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25571,"mean_force":0.05924,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51592,0.11819,0.14884]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.50124,0.04506,-0.00214],"force_p95":0.16079,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21204,"mean_force":0.13285,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48906,0.04349,0.04656]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17580.0,"contact_point_centroid":[0.52044,0.10184,0.14721],"force_p95":0.09781,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21106,"mean_force":0.05874,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51664,0.12023,0.14868]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4855.0,"contact_point_centroid":[0.48998,0.02425,0.04628],"force_p95":0.07635,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16581,"mean_force":0.04539,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48787,0.04338,0.04527]},{"body_a":"world","body_b":"grasp_target","contact_count":1508.0,"contact_point_centroid":[0.50118,0.04505,-0.00191],"force_p95":0.13496,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49781,0.01931,0.24322]},{"body_a":"world","body_b":"grasp_target","contact_count":1640.0,"contact_point_centroid":[0.50118,0.04505,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49558,0.04191,0.11984]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5056.0,"contact_point_centroid":[0.48728,0.0626,0.04887],"force_p95":0.07492,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08223,"mean_force":0.04373,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.48787,0.04338,0.04527]}],"total_contact_groups":11},"final_pose_error":0.04746,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.53145,0.21189,0.0266],"final_tcp_position":[0.54556,0.20154,0.14233],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":1.36068,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":378.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1508.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.49751,0.03993,0.18618],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16029,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":410.0,"n_steps_budget":1000.0,"object_pos_end":[0.50118,0.04505,0.02602],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24188,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1640.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49618,0.04413,0.05439],"tcp_start":[0.49751,0.03993,0.18618],"tcp_to_object_dist_end":0.02882,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.50122,0.04423,0.0255],"object_pos_start":[0.50118,0.04505,0.02602],"object_to_goal_dist_end":0.24281,"object_to_goal_dist_start":0.24188,"object_z_max":0.02602,"peak_contact_force":0.15951,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11711.0,"raw_peak_contact_force":0.21204,"tcp_end":[0.48784,0.04338,0.04523],"tcp_start":[0.49618,0.04413,0.05439],"tcp_to_object_dist_end":0.02386,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49905,0.0445,0.13356],"object_pos_start":[0.50122,0.04423,0.0255],"object_to_goal_dist_end":0.21117,"object_to_goal_dist_start":0.24281,"object_z_max":0.13347,"peak_contact_force":0.07876,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40430.0,"raw_peak_contact_force":0.43469,"tcp_end":[0.49285,0.0436,0.15946],"tcp_start":[0.48784,0.04338,0.04523],"tcp_to_object_dist_end":0.02664,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53145,0.21189,0.0266],"object_pos_start":[0.49905,0.0445,0.13356],"object_to_goal_dist_end":0.12891,"object_to_goal_dist_start":0.21117,"object_z_max":0.13358,"peak_contact_force":0.14443,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":34466.0,"raw_peak_contact_force":1.36068,"tcp_end":[0.54234,0.20035,0.16929],"tcp_start":[0.49285,0.0436,0.15946],"tcp_to_object_dist_end":0.14358,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5274,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.29612,"descend_1.depth":0.04297,"grasp_1.grip_force":21.92036,"lift_1.speed":0.05625},"optimized_scores":{"best_composite_score":0.32464,"best_fitness_score":0.61464,"best_task_score":0.30385},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":274.0,"contact_point_centroid":[0.56745,0.12725,-0.00524],"force_p95":0.81896,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.35443,"mean_force":0.25461,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57152,0.10043,0.18329]},{"body_a":"world","body_b":"grasp_target","contact_count":173.0,"contact_point_centroid":[0.47192,-0.01904,-0.00116],"force_p95":0.23803,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36546,"mean_force":0.07367,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46241,-0.01952,0.0483]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12915.0,"contact_point_centroid":[0.51308,0.05414,0.14818],"force_p95":0.11151,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34887,"mean_force":0.07628,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51384,0.03531,0.14985]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20238.0,"contact_point_centroid":[0.46312,-0.03874,0.09476],"force_p95":0.07103,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2434,"mean_force":0.04948,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46312,-0.01958,0.09275]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20629.0,"contact_point_centroid":[0.46398,-0.00045,0.09228],"force_p95":0.07265,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23217,"mean_force":0.04912,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46304,-0.01958,0.09151]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15293.0,"contact_point_centroid":[0.51627,0.01822,0.14847],"force_p95":0.09786,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22445,"mean_force":0.06396,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51512,0.03675,0.15017]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.0202,-0.00205],"force_p95":0.13877,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17524,"mean_force":0.12676,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46502,-0.01956,0.0479]},{"body_a":"world","body_b":"grasp_target","contact_count":380.0,"contact_point_centroid":[0.47616,-0.02015,-0.00167],"force_p95":0.13823,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12398,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49119,-0.006,0.29632]},{"body_a":"world","body_b":"grasp_target","contact_count":2932.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47611,-0.01635,0.17315]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5324.0,"contact_point_centroid":[0.4649,-0.00036,0.04792],"force_p95":0.066,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10043,"mean_force":0.0415,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46386,-0.01954,0.04672]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4895.0,"contact_point_centroid":[0.46397,-0.0388,0.04949],"force_p95":0.07173,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08201,"mean_force":0.0447,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46386,-0.01954,0.04672]}],"total_contact_groups":11},"final_pose_error":0.08463,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.56716,0.12762,0.0263],"final_tcp_position":[0.57458,0.10098,0.1667],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":8.91703,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":96.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02601],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28839,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":8.91703,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":380.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.48221,-0.01308,0.29298],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.26714,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":733.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02601],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28839,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2932.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.47199,-0.01967,0.05508],"tcp_start":[0.48221,-0.01308,0.29298],"tcp_to_object_dist_end":0.02936,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.4761,-0.01997,0.0258],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28843,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13873,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12019.0,"raw_peak_contact_force":0.17524,"tcp_end":[0.46383,-0.01954,0.04669],"tcp_start":[0.47199,-0.01967,0.05508],"tcp_to_object_dist_end":0.02423,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47185,-0.02026,0.11332],"object_pos_start":[0.4761,-0.01997,0.0258],"object_to_goal_dist_end":0.25209,"object_to_goal_dist_start":0.28843,"object_z_max":0.11323,"peak_contact_force":0.07485,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41040.0,"raw_peak_contact_force":0.36546,"tcp_end":[0.46652,-0.01969,0.13993],"tcp_start":[0.46383,-0.01954,0.04669],"tcp_to_object_dist_end":0.02715,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.56716,0.12762,0.0263],"object_pos_start":[0.47185,-0.02026,0.11332],"object_to_goal_dist_end":0.17868,"object_to_goal_dist_start":0.25209,"object_z_max":0.13214,"peak_contact_force":0.10841,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":28482.0,"raw_peak_contact_force":1.35443,"tcp_end":[0.57143,0.10039,0.19352],"tcp_start":[0.46652,-0.01969,0.13993],"tcp_to_object_dist_end":0.16947,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56164,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13628,"descend_1.depth":0.04431,"grasp_1.grip_force":22.34,"lift_1.speed":0.03977},"optimized_scores":{"best_composite_score":0.32493,"best_fitness_score":0.61493,"best_task_score":0.30506},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":728.0,"contact_point_centroid":[0.5348,0.09383,-0.00283],"force_p95":0.48534,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.23655,"mean_force":0.16509,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54469,0.10531,0.12461]},{"body_a":"world","body_b":"grasp_target","contact_count":165.0,"contact_point_centroid":[0.45463,-0.02518,-0.00115],"force_p95":0.27133,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33569,"mean_force":0.07421,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44474,-0.0256,0.04836]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13544.0,"contact_point_centroid":[0.48901,0.01144,0.1249],"force_p95":0.09675,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23807,"mean_force":0.06571,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.48829,0.02995,0.12654]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11539.0,"contact_point_centroid":[0.48577,0.04622,0.12515],"force_p95":0.11449,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22212,"mean_force":0.0771,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.48635,0.02738,0.12689]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20299.0,"contact_point_centroid":[0.44528,-0.0448,0.09379],"force_p95":0.07131,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21856,"mean_force":0.04923,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44539,-0.02564,0.09171]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20802.0,"contact_point_centroid":[0.44652,-0.00652,0.09116],"force_p95":0.07315,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20748,"mean_force":0.04866,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44531,-0.02564,0.09044]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02638,-0.00206],"force_p95":0.14021,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17881,"mean_force":0.12716,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44727,-0.02567,0.04797]},{"body_a":"world","body_b":"grasp_target","contact_count":1884.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47877,-0.0116,0.22335]},{"body_a":"world","body_b":"grasp_target","contact_count":1168.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45507,-0.02484,0.09999]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5321.0,"contact_point_centroid":[0.44742,-0.00646,0.04793],"force_p95":0.06743,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1221,"mean_force":0.0416,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44612,-0.02564,0.04686]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4892.0,"contact_point_centroid":[0.44614,-0.0449,0.04962],"force_p95":0.07352,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07986,"mean_force":0.04471,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44613,-0.02564,0.04687]}],"total_contact_groups":11},"final_pose_error":0.1316,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.53461,0.09434,0.01602],"final_tcp_position":[0.54729,0.10602,0.1175],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.23655,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":472.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1884.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.4584,-0.02391,0.14574],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11974,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":292.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1168.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45408,-0.02587,0.05469],"tcp_start":[0.4584,-0.02391,0.14574],"tcp_to_object_dist_end":0.02902,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02614,0.02578],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30361,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14014,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12013.0,"raw_peak_contact_force":0.17881,"tcp_end":[0.4461,-0.02564,0.04684],"tcp_start":[0.45408,-0.02587,0.05469],"tcp_to_object_dist_end":0.02445,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.454,-0.02642,0.11052],"object_pos_start":[0.45851,-0.02614,0.02578],"object_to_goal_dist_end":0.29341,"object_to_goal_dist_start":0.30361,"object_z_max":0.11043,"peak_contact_force":0.07624,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41266.0,"raw_peak_contact_force":0.33569,"tcp_end":[0.44868,-0.02576,0.13715],"tcp_start":[0.4461,-0.02564,0.04684],"tcp_to_object_dist_end":0.02717,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53461,0.09434,0.01602],"object_pos_start":[0.454,-0.02642,0.11052],"object_to_goal_dist_end":0.17809,"object_to_goal_dist_start":0.29341,"object_z_max":0.11053,"peak_contact_force":0.1226,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":25811.0,"raw_peak_contact_force":1.23655,"tcp_end":[0.54371,0.10532,0.14488],"tcp_start":[0.44868,-0.02576,0.13715],"tcp_to_object_dist_end":0.12965,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```