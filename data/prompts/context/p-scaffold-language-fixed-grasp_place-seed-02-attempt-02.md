## Search State

- **Seed**: 2
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | admittance_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | 3 | 0.3009 | 0.16 | ✅ accepted |
| 1 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | admittance_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | 3 | 0.3009 | 0.15 | ✅ accepted |
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | admittance_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | 3 | 0.3008 | 0.15 | ✅ accepted |

**Proposal policy**: task_score is 0.16 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`
- Frozen object start: [0.4761612134249316, -0.02015088565858767, 0.03]
- Frozen task target: [0.631422574059428, 0.1591915942135097, 0.1900150788948481]
- Goal object position: (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.4761612134249316, -0.02015088565858767, 0.03)
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
  frozen_object_start: [0.4762, -0.0202, 0.03]
  frozen_task_target: [0.6314, 0.1592, 0.19]
  frozen_object_starts: {'grasp_target': [0.4761612134249316, -0.02015088565858767, 0.03]}
  frozen_targets: {'place_target': [0.631422574059428, 0.1591915942135097, 0.1900150788948481]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a

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

## Current Skill (Q=0.301) — your mutation base

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
- id: release_1
  type: release
  control: admittance_control
  termination: time_limit
  end_effector_action: open

```

## Design Metrics

- **Composite score**: 0.301
- **task_score** (E): 0.155
- **fitness_score**: 0.541  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.240

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1244 |
| descend_1 | 1.00 | 1.00 | 0.1337 |
| grasp_1 | 1.00 | 1.00 | 0.0122 |
| lift_1 | 1.00 | 1.00 | 0.1630 |
| release_1 | 1.00 | 1.00 | 0.0256 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, -0.012, 0.188) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 10.982 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.493, -0.012, 0.188)→(0.488, -0.015, 0.054) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.488, -0.015, 0.054)→(0.480, -0.015, 0.046) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 44.333 | 0.137 | 0.168 |
| lift_1 | lift | 1.00 / step_budget | (0.480, -0.015, 0.046)→(0.489, -0.015, 0.208) | (0.493, -0.015, 0.026)→(0.495, -0.015, 0.181) | 0.281→0.240 | 1.00 / 35.333 | 0.090 | 0.436 |
| release_1 | release | 1.00 / step_budget | (0.489, -0.015, 0.208)→(0.484, -0.015, 0.233) | (0.495, -0.015, 0.181)→(0.488, -0.001, 0.014) | 0.240→0.281 | 1.00 / 2.333 | 0.207 | 1.786 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.184
- phase_score: 0.247
- phase_breakdown.transport_arc_score: 0.000
- phase_breakdown.approach_1_score: 0.150
- phase_breakdown.descend_1_score: 0.867
- phase_breakdown.release_1_score: 0.019
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.557

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.557
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.184
- **Median Q (composite search score)**: 0.298
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.254


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `dde525b5f1d1bd9dc458c18c8bb170b8849a392c0909c5e3e8e19baca2e18946`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3eaf951d4314ad541ffae42f4c615c856bb77d128e3ae1cab520a1988305ba67`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60526,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14339,"approach_1.speed":0.06098,"grasp_1.grip_force":22.71031},"optimized_scores":{"best_composite_score":0.29846,"best_fitness_score":0.53846,"best_task_score":0.15126},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":121.0,"contact_point_centroid":[0.47122,0.02069,-0.00925],"force_p95":1.1869,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.98306,"mean_force":0.5612,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.46732,-0.01984,0.23079]},{"body_a":"world","body_b":"grasp_target","contact_count":130.0,"contact_point_centroid":[0.47316,-0.01915,-0.00112],"force_p95":0.28824,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41967,"mean_force":0.06011,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4621,-0.01967,0.04809]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19846.0,"contact_point_centroid":[0.46573,-0.03894,0.12697],"force_p95":0.07341,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28296,"mean_force":0.05141,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46539,-0.01978,0.12517]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20166.0,"contact_point_centroid":[0.46665,-0.00068,0.12531],"force_p95":0.07672,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2816,"mean_force":0.0511,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46535,-0.01978,0.12452]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1645.0,"contact_point_centroid":[0.47156,0.00021,0.20743],"force_p95":0.10168,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19324,"mean_force":0.05761,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.47013,-0.01991,0.20764]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02022,-0.00204],"force_p95":0.13696,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17025,"mean_force":0.12624,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46448,-0.01971,0.0475]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1116.0,"contact_point_centroid":[0.4711,-0.039,0.20882],"force_p95":0.07535,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15838,"mean_force":0.04487,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.47075,-0.01993,0.20822]},{"body_a":"world","body_b":"grasp_target","contact_count":1876.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12289,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48665,-0.0088,0.22708]},{"body_a":"world","body_b":"grasp_target","contact_count":1248.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47181,-0.01897,0.10353]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5094.0,"contact_point_centroid":[0.46484,-0.00052,0.04761],"force_p95":0.06735,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09714,"mean_force":0.04336,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46331,-0.01968,0.04632]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4882.0,"contact_point_centroid":[0.4635,-0.03892,0.0492],"force_p95":0.07127,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.085,"mean_force":0.04465,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46331,-0.01968,0.04632]}],"total_contact_groups":11},"final_pose_error":0.01637,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.47048,0.01948,0.00335],"final_tcp_position":[0.47193,-0.01996,0.21],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":1.98306,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":470.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1876.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.47463,-0.01818,0.15307],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12707,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":312.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1248.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47143,-0.01982,0.05465],"tcp_start":[0.47463,-0.01818,0.15307],"tcp_to_object_dist_end":0.02902,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47609,-0.02006,0.02582],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28848,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.137,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11776.0,"raw_peak_contact_force":0.17025,"tcp_end":[0.46328,-0.01968,0.04629],"tcp_start":[0.47143,-0.01982,0.05465],"tcp_to_object_dist_end":0.02414,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47858,-0.02046,0.18289],"object_pos_start":[0.47609,-0.02006,0.02582],"object_to_goal_dist_end":0.23597,"object_to_goal_dist_start":0.28848,"object_z_max":0.1827,"peak_contact_force":0.08113,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40142.0,"raw_peak_contact_force":0.41967,"tcp_end":[0.47193,-0.01996,0.21],"tcp_start":[0.46328,-0.01968,0.04629],"tcp_to_object_dist_end":0.02791,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47048,0.01948,0.00335],"object_pos_start":[0.47858,-0.02046,0.18289],"object_to_goal_dist_end":0.28331,"object_to_goal_dist_start":0.23597,"object_z_max":0.18303,"peak_contact_force":0.15997,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2882.0,"raw_peak_contact_force":1.98306,"tcp_end":[0.46726,-0.01984,0.23558],"tcp_start":[0.47193,-0.01996,0.21],"tcp_to_object_dist_end":0.23556,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `92fc0f2bbc35407e7976a239cbab7bb266e8a517486aa3be6bd6666f4c63f38d`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73832,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.28817,"approach_1.speed":0.07167,"grasp_1.grip_force":21.97811},"optimized_scores":{"best_composite_score":0.28746,"best_fitness_score":0.52746,"best_task_score":0.13003},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":104.0,"contact_point_centroid":[0.43896,-0.03527,-0.01018],"force_p95":1.55525,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.84945,"mean_force":0.70651,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.44996,-0.02576,0.22716]},{"body_a":"world","body_b":"grasp_target","contact_count":130.0,"contact_point_centroid":[0.45627,-0.02527,-0.00113],"force_p95":0.22168,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41063,"mean_force":0.05249,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44537,-0.02557,0.04896]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19618.0,"contact_point_centroid":[0.44833,-0.04475,0.12721],"force_p95":0.08003,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27965,"mean_force":0.05223,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44834,-0.02571,0.12581]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19263.0,"contact_point_centroid":[0.44952,-0.00664,0.12289],"force_p95":0.09181,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26928,"mean_force":0.0538,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44813,-0.0257,0.12272]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1027.0,"contact_point_centroid":[0.45213,-0.0447,0.20813],"force_p95":0.10484,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18958,"mean_force":0.05527,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.45319,-0.02589,0.20871]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02637,-0.00206],"force_p95":0.14069,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17993,"mean_force":0.12735,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44772,-0.02564,0.04819]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":758.0,"contact_point_centroid":[0.45398,-0.00728,0.20559],"force_p95":0.10207,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17592,"mean_force":0.06552,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.45318,-0.02589,0.20867]},{"body_a":"world","body_b":"grasp_target","contact_count":640.0,"contact_point_centroid":[0.45856,-0.02632,-0.0018],"force_p95":0.13763,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12339,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48302,-0.0095,0.2924]},{"body_a":"world","body_b":"grasp_target","contact_count":2896.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45928,-0.02286,0.16958]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5539.0,"contact_point_centroid":[0.44803,-0.0064,0.04833],"force_p95":0.06639,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1195,"mean_force":0.04006,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44658,-0.0256,0.04708]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5135.0,"contact_point_centroid":[0.44679,-0.0449,0.05006],"force_p95":0.07219,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08103,"mean_force":0.04279,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44658,-0.0256,0.04708]}],"total_contact_groups":11},"final_pose_error":0.01583,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.45537,-0.02281,0.01552],"final_tcp_position":[0.45445,-0.02594,0.21047],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":9.99515,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":161.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":9.99515,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":640.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.46601,-0.01997,0.2861],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.26027,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":724.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2896.0,"raw_peak_contact_force":0.12264,"tcp_end":[0.45455,-0.02583,0.05492],"tcp_start":[0.46601,-0.01997,0.2861],"tcp_to_object_dist_end":0.02918,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02609,0.02577],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30358,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14077,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12474.0,"raw_peak_contact_force":0.17993,"tcp_end":[0.44655,-0.0256,0.04705],"tcp_start":[0.45455,-0.02583,0.05492],"tcp_to_object_dist_end":0.02442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45996,-0.02687,0.18132],"object_pos_start":[0.45851,-0.02609,0.02577],"object_to_goal_dist_end":0.2979,"object_to_goal_dist_start":0.30358,"object_z_max":0.18113,"peak_contact_force":0.10897,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39011.0,"raw_peak_contact_force":0.41063,"tcp_end":[0.45445,-0.02594,0.21047],"tcp_start":[0.44655,-0.0256,0.04705],"tcp_to_object_dist_end":0.02968,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45537,-0.02281,0.01552],"object_pos_start":[0.45996,-0.02687,0.18132],"object_to_goal_dist_end":0.306,"object_to_goal_dist_start":0.2979,"object_z_max":0.18146,"peak_contact_force":0.32592,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1889.0,"raw_peak_contact_force":1.84945,"tcp_end":[0.44987,-0.02576,0.2365],"tcp_start":[0.45445,-0.02594,0.21047],"tcp_to_object_dist_end":0.22107,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3b2449a94ded39f3d450008c4da002b4ddf87103ab7d1b86900d116c316ff53`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27119,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11796,"approach_1.speed":0.02004,"grasp_1.grip_force":19.0904},"optimized_scores":{"best_composite_score":0.31667,"best_fitness_score":0.55667,"best_task_score":0.18374},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":132.0,"contact_point_centroid":[0.53286,0.00063,-0.00976],"force_p95":1.44852,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.52472,"mean_force":0.56764,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.53448,0.00093,0.21886]},{"body_a":"world","body_b":"grasp_target","contact_count":144.0,"contact_point_centroid":[0.54143,0.00098,-0.00112],"force_p95":0.32296,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47622,"mean_force":0.07313,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52815,0.0008,0.0449]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18679.0,"contact_point_centroid":[0.53354,0.02002,0.12637],"force_p95":0.07828,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32608,"mean_force":0.05431,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53235,0.00088,0.12398]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19827.0,"contact_point_centroid":[0.5329,-0.01819,0.12182],"force_p95":0.07559,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29907,"mean_force":0.05173,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53202,0.00088,0.11983]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1173.0,"contact_point_centroid":[0.53955,0.02016,0.20356],"force_p95":0.07514,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16356,"mean_force":0.04529,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5381,0.001,0.20196]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1173.0,"contact_point_centroid":[0.53902,-0.01815,0.20305],"force_p95":0.07502,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15834,"mean_force":0.0453,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5381,0.001,0.20196]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00118,-0.00203],"force_p95":0.13311,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15488,"mean_force":0.12546,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53072,0.00086,0.0447]},{"body_a":"world","body_b":"grasp_target","contact_count":2576.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.13005,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12282,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51704,0.00048,0.21175]},{"body_a":"world","body_b":"grasp_target","contact_count":884.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53632,0.00097,0.0888]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4840.0,"contact_point_centroid":[0.5307,-0.01822,0.04487],"force_p95":0.06847,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10497,"mean_force":0.04472,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52947,0.00083,0.04321]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4149.0,"contact_point_centroid":[0.53078,0.02004,0.04576],"force_p95":0.07493,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09449,"mean_force":0.05173,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52947,0.00083,0.04322]}],"total_contact_groups":11},"final_pose_error":0.0222,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.53801,0.00104,0.02405],"final_tcp_position":[0.53939,0.00102,0.20419],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":22.82926,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":645.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":22.82926,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2576.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53696,0.00098,0.12455],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09881,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":221.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":884.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53815,0.00101,0.05362],"tcp_start":[0.53696,0.00098,0.12455],"tcp_to_object_dist_end":0.02828,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54421,0.0011,0.02586],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25028,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.1331,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10789.0,"raw_peak_contact_force":0.15488,"tcp_end":[0.52944,0.00083,0.04318],"tcp_start":[0.53815,0.00101,0.05362],"tcp_to_object_dist_end":0.02276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54724,0.00118,0.18001],"object_pos_start":[0.54421,0.0011,0.02586],"object_to_goal_dist_end":0.1866,"object_to_goal_dist_start":0.25028,"object_z_max":0.17982,"peak_contact_force":0.07889,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38650.0,"raw_peak_contact_force":0.47622,"tcp_end":[0.53939,0.00102,0.20419],"tcp_start":[0.52944,0.00083,0.04318],"tcp_to_object_dist_end":0.02542,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53801,0.00104,0.02405],"object_pos_start":[0.54724,0.00118,0.18001],"object_to_goal_dist_end":0.25414,"object_to_goal_dist_start":0.1866,"object_z_max":0.18015,"peak_contact_force":0.1361,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2478.0,"raw_peak_contact_force":1.52472,"tcp_end":[0.53441,0.00093,0.22798],"tcp_start":[0.53939,0.00102,0.20419],"tcp_to_object_dist_end":0.20396,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```