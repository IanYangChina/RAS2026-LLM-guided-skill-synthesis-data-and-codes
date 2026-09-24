## Search State

- **Seed**: 7
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → push → descend → release | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | position_control | admittance_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 7 | 0.1013 | 0.25 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach | arc_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 9 | -0.3188 | 0.17 | ❌ rejected |
| 0 | approach → descend → grasp → lift → release | arc_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 3 | 0.3763 | 0.31 | ✅ accepted |

**Proposal policy**: task_score is 0.25 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.101) — your mutation base

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

- **Composite score**: 0.101
- **task_score** (E): 0.248
- **fitness_score**: 0.601  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.500

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2672 |
| descend_1 | 1.00 | 1.00 | 0.0044 |
| grasp_1 | 1.00 | 1.00 | 0.0121 |
| lift_1 | 1.00 | 1.00 | 0.1016 |
| transport_arc | 1.00 | 1.00 | 0.2301 |
| descend_to_goal | 1.00 | 1.00 | 0.0502 |
| release_1 | 1.00 | 1.00 | 0.0205 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.026, 0.037) | (0.511, 0.022, 0.030)→(0.511, 0.022, 0.026) | 0.271→0.273 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.506, 0.026, 0.037)→(0.505, 0.025, 0.033) | (0.511, 0.022, 0.026)→(0.511, 0.022, 0.026) | 0.273→0.273 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.505, 0.025, 0.033)→(0.497, 0.024, 0.024) | (0.511, 0.022, 0.026)→(0.511, 0.024, 0.025) | 0.273→0.272 | 1.00 / 42.000 | 0.178 | 0.249 |
| lift_1 | lift | 1.00 / step_budget | (0.497, 0.024, 0.024)→(0.504, 0.024, 0.126) | (0.511, 0.024, 0.025)→(0.520, 0.024, 0.113) | 0.272→0.225 | 1.00 / 24.333 | 0.116 | 0.665 |
| transport_arc | push | 1.00 / step_budget | (0.504, 0.024, 0.126)→(0.595, 0.190, 0.241) | (0.520, 0.024, 0.113)→(0.546, 0.104, 0.016) | 0.225→0.225 | 1.00 / 8.000 | 0.123 | 1.601 |
| descend_to_goal | descend | 1.00 / step_budget | (0.595, 0.190, 0.241)→(0.602, 0.205, 0.195) | (0.546, 0.104, 0.016)→(0.546, 0.104, 0.016) | 0.225→0.225 | 1.00 / 8.333 | 94251.108 | 0.123 |
| release_1 | release | 1.00 / step_budget | (0.602, 0.205, 0.195)→(0.596, 0.203, 0.215) | (0.546, 0.104, 0.016)→(0.546, 0.104, 0.016) | 0.225→0.225 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: 1.000
- terminal_score: 0.403
- phase_score: 0.770
- phase_breakdown.approach_1_score: 0.820
- phase_breakdown.descend_1_score: 0.703
- phase_breakdown.transport_arc_score: 0.727
- phase_breakdown.release_1_score: 0.723
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.679

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.679
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.403
- **Median Q (composite search score)**: 0.083
- **K-run variance**: 0.0033
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.361


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30952,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.03197,"descend_1.speed":0.05005,"descend_to_goal.speed":0.0625,"lift_1.lift_height":0.10729,"lift_1.speed":0.08312,"transport_arc.speed":0.09362,"transport_arc.transport_height":0.0012},"optimized_scores":{"best_composite_score":0.17895,"best_fitness_score":0.67895,"best_task_score":0.40285},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":685.0,"contact_point_centroid":[0.59004,0.1491,-0.00313],"force_p95":0.64053,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.40629,"mean_force":0.18351,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"push","tcp_position_centroid":[0.59855,0.14372,0.1439]},{"body_a":"world","body_b":"grasp_target","contact_count":164.0,"contact_point_centroid":[0.51011,0.04111,-0.00127],"force_p95":0.47082,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65492,"mean_force":0.08964,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49704,0.04056,0.02623]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7279.0,"contact_point_centroid":[0.50325,0.05931,0.0667],"force_p95":0.11135,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31079,"mean_force":0.07509,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50003,0.04039,0.06449]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8091.0,"contact_point_centroid":[0.50319,0.02168,0.06556],"force_p95":0.10467,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28534,"mean_force":0.06858,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49996,0.04039,0.06383]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3478.0,"contact_point_centroid":[0.5379,0.08982,0.1306],"force_p95":0.15608,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27291,"mean_force":0.09734,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"push","tcp_position_centroid":[0.53332,0.07184,0.13259]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2887.0,"contact_point_centroid":[0.53603,0.05171,0.13055],"force_p95":0.17848,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2591,"mean_force":0.10717,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"push","tcp_position_centroid":[0.53169,0.07004,0.13199]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.51254,0.03999,-0.00209],"force_p95":0.15007,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22657,"mean_force":0.13004,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4995,0.0408,0.02596]},{"body_a":"world","body_b":"grasp_target","contact_count":3608.0,"contact_point_centroid":[0.51251,0.03972,-0.00196],"force_p95":0.12566,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12276,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50225,0.03644,0.17139]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4071.0,"contact_point_centroid":[0.49923,0.05991,0.02734],"force_p95":0.07834,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1317,"mean_force":0.05191,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49831,0.0407,0.02468]},{"body_a":"world","body_b":"grasp_target","contact_count":1968.0,"contact_point_centroid":[0.58984,0.14945,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12278,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.6196,0.16811,0.13544]},{"body_a":"world","body_b":"grasp_target","contact_count":92.0,"contact_point_centroid":[0.51251,0.03972,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50651,0.04182,0.03605]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.58984,0.14945,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.61774,0.16911,0.13616]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4962.0,"contact_point_centroid":[0.49919,0.02159,0.02658],"force_p95":0.07034,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08759,"mean_force":0.04471,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.49832,0.0407,0.02469]},{"body_a":"left_finger","body_b":"right_finger","contact_count":432.0,"contact_point_centroid":[0.60617,0.15164,0.14509],"force_p95":0.0145,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01638,"mean_force":0.01114,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"push","tcp_position_centroid":[0.60577,0.15163,0.14286]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2080.0,"contact_point_centroid":[0.62,0.16813,0.13773],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.01054,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.61959,0.1681,0.13544]},{"body_a":"left_finger","body_b":"right_finger","contact_count":217.0,"contact_point_centroid":[0.62124,0.17011,0.13524],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01099,"mean_force":0.01025,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.62084,0.17008,0.13282]}],"total_contact_groups":16},"final_pose_error":0.01078,"key_states":{"actual_goal_position":[0.62757,0.17252,0.14502],"final_object_position":[0.58984,0.14945,0.01602],"final_tcp_position":[0.62234,0.17051,0.13582],"realised_goal_position":[0.62757,0.17252,0.14502],"realised_object_initial_position":[0.51251,0.03972,0.03]},"peak_contact_force":273004.30042,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":903.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.03],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21001,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3608.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.50727,0.04217,0.03807],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01337,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":23.0,"n_steps_budget":1000.0,"object_pos_end":[0.51251,0.03972,0.02602],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21222,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":92.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.50648,0.04149,0.03355],"tcp_start":[0.50727,0.04217,0.03807],"tcp_to_object_dist_end":0.00981,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51238,0.04079,0.0257],"object_pos_start":[0.51251,0.03972,0.02602],"object_to_goal_dist_end":0.21181,"object_to_goal_dist_start":0.21222,"object_z_max":0.02602,"peak_contact_force":0.14435,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10833.0,"raw_peak_contact_force":0.22657,"subtask_id":"grasp_1","tcp_end":[0.49828,0.0407,0.02465],"tcp_start":[0.50648,0.04149,0.03355],"tcp_to_object_dist_end":0.01413,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":22.0,"n_steps":536.0,"n_steps_budget":600.0,"object_pos_end":[0.5262,0.04054,0.11042],"object_pos_start":[0.51238,0.04079,0.0257],"object_to_goal_dist_end":0.16998,"object_to_goal_dist_start":0.21181,"object_z_max":0.1103,"peak_contact_force":0.11552,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15534.0,"raw_peak_contact_force":0.65492,"tcp_end":[0.50727,0.04044,0.11976],"tcp_start":[0.49828,0.0407,0.02465],"tcp_to_object_dist_end":0.0211,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":572.0,"n_steps_budget":630.0,"object_pos_end":[0.58983,0.14944,0.01602],"object_pos_start":[0.5262,0.04054,0.11042],"object_to_goal_dist_end":0.13638,"object_to_goal_dist_start":0.16998,"object_z_max":0.12114,"peak_contact_force":0.12279,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":7482.0,"raw_peak_contact_force":1.40629,"subtask_id":"transport_arc","tcp_end":[0.61587,0.16289,0.14015],"tcp_start":[0.50727,0.04044,0.11976],"tcp_to_object_dist_end":0.12754,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":492.0,"n_steps_budget":1000.0,"object_pos_end":[0.58984,0.14945,0.01602],"object_pos_start":[0.58983,0.14944,0.01602],"object_to_goal_dist_end":0.13638,"object_to_goal_dist_start":0.13638,"object_z_max":0.01602,"peak_contact_force":273004.30042,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4048.0,"raw_peak_contact_force":0.12278,"tcp_end":[0.62234,0.17051,0.13582],"tcp_start":[0.61587,0.16289,0.14015],"tcp_to_object_dist_end":0.12591,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.58984,0.14945,0.01602],"object_pos_start":[0.58984,0.14945,0.01602],"object_to_goal_dist_end":0.13638,"object_to_goal_dist_start":0.13638,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1017.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.61592,0.16853,0.15553],"tcp_start":[0.62234,0.17051,0.13582],"tcp_to_object_dist_end":0.14321,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08338,"descend_1.speed":0.05144,"descend_to_goal.speed":0.02596,"lift_1.lift_height":0.12764,"lift_1.speed":0.03076,"transport_arc.speed":0.08804,"transport_arc.transport_height":0.07332},"optimized_scores":{"best_composite_score":0.08313,"best_fitness_score":0.58313,"best_task_score":0.20585},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1828.0,"contact_point_centroid":[0.51363,0.15417,-0.00266],"force_p95":0.25377,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.89146,"mean_force":0.153,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"push","tcp_position_centroid":[0.54422,0.1679,0.26351]},{"body_a":"world","body_b":"grasp_target","contact_count":160.0,"contact_point_centroid":[0.47981,0.0494,-0.00115],"force_p95":0.45356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63621,"mean_force":0.08742,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46898,0.04902,0.02837]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4082.0,"contact_point_centroid":[0.48899,0.05,0.15831],"force_p95":0.16605,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3048,"mean_force":0.08857,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"push","tcp_position_centroid":[0.48528,0.06854,0.15915]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17427.0,"contact_point_centroid":[0.47245,0.06785,0.07661],"force_p95":0.08542,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30003,"mean_force":0.05832,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4712,0.04877,0.07472]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4526.0,"contact_point_centroid":[0.4906,0.08928,0.16156],"force_p95":0.16362,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28,"mean_force":0.08638,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"push","tcp_position_centroid":[0.48655,0.0708,0.1626]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18174.0,"contact_point_centroid":[0.47233,0.02977,0.07606],"force_p95":0.08385,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26698,"mean_force":0.0561,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47115,0.04877,0.07419]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.48269,0.04883,-0.00205],"force_p95":0.13688,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18518,"mean_force":0.12657,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47138,0.0493,0.0279]},{"body_a":"world","body_b":"grasp_target","contact_count":3040.0,"contact_point_centroid":[0.4827,0.04873,-0.00195],"force_p95":0.12784,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12279,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48884,0.0405,0.17265]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.4827,0.04873,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47826,0.05031,0.03708]},{"body_a":"world","body_b":"grasp_target","contact_count":644.0,"contact_point_centroid":[0.51368,0.15425,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.57533,0.22171,0.26608]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.51368,0.15425,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57406,0.2237,0.23892]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5066.0,"contact_point_centroid":[0.47004,0.06845,0.02965],"force_p95":0.06573,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09127,"mean_force":0.04301,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47026,0.04919,0.02677]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5398.0,"contact_point_centroid":[0.4699,0.02995,0.02932],"force_p95":0.06392,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08588,"mean_force":0.04109,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.47026,0.04919,0.02677]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1765.0,"contact_point_centroid":[0.54724,0.17239,0.269],"force_p95":0.01179,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01547,"mean_force":0.01064,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"push","tcp_position_centroid":[0.54689,0.17237,0.26681]},{"body_a":"left_finger","body_b":"right_finger","contact_count":223.0,"contact_point_centroid":[0.5765,0.22467,0.23719],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01253,"mean_force":0.01001,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.57597,0.22464,0.23488]},{"body_a":"left_finger","body_b":"right_finger","contact_count":684.0,"contact_point_centroid":[0.57574,0.22171,0.26851],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01104,"mean_force":0.01048,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.57532,0.22168,0.2663]}],"total_contact_groups":16},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.58187,0.22885,0.23048],"final_object_position":[0.51368,0.15425,0.01602],"final_tcp_position":[0.57735,0.22514,0.23853],"realised_goal_position":[0.58187,0.22885,0.23048],"realised_object_initial_position":[0.4827,0.04873,0.03]},"peak_contact_force":1.89146,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":761.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.03],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28719,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3040.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47915,0.05061,0.03899],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.01358,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":22.0,"n_steps_budget":1000.0,"object_pos_end":[0.4827,0.04873,0.02602],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28998,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":88.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.47805,0.05005,0.03472],"tcp_start":[0.47915,0.05061,0.03899],"tcp_to_object_dist_end":0.00995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48257,0.04918,0.02582],"object_pos_start":[0.4827,0.04873,0.02602],"object_to_goal_dist_end":0.28988,"object_to_goal_dist_start":0.28998,"object_z_max":0.02602,"peak_contact_force":0.13538,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12264.0,"raw_peak_contact_force":0.18518,"subtask_id":"grasp_1","tcp_end":[0.47023,0.04919,0.02674],"tcp_start":[0.47805,0.05005,0.03472],"tcp_to_object_dist_end":0.01237,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48995,0.04873,0.11562],"object_pos_start":[0.48257,0.04918,0.02582],"object_to_goal_dist_end":0.23256,"object_to_goal_dist_start":0.28988,"object_z_max":0.11551,"peak_contact_force":0.08836,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":35761.0,"raw_peak_contact_force":0.63621,"tcp_end":[0.47632,0.04877,0.1271],"tcp_start":[0.47023,0.04919,0.02674],"tcp_to_object_dist_end":0.01782,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":932.0,"n_steps_budget":990.0,"object_pos_end":[0.51368,0.15425,0.01602],"object_pos_start":[0.48995,0.04873,0.11562],"object_to_goal_dist_end":0.23709,"object_to_goal_dist_start":0.23256,"object_z_max":0.18339,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12201.0,"raw_peak_contact_force":1.89146,"subtask_id":"transport_arc","tcp_end":[0.57456,0.21899,0.29231],"tcp_start":[0.47632,0.04877,0.1271],"tcp_to_object_dist_end":0.29023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":161.0,"n_steps_budget":1000.0,"object_pos_end":[0.51368,0.15425,0.01602],"object_pos_start":[0.51368,0.15425,0.01602],"object_to_goal_dist_end":0.23709,"object_to_goal_dist_start":0.23709,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1328.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.57735,0.22514,0.23853],"tcp_start":[0.57456,0.21899,0.29231],"tcp_to_object_dist_end":0.24205,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.51368,0.15425,0.01602],"object_pos_start":[0.51368,0.15425,0.01602],"object_to_goal_dist_end":0.23709,"object_to_goal_dist_start":0.23709,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.57297,0.22314,0.25866],"tcp_start":[0.57735,0.22514,0.23853],"tcp_to_object_dist_end":0.2591,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78771,"average_solve_count":179.0,"average_success_count":179.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0433,"descend_1.speed":0.04929,"descend_to_goal.speed":0.06041,"lift_1.lift_height":0.14961,"lift_1.speed":0.03346,"transport_arc.speed":0.08298,"transport_arc.transport_height":0.10167},"optimized_scores":{"best_composite_score":0.04168,"best_fitness_score":0.54168,"best_task_score":0.13466},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3118.0,"contact_point_centroid":[0.53507,0.00833,-0.00226],"force_p95":0.12713,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.50675,"mean_force":0.13706,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"push","tcp_position_centroid":[0.56446,0.09748,0.23895]},{"body_a":"world","body_b":"grasp_target","contact_count":221.0,"contact_point_centroid":[0.53442,-0.01427,-0.00149],"force_p95":0.40083,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70409,"mean_force":0.1368,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.51974,-0.01705,0.0241]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":14236.0,"contact_point_centroid":[0.52589,-0.03563,0.07053],"force_p95":0.11741,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3825,"mean_force":0.07506,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52262,-0.01704,0.06992]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13017.0,"contact_point_centroid":[0.52709,0.00161,0.07569],"force_p95":0.12342,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36217,"mean_force":0.07908,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52315,-0.01704,0.07486]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53736,-0.0205,-0.00239],"force_p95":0.27359,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33463,"mean_force":0.17969,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52275,-0.0171,0.0233]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1364.0,"contact_point_centroid":[0.53275,-0.02442,0.13768],"force_p95":0.15434,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32016,"mean_force":0.1087,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"push","tcp_position_centroid":[0.52999,-0.00651,0.14215]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1219.0,"contact_point_centroid":[0.53251,0.00953,0.13506],"force_p95":0.16695,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28972,"mean_force":0.11149,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"push","tcp_position_centroid":[0.52952,-0.00854,0.13962]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":3597.0,"contact_point_centroid":[0.52365,0.00193,0.02501],"force_p95":0.11546,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20637,"mean_force":0.07254,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.5215,-0.01709,0.0219]},{"body_a":"world","body_b":"grasp_target","contact_count":3560.0,"contact_point_centroid":[0.53702,-0.02132,-0.00196],"force_p95":0.12598,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12276,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51442,0.00791,0.16426]},{"body_a":"world","body_b":"grasp_target","contact_count":88.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52995,-0.01652,0.03363]},{"body_a":"world","body_b":"grasp_target","contact_count":1024.0,"contact_point_centroid":[0.53497,0.00835,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59946,0.20368,0.24983]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.53497,0.00835,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60124,0.21915,0.21105]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4547.0,"contact_point_centroid":[0.52359,-0.03652,0.02361],"force_p95":0.10288,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11718,"mean_force":0.06277,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52152,-0.01709,0.02193]},{"body_a":"left_finger","body_b":"right_finger","contact_count":3069.0,"contact_point_centroid":[0.56702,0.10395,0.24647],"force_p95":0.01119,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01655,"mean_force":0.01055,"phase_index":4.0,"phase_name":"transport_arc","phase_type":"push","tcp_position_centroid":[0.56668,0.10394,0.24418]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1090.0,"contact_point_centroid":[0.59971,0.20368,0.25215],"force_p95":0.01097,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01276,"mean_force":0.01047,"phase_index":5.0,"phase_name":"descend_to_goal","phase_type":"descend","tcp_position_centroid":[0.59945,0.20367,0.24986]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.60408,0.22021,0.20966],"force_p95":0.01092,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01094,"mean_force":0.00993,"phase_index":6.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.60345,0.22019,0.20756]}],"total_contact_groups":16},"final_pose_error":0.00982,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.53497,0.00835,0.01602],"final_tcp_position":[0.60495,0.22048,0.21126],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":9748.89972,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":891.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3560.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53061,-0.01603,0.03534],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.0125,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":22.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":88.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.52998,-0.01707,0.03149],"tcp_start":[0.53061,-0.01603,0.03534],"tcp_to_object_dist_end":0.00988,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53747,-0.01717,0.02466],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31415,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.25425,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9944.0,"raw_peak_contact_force":0.33463,"subtask_id":"grasp_1","tcp_end":[0.52147,-0.01708,0.02188],"tcp_start":[0.52998,-0.01707,0.03149],"tcp_to_object_dist_end":0.01624,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54351,-0.01723,0.11209],"object_pos_start":[0.53747,-0.01717,0.02466],"object_to_goal_dist_end":0.27123,"object_to_goal_dist_start":0.31415,"object_z_max":0.11204,"peak_contact_force":0.14311,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":27474.0,"raw_peak_contact_force":0.70409,"tcp_end":[0.52924,-0.01707,0.13039],"tcp_start":[0.52147,-0.01708,0.02188],"tcp_to_object_dist_end":0.02321,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53497,0.00835,0.01602],"object_pos_start":[0.54351,-0.01723,0.11209],"object_to_goal_dist_end":0.30075,"object_to_goal_dist_start":0.27123,"object_z_max":0.12952,"peak_contact_force":0.12263,"phase_name":"transport_arc","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8770.0,"raw_peak_contact_force":1.50675,"subtask_id":"transport_arc","tcp_end":[0.59563,0.18845,0.29004],"tcp_start":[0.52924,-0.01707,0.13039],"tcp_to_object_dist_end":0.33347,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":256.0,"n_steps_budget":1000.0,"object_pos_end":[0.53497,0.00835,0.01602],"object_pos_start":[0.53497,0.00835,0.01602],"object_to_goal_dist_end":0.30075,"object_to_goal_dist_start":0.30075,"object_z_max":0.01602,"peak_contact_force":9748.89972,"phase_name":"descend_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2114.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.60495,0.22048,0.21126],"tcp_start":[0.59563,0.18845,0.29004],"tcp_to_object_dist_end":0.29668,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53497,0.00835,0.01602],"object_pos_start":[0.53497,0.00835,0.01602],"object_to_goal_dist_end":0.30075,"object_to_goal_dist_start":0.30075,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.12263,"subtask_id":"release_1","tcp_end":[0.59997,0.21854,0.23047],"tcp_start":[0.60495,0.22048,0.21126],"tcp_to_object_dist_end":0.30724,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```