## Search State

- **Seed**: 7
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 3 | 0.3763 | 0.31 | ✅ accepted |
| 2 | approach → descend → grasp → lift → push → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1013 | 0.25 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 9 | -0.3188 | 0.17 | ❌ rejected |
| 0 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 3 | 0.3763 | 0.31 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`
- Frozen object start: [0.5125095466604667, 0.039721380096957554, 0.03]
- Frozen task target: [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]
- Goal object position: (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.6275685690245193, 0.17252071899905919, 0.14502494273668382)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5125095466604667, 0.039721380096957554, 0.03)
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
  frozen_object_start: [0.5125, 0.0397, 0.03]
  frozen_task_target: [0.6276, 0.1725, 0.145]
  frozen_object_starts: {'grasp_target': [0.5125095466604667, 0.039721380096957554, 0.03]}
  frozen_targets: {'place_target': [0.6275685690245193, 0.17252071899905919, 0.14502494273668382]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6

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

## Current Skill (Q=0.376) — your mutation base

```yaml
skill: grasp_place
skill_type: arm_gripper
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
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
  control: admittance_control
  termination: pose_tolerance
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
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
  control: position_control
  termination: pose_tolerance
  end_effector_action: open

```

## Design Metrics

- **Composite score**: 0.376
- **task_score** (E): 0.305
- **fitness_score**: 0.616  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.240

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1690 |
| descend_1 | 1.00 | 1.00 | 0.0835 |
| grasp_1 | 1.00 | 1.00 | 0.0127 |
| lift_1 | 0.33 | 1.00 | 0.1162 |
| release_1 | 0.33 | 1.00 | 0.1676 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.025, 0.138) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.025, 0.138)→(0.505, 0.022, 0.054) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.505, 0.022, 0.054)→(0.497, 0.022, 0.045) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 47.000 | 0.147 | 0.193 |
| lift_1 | lift | 0.33 / step_budget | (0.497, 0.022, 0.045)→(0.502, 0.022, 0.161) | (0.511, 0.022, 0.026)→(0.509, 0.022, 0.135) | 0.273→0.227 | 1.00 / 38.000 | 0.080 | 0.418 |
| release_1 | release | 0.33 / step_budget | (0.502, 0.022, 0.161)→(0.578, 0.159, 0.205) | (0.509, 0.022, 0.135)→(0.578, 0.172, 0.021) | 0.227→0.183 | 1.00 / 3.333 | 0.196 | 1.545 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.419
- phase_score: 0.328
- phase_breakdown.approach_1_score: 0.114
- phase_breakdown.descend_1_score: 0.872
- phase_breakdown.transport_arc_score: 0.000
- phase_breakdown.release_1_score: 0.570
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.673

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.673
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.419
- **Median Q (composite search score)**: 0.352
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.303


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `0b279c554151a1bc107b4895d67067efa2444eadb5a644f2482f57ab9ff93d7f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `079d4532bc3cff86c1b89933c7940f2ee474dc4233e12f8d134c76ceb3cd8d4d`; realized-scene SHA-256: `8a4edc50bf1a337961423afe5cdf858aa28147f944f8fcd30a2ce1adc75d1bd6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51251,0.03972,0.03]},{"name":"goal","value":[0.62757,0.17252,0.14502]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.51251,0.03972,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.62757,0.17252,0.14502]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.49333,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06589,"grasp_1.grip_force":14.2846,"lift_1.speed":0.05749},"optimized_scores":{"best_composite_score":0.43329,"best_fitness_score":0.67329,"best_task_score":0.419},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":478.0,"contact_point_centroid":[0.61129,0.18387,-0.00364],"force_p95":0.65324,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.13248,"mean_force":0.18928,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60986,0.15952,0.14589]},{"body_a":"world","body_b":"grasp_target","contact_count":204.0,"contact_point_centroid":[0.50832,0.03814,-0.00118],"force_p95":0.24703,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38968,"mean_force":0.07783,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49702,0.03865,0.04634]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13242.0,"contact_point_centroid":[0.54709,0.06987,0.13291],"force_p95":0.11714,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37264,"mean_force":0.07176,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54574,0.08876,0.13429]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19839.0,"contact_point_centroid":[0.49836,0.05778,0.09214],"force_p95":0.07489,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24386,"mean_force":0.05071,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49816,0.0386,0.08969]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15362.0,"contact_point_centroid":[0.54625,0.11069,0.13402],"force_p95":0.0973,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24329,"mean_force":0.06056,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54893,0.09218,0.13435]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21004.0,"contact_point_centroid":[0.49969,0.0195,0.09017],"force_p95":0.07865,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23899,"mean_force":0.04842,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49808,0.0386,0.08865]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51254,0.03974,-0.00208],"force_p95":0.14472,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18766,"mean_force":0.12857,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49987,0.0389,0.04603]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5550.0,"contact_point_centroid":[0.50025,0.0196,0.04683],"force_p95":0.07041,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15381,"mean_force":0.03982,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49866,0.03881,0.04468]},{"body_a":"world","body_b":"grasp_target","contact_count":2264.0,"contact_point_centroid":[0.51251,0.03972,-0.00194],"force_p95":0.13153,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50232,0.02888,0.2223]},{"body_a":"world","body_b":"grasp_target","contact_count":1048.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50604,0.04009,0.09595]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5143.0,"contact_point_centroid":[0.49895,0.05811,0.04771],"force_p95":0.07352,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07849,"mean_force":0.04293,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49867,0.03881,0.04469]}],"total_contact_groups":11},"final_pose_error":0.02093,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.6114,0.18386,0.01605],"final_tcp_position":[0.61301,0.16031,0.13624],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":1.13248,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":567.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2264.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.50747,0.04086,0.13838],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11248,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":262.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1048.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.50707,0.03951,0.05413],"tcp_start":[0.50747,0.04086,0.13838],"tcp_to_object_dist_end":0.02864,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51248,0.03933,0.02571],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21265,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14397,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12493.0,"raw_peak_contact_force":0.18766,"tcp_end":[0.49863,0.0388,0.04465],"tcp_start":[0.50707,0.03951,0.05413],"tcp_to_object_dist_end":0.02347,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50838,0.03939,0.11246],"object_pos_start":[0.51248,0.03933,0.02571],"object_to_goal_dist_end":0.18164,"object_to_goal_dist_start":0.21265,"object_z_max":0.11236,"peak_contact_force":0.07967,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":41047.0,"raw_peak_contact_force":0.38968,"tcp_end":[0.50201,0.03875,0.13772],"tcp_start":[0.49863,0.0388,0.04465],"tcp_to_object_dist_end":0.02605,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.6114,0.18386,0.01605],"object_pos_start":[0.50838,0.03939,0.11246],"object_to_goal_dist_end":0.13048,"object_to_goal_dist_start":0.18164,"object_z_max":0.11248,"peak_contact_force":0.12406,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":29082.0,"raw_peak_contact_force":1.13248,"tcp_end":[0.60952,0.15935,0.16208],"tcp_start":[0.50201,0.03875,0.13772],"tcp_to_object_dist_end":0.14809,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `a74f7c08b88460953bfa7e35b953cddf9278fdc17d2d4db8a2ea121b328e8b73`; realized-scene SHA-256: `f44a4a1356de6cb8b5dec75995af4354e38cafd01c85526c1c2a33c8dd2e5b1c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.4827,0.04873,0.03]},{"name":"goal","value":[0.58187,0.22885,0.23048]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.4827,0.04873,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.58187,0.22885,0.23048]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25269,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0397,"grasp_1.grip_force":19.55116,"lift_1.speed":0.05792},"optimized_scores":{"best_composite_score":0.34371,"best_fitness_score":0.58371,"best_task_score":0.24179},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":195.0,"contact_point_centroid":[0.54238,0.19032,-0.00712],"force_p95":1.13254,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.74232,"mean_force":0.36925,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.54719,0.17927,0.2182]},{"body_a":"world","body_b":"grasp_target","contact_count":185.0,"contact_point_centroid":[0.47877,0.0464,-0.0012],"force_p95":0.24111,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38525,"mean_force":0.07517,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46815,0.04736,0.04766]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20066.0,"contact_point_centroid":[0.46856,0.06645,0.09415],"force_p95":0.07509,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24394,"mean_force":0.05009,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46911,0.04732,0.09171]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20234.0,"contact_point_centroid":[0.47084,0.02824,0.09263],"force_p95":0.07898,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23389,"mean_force":0.05016,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46912,0.04732,0.09185]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15757.0,"contact_point_centroid":[0.50427,0.12725,0.16569],"force_p95":0.09915,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2305,"mean_force":0.06135,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50644,0.10858,0.16551]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15048.0,"contact_point_centroid":[0.50917,0.08874,0.163],"force_p95":0.10351,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22837,"mean_force":0.06589,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5056,0.10716,0.16484]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48273,0.04878,-0.0021],"force_p95":0.15092,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19452,"mean_force":0.13,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47082,0.04764,0.04719]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5099.0,"contact_point_centroid":[0.47153,0.02834,0.04683],"force_p95":0.07648,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1624,"mean_force":0.04365,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46965,0.04753,0.04597]},{"body_a":"world","body_b":"grasp_target","contact_count":2304.0,"contact_point_centroid":[0.4827,0.04873,-0.00194],"force_p95":0.13146,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48969,0.03261,0.22392]},{"body_a":"world","body_b":"grasp_target","contact_count":1072.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47785,0.04864,0.09666]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5146.0,"contact_point_centroid":[0.46878,0.06674,0.04956],"force_p95":0.07583,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07785,"mean_force":0.04281,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46965,0.04753,0.04597]}],"total_contact_groups":11},"final_pose_error":0.0659,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.54844,0.18877,0.02403],"final_tcp_position":[0.54981,0.18016,0.19976],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.74232,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":577.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2304.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.48027,0.04915,0.13942],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.11343,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":268.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1072.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.4778,0.04834,0.05454],"tcp_start":[0.48027,0.04915,0.13942],"tcp_to_object_dist_end":0.02894,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48271,0.04826,0.02564],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.29053,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.15048,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12045.0,"raw_peak_contact_force":0.19452,"tcp_end":[0.46962,0.04752,0.04594],"tcp_start":[0.4778,0.04834,0.05454],"tcp_to_object_dist_end":0.02416,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47835,0.04846,0.11408],"object_pos_start":[0.48271,0.04826,0.02564],"object_to_goal_dist_end":0.23835,"object_to_goal_dist_start":0.29053,"object_z_max":0.11398,"peak_contact_force":0.07965,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40485.0,"raw_peak_contact_force":0.38525,"tcp_end":[0.47284,0.04754,0.14054],"tcp_start":[0.46962,0.04752,0.04594],"tcp_to_object_dist_end":0.02705,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54844,0.18877,0.02403],"object_pos_start":[0.47835,0.04846,0.11408],"object_to_goal_dist_end":0.21295,"object_to_goal_dist_start":0.23835,"object_z_max":0.16651,"peak_contact_force":0.22093,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":31000.0,"raw_peak_contact_force":1.74232,"tcp_end":[0.54712,0.17923,0.2267],"tcp_start":[0.47284,0.04754,0.14054],"tcp_to_object_dist_end":0.2029,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b1a72366a9c9a56aa2e80fc4399e157c8281abf492ab3c1ede02058762a86ed7`; realized-scene SHA-256: `0143f6b0f71a2b9dc1b332d50c0ca91b210f169a33e3f94f972cb0659a69dba8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53702,-0.02132,0.03]},{"name":"goal","value":[0.61031,0.22775,0.20741]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.53702,-0.02132,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.61031,0.22775,0.20741]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91034,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07077,"grasp_1.grip_force":14.29764,"lift_1.speed":0.09985},"optimized_scores":{"best_composite_score":0.35192,"best_fitness_score":0.59192,"best_task_score":0.25516},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":188.0,"contact_point_centroid":[0.5658,0.14558,-0.00738],"force_p95":1.23192,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.75966,"mean_force":0.38634,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57614,0.13747,0.21693]},{"body_a":"world","body_b":"grasp_target","contact_count":146.0,"contact_point_centroid":[0.534,-0.01998,-0.00119],"force_p95":0.31663,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47949,"mean_force":0.07533,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52125,-0.02027,0.04546]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19146.0,"contact_point_centroid":[0.52571,-0.03967,0.12495],"force_p95":0.07493,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31079,"mean_force":0.05302,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52515,-0.0205,0.12215]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20738.0,"contact_point_centroid":[0.52622,-0.00141,0.12035],"force_p95":0.07565,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30829,"mean_force":0.04985,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52486,-0.02048,0.11853]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16927.0,"contact_point_centroid":[0.55593,0.03637,0.19878],"force_p95":0.09764,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22773,"mean_force":0.05918,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55276,0.05503,0.19878]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17159.0,"contact_point_centroid":[0.55228,0.0743,0.19883],"force_p95":0.09524,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21866,"mean_force":0.05795,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.55287,0.05539,0.19877]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53706,-0.02135,-0.00209],"force_p95":0.14803,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19738,"mean_force":0.12964,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52382,-0.0203,0.04514]},{"body_a":"world","body_b":"grasp_target","contact_count":2312.0,"contact_point_centroid":[0.53702,-0.02132,-0.00194],"force_p95":0.13126,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12284,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51419,0.00178,0.21554]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5789.0,"contact_point_centroid":[0.52321,-0.00113,0.04665],"force_p95":0.06152,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.13241,"mean_force":0.03802,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52258,-0.02028,0.04369]},{"body_a":"world","body_b":"grasp_target","contact_count":1004.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5296,-0.018,0.09411]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4691.0,"contact_point_centroid":[0.52282,-0.03961,0.04738],"force_p95":0.07291,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07614,"mean_force":0.04686,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52258,-0.02028,0.0437]}],"total_contact_groups":11},"final_pose_error":0.09535,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.57431,0.14434,0.02377],"final_tcp_position":[0.57888,0.13815,0.19878],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.75966,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":579.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2312.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53046,-0.01569,0.13497],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1093,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":251.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1004.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.5312,-0.02037,0.05389],"tcp_start":[0.53046,-0.01569,0.13497],"tcp_to_object_dist_end":0.02849,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53698,-0.02089,0.02566],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3166,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14685,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12280.0,"raw_peak_contact_force":0.19738,"tcp_end":[0.52255,-0.02028,0.04366],"tcp_start":[0.5312,-0.02037,0.05389],"tcp_to_object_dist_end":0.02308,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53999,-0.02127,0.17968],"object_pos_start":[0.53698,-0.02089,0.02566],"object_to_goal_dist_end":0.26025,"object_to_goal_dist_start":0.3166,"object_z_max":0.17949,"peak_contact_force":0.07923,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40030.0,"raw_peak_contact_force":0.47949,"tcp_end":[0.5322,-0.02077,0.20417],"tcp_start":[0.52255,-0.02028,0.04366],"tcp_to_object_dist_end":0.02571,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57431,0.14434,0.02377],"object_pos_start":[0.53999,-0.02127,0.17968],"object_to_goal_dist_end":0.20488,"object_to_goal_dist_start":0.26025,"object_z_max":0.17982,"peak_contact_force":0.24273,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":34274.0,"raw_peak_contact_force":1.75966,"tcp_end":[0.57608,0.13743,0.22534],"tcp_start":[0.5322,-0.02077,0.20417],"tcp_to_object_dist_end":0.20169,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```