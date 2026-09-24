## Search State

- **Seed**: 3
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | position_control | position_control | position_control | position_control | pose_tolerance | contact_detected | grasp_success | pose_tolerance | pose_tolerance | 5 | 0.2349 | 0.20 | ✅ accepted |

**Proposal policy**: task_score is 0.20 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `51caab5aeef033bda3880e250ac3d834b494dfd11f1563b679caeea40811318b`
- Frozen object start: [0.45856491671436245, -0.02631894934039003, 0.03]
- Frozen task target: [0.6301274465206397, 0.20821620360643678, 0.11411929633605988]
- Goal object position: (0.6301274465206397, 0.20821620360643678, 0.11411929633605988)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6301274465206397, 0.20821620360643678, 0.11411929633605988)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.45856491671436245, -0.02631894934039003, 0.03)
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
  frozen_object_start: [0.4586, -0.0263, 0.03]
  frozen_task_target: [0.6301, 0.2082, 0.1141]
  frozen_object_starts: {'grasp_target': [0.45856491671436245, -0.02631894934039003, 0.03]}
  frozen_targets: {'place_target': [0.6301274465206397, 0.20821620360643678, 0.11411929633605988]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 51caab5aeef033bda3880e250ac3d834b494dfd11f1563b679caeea40811318b

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

## Current Skill (Q=0.235) — your mutation base

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
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
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
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: release_1
  type: release
  control: position_control
  termination: pose_tolerance
  end_effector_action: open

```

## Design Metrics

- **Composite score**: 0.235
- **task_score** (E): 0.202
- **fitness_score**: 0.575  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.340

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1682 |
| descend_1 | 1.00 | 1.00 | 0.0937 |
| grasp_1 | 1.00 | 1.00 | 0.0124 |
| lift_1 | 1.00 | 1.00 | 0.1540 |
| release_1 | 1.00 | 1.00 | 0.0252 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.138) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.002, 0.138)→(0.506, 0.002, 0.044) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.506, 0.002, 0.044)→(0.498, 0.002, 0.035) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 43.333 | 0.138 | 0.169 |
| lift_1 | lift | 1.00 / step_budget | (0.498, 0.002, 0.035)→(0.506, 0.002, 0.189) | (0.511, 0.002, 0.026)→(0.515, 0.002, 0.172) | 0.246→0.219 | 1.00 / 37.000 | 0.081 | 0.573 |
| release_1 | release | 1.00 / step_budget | (0.506, 0.002, 0.189)→(0.501, 0.002, 0.213) | (0.515, 0.002, 0.172)→(0.509, 0.002, 0.023) | 0.219→0.248 | 1.00 / 2.000 | 0.143 | 1.550 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.291
- phase_score: 0.242
- phase_breakdown.approach_1_score: 0.117
- phase_breakdown.release_1_score: 0.019
- phase_breakdown.descend_1_score: 0.833
- phase_breakdown.transport_arc_score: 0.000
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.621

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.621
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.291
- **Median Q (composite search score)**: 0.230
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.455


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `952d4e9e12c194d228cf63d10b31c959edc327920598c352d26dcf1284463776`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ab36b663de63a40a5839be0af4fc1d53d37f9e78d4183a3de7f11063534632b8`; realized-scene SHA-256: `51caab5aeef033bda3880e250ac3d834b494dfd11f1563b679caeea40811318b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.14124,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.02985,"descend_1.depth":0.09718,"grasp_1.grip_force":25.49975,"lift_1.lift_height":0.21035,"lift_1.speed":0.09977},"optimized_scores":{"best_composite_score":0.1942,"best_fitness_score":0.5342,"best_task_score":0.12737},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":184.0,"contact_point_centroid":[0.44026,-0.02661,-0.00755],"force_p95":1.3584,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.75717,"mean_force":0.40304,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.44849,-0.02589,0.21898]},{"body_a":"world","body_b":"grasp_target","contact_count":129.0,"contact_point_centroid":[0.45597,-0.02549,-0.0011],"force_p95":0.27123,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48301,"mean_force":0.06159,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44467,-0.02576,0.04167]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18355.0,"contact_point_centroid":[0.44724,-0.04505,0.12152],"force_p95":0.07925,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28892,"mean_force":0.05469,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44736,-0.02586,0.11876]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":21109.0,"contact_point_centroid":[0.44888,-0.00684,0.12063],"force_p95":0.07339,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28813,"mean_force":0.04875,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44738,-0.02587,0.11888]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.0264,-0.00204],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1619,"mean_force":0.12606,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44705,-0.02583,0.04095]},{"body_a":"world","body_b":"grasp_target","contact_count":2160.0,"contact_point_centroid":[0.45856,-0.02632,-0.00193],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47862,-0.01162,0.22035]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1059.0,"contact_point_centroid":[0.45216,-0.04526,0.20232],"force_p95":0.07949,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.137,"mean_force":0.04925,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.45182,-0.02602,0.19964]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5315.0,"contact_point_centroid":[0.44687,-0.00669,0.04129],"force_p95":0.06929,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12901,"mean_force":0.04136,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44589,-0.02579,0.03983]},{"body_a":"world","body_b":"grasp_target","contact_count":2052.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45446,-0.02498,0.0908]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1224.0,"contact_point_centroid":[0.4539,-0.00704,0.20118],"force_p95":0.07284,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1215,"mean_force":0.04351,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.45185,-0.02602,0.19967]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4398.0,"contact_point_centroid":[0.4453,-0.04506,0.0426],"force_p95":0.07916,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09065,"mean_force":0.04915,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44589,-0.02579,0.03983]}],"total_contact_groups":11},"final_pose_error":0.0352,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.44901,-0.02539,0.02375],"final_tcp_position":[0.45311,-0.02607,0.20141],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1.75717,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":541.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2160.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.45824,-0.02397,0.13961],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11362,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":513.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2052.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45379,-0.02602,0.04746],"tcp_start":[0.45824,-0.02397,0.13961],"tcp_to_object_dist_end":0.02197,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":44.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45847,-0.02627,0.02584],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30371,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13692,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11513.0,"raw_peak_contact_force":0.1619,"tcp_end":[0.44586,-0.02579,0.0398],"tcp_start":[0.45379,-0.02602,0.04746],"tcp_to_object_dist_end":0.01882,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46126,-0.02671,0.18032],"object_pos_start":[0.45847,-0.02627,0.02584],"object_to_goal_dist_end":0.29679,"object_to_goal_dist_start":0.30371,"object_z_max":0.18012,"peak_contact_force":0.08204,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39593.0,"raw_peak_contact_force":0.48301,"tcp_end":[0.45311,-0.02607,0.20141],"tcp_start":[0.44586,-0.02579,0.0398],"tcp_to_object_dist_end":0.02262,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.44901,-0.02539,0.02375],"object_pos_start":[0.46126,-0.02671,0.18032],"object_to_goal_dist_end":0.3091,"object_to_goal_dist_start":0.29679,"object_z_max":0.18045,"peak_contact_force":0.18611,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2467.0,"raw_peak_contact_force":1.75717,"tcp_end":[0.44841,-0.02588,0.2275],"tcp_start":[0.45311,-0.02607,0.20141],"tcp_to_object_dist_end":0.20376,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `aa6ec658384c70fac6b4eb656cc8c53536c3d5c760368ab2b384dccf294e2c48`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90476,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07645,"descend_1.depth":0.0651,"grasp_1.grip_force":24.70197,"lift_1.lift_height":0.17385,"lift_1.speed":0.09168},"optimized_scores":{"best_composite_score":0.22971,"best_fitness_score":0.56971,"best_task_score":0.18808},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":120.0,"contact_point_centroid":[0.53489,0.00036,-0.01051],"force_p95":1.37082,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.43035,"mean_force":0.60006,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.53386,0.00092,0.19408]},{"body_a":"world","body_b":"grasp_target","contact_count":158.0,"contact_point_centroid":[0.54107,0.00113,-0.00112],"force_p95":0.40475,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61521,"mean_force":0.09633,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52885,0.00082,0.03389]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17931.0,"contact_point_centroid":[0.53341,0.02003,0.10761],"force_p95":0.07958,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33756,"mean_force":0.05602,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.5325,0.00089,0.10524]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19789.0,"contact_point_centroid":[0.53297,-0.01814,0.10346],"force_p95":0.07601,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31501,"mean_force":0.05144,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53218,0.00088,0.10134]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00115,-0.00203],"force_p95":0.13121,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.1527,"mean_force":0.1253,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53153,0.00087,0.03376]},{"body_a":"world","body_b":"grasp_target","contact_count":2248.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51706,0.00047,0.2177]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1158.0,"contact_point_centroid":[0.53882,0.02011,0.17924],"force_p95":0.07651,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12745,"mean_force":0.04548,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.53779,0.001,0.17712]},{"body_a":"world","body_b":"grasp_target","contact_count":3504.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53652,0.00098,0.0794]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1127.0,"contact_point_centroid":[0.53891,-0.01815,0.17932],"force_p95":0.07702,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12232,"mean_force":0.04673,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.53775,0.001,0.17706]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4149.0,"contact_point_centroid":[0.53129,0.02015,0.03467],"force_p95":0.07656,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0965,"mean_force":0.05218,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53024,0.00085,0.03226]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5327.0,"contact_point_centroid":[0.53063,-0.01819,0.03476],"force_p95":0.06263,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08703,"mean_force":0.04072,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53024,0.00085,0.03226]}],"total_contact_groups":11},"final_pose_error":0.02099,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.54761,0.00166,0.02274],"final_tcp_position":[0.53917,0.00102,0.17934],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.43035,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2248.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53688,0.00098,0.13649],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11072,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":876.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3504.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53883,0.00102,0.04234],"tcp_start":[0.53688,0.00098,0.13649],"tcp_to_object_dist_end":0.01722,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54418,0.00111,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25029,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13093,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11276.0,"raw_peak_contact_force":0.1527,"tcp_end":[0.53021,0.00085,0.03222],"tcp_start":[0.53883,0.00102,0.04234],"tcp_to_object_dist_end":0.01535,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54865,0.00101,0.16552],"object_pos_start":[0.54418,0.00111,0.02587],"object_to_goal_dist_end":0.18741,"object_to_goal_dist_start":0.25029,"object_z_max":0.16535,"peak_contact_force":0.082,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37878.0,"raw_peak_contact_force":0.61521,"tcp_end":[0.53917,0.00102,0.17934],"tcp_start":[0.53021,0.00085,0.03222],"tcp_to_object_dist_end":0.01676,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54761,0.00166,0.02274],"object_pos_start":[0.54865,0.00101,0.16552],"object_to_goal_dist_end":0.25064,"object_to_goal_dist_start":0.18741,"object_z_max":0.16563,"peak_contact_force":0.09925,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2405.0,"raw_peak_contact_force":1.43035,"tcp_end":[0.53378,0.00092,0.20317],"tcp_start":[0.53917,0.00102,0.17934],"tcp_to_object_dist_end":0.18096,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e1209649252ffcf03853fe0727696e22a1eda11729c6c1ae21659980557d7e98`; realized-scene SHA-256: `e32d7866764afb23ec7c7faebb4bcca0aa39fbf2f1ab61f3c9c527b297153af9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5305,0.03079,0.03]},{"name":"goal","value":[0.60153,0.17858,0.10809]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.5305,0.03079,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.60153,0.17858,0.10809]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34815,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04471,"descend_1.depth":0.03722,"grasp_1.grip_force":19.35302,"lift_1.lift_height":0.17253,"lift_1.speed":0.09898},"optimized_scores":{"best_composite_score":0.28067,"best_fitness_score":0.62067,"best_task_score":0.29069},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":117.0,"contact_point_centroid":[0.5232,0.03096,-0.0109],"force_p95":1.38883,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.46265,"mean_force":0.63007,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52103,0.02971,0.20078]},{"body_a":"world","body_b":"grasp_target","contact_count":148.0,"contact_point_centroid":[0.5277,0.02941,-0.00118],"force_p95":0.42552,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62164,"mean_force":0.08191,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51527,0.02971,0.03472]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":16371.0,"contact_point_centroid":[0.51959,0.04898,0.11068],"force_p95":0.08258,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34089,"mean_force":0.05873,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51917,0.02979,0.1079]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19827.0,"contact_point_centroid":[0.52068,0.01083,0.10807],"force_p95":0.07747,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31572,"mean_force":0.04992,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51905,0.02978,0.10638]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53053,0.0308,-0.00209],"force_p95":0.14781,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19347,"mean_force":0.12922,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51793,0.0299,0.03439]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1225.0,"contact_point_centroid":[0.52704,0.01102,0.18486],"force_p95":0.07467,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14033,"mean_force":0.0432,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5248,0.02998,0.1833]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5287.0,"contact_point_centroid":[0.51768,0.01078,0.0348],"force_p95":0.06895,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13881,"mean_force":0.0411,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51666,0.02982,0.03294]},{"body_a":"world","body_b":"grasp_target","contact_count":2348.0,"contact_point_centroid":[0.5305,0.03079,-0.00194],"force_p95":0.13103,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12283,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51069,0.01382,0.21817]},{"body_a":"world","body_b":"grasp_target","contact_count":3384.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52325,0.02939,0.07944]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1059.0,"contact_point_centroid":[0.52523,0.04923,0.18607],"force_p95":0.07889,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11388,"mean_force":0.04885,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52478,0.02998,0.18327]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4191.0,"contact_point_centroid":[0.51707,0.04912,0.03573],"force_p95":0.08287,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08552,"mean_force":0.05187,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51666,0.02982,0.03295]}],"total_contact_groups":11},"final_pose_error":0.01335,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.53102,0.02953,0.0235],"final_tcp_position":[0.52623,0.03006,0.18555],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":1.46265,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":588.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2348.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.52408,0.02818,0.13712],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11132,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":846.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3384.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.52512,0.03037,0.04262],"tcp_start":[0.52408,0.02818,0.13712],"tcp_to_object_dist_end":0.01745,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":43.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53043,0.03032,0.02569],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18392,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.14676,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11278.0,"raw_peak_contact_force":0.19347,"tcp_end":[0.51663,0.02981,0.03291],"tcp_start":[0.52512,0.03037,0.04262],"tcp_to_object_dist_end":0.01559,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":37.0,"n_steps":963.0,"n_steps_budget":1000.0,"object_pos_end":[0.53609,0.03076,0.17084],"object_pos_start":[0.53043,0.03032,0.02569],"object_to_goal_dist_end":0.17341,"object_to_goal_dist_start":0.18392,"object_z_max":0.17072,"peak_contact_force":0.0785,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":36346.0,"raw_peak_contact_force":0.62164,"tcp_end":[0.52623,0.03006,0.18555],"tcp_start":[0.51663,0.02981,0.03291],"tcp_to_object_dist_end":0.01773,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53102,0.02953,0.0235],"object_pos_start":[0.53609,0.03076,0.17084],"object_to_goal_dist_end":0.18532,"object_to_goal_dist_start":0.17341,"object_z_max":0.17088,"peak_contact_force":0.14239,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2401.0,"raw_peak_contact_force":1.46265,"tcp_end":[0.52095,0.02971,0.20967],"tcp_start":[0.52623,0.03006,0.18555],"tcp_to_object_dist_end":0.18644,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```