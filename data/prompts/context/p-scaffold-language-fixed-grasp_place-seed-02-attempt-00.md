## Search State

- **Seed**: 2
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → descend → grasp → lift → release | linear_cartesian | linear_cartesian | — | linear_cartesian | — | position_control | admittance_control | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | time_limit | 3 | 0.3008 | 0.15 | ✅ accepted |

**Proposal policy**: task_score is 0.15 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.240

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0865 |
| descend_1 | 1.00 | 1.00 | 0.1706 |
| grasp_1 | 1.00 | 1.00 | 0.0122 |
| lift_1 | 1.00 | 1.00 | 0.1628 |
| release_1 | 1.00 | 1.00 | 0.0256 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.491, -0.013, 0.225) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 5.185 | 0.138 |
| descend_1 | descend | 1.00 / step_budget | (0.491, -0.013, 0.225)→(0.488, -0.015, 0.055) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp_1 | grasp | 1.00 / step_budget | (0.488, -0.015, 0.055)→(0.480, -0.015, 0.046) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 46.667 | 0.137 | 0.172 |
| lift_1 | lift | 1.00 / step_budget | (0.480, -0.015, 0.046)→(0.489, -0.015, 0.208) | (0.493, -0.015, 0.026)→(0.495, -0.015, 0.181) | 0.281→0.240 | 1.00 / 35.333 | 0.090 | 0.439 |
| release_1 | release | 1.00 / step_budget | (0.489, -0.015, 0.208)→(0.484, -0.015, 0.233) | (0.495, -0.015, 0.181)→(0.488, -0.001, 0.015) | 0.240→0.281 | 1.00 / 2.333 | 0.203 | 1.792 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.183
- phase_score: 0.241
- phase_breakdown.transport_arc_score: 0.000
- phase_breakdown.approach_1_score: 0.011
- phase_breakdown.descend_1_score: 0.872
- phase_breakdown.release_1_score: 0.019
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.556

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.556
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.183
- **Median Q (composite search score)**: 0.298
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.275


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15569,"average_solve_count":167.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1488,"approach_1.speed":0.02972,"grasp_1.grip_force":17.7293},"optimized_scores":{"best_composite_score":0.29849,"best_fitness_score":0.53849,"best_task_score":0.15127},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":126.0,"contact_point_centroid":[0.47208,0.01965,-0.00899],"force_p95":1.17653,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.00581,"mean_force":0.54085,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.46732,-0.01985,0.23061]},{"body_a":"world","body_b":"grasp_target","contact_count":130.0,"contact_point_centroid":[0.47316,-0.01916,-0.00112],"force_p95":0.28772,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41979,"mean_force":0.06014,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46211,-0.01967,0.04809]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19859.0,"contact_point_centroid":[0.46573,-0.03894,0.12697],"force_p95":0.07336,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28305,"mean_force":0.05137,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4654,-0.01979,0.12517]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20169.0,"contact_point_centroid":[0.46666,-0.00068,0.12531],"force_p95":0.07668,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28166,"mean_force":0.0511,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46536,-0.01978,0.12452]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1621.0,"contact_point_centroid":[0.47159,0.00013,0.20745],"force_p95":0.10187,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1951,"mean_force":0.05717,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.47016,-0.01992,0.20765]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.02022,-0.00204],"force_p95":0.13689,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17004,"mean_force":0.12623,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46449,-0.01971,0.04749]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1116.0,"contact_point_centroid":[0.47109,-0.039,0.20883],"force_p95":0.07537,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1583,"mean_force":0.04492,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.47075,-0.01993,0.20822]},{"body_a":"world","body_b":"grasp_target","contact_count":1892.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13354,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12288,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48672,-0.00874,0.22985]},{"body_a":"world","body_b":"grasp_target","contact_count":1312.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47185,-0.01895,0.10609]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5095.0,"contact_point_centroid":[0.46485,-0.00052,0.04761],"force_p95":0.06738,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09714,"mean_force":0.04336,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46333,-0.01969,0.04631]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4882.0,"contact_point_centroid":[0.46352,-0.03893,0.0492],"force_p95":0.07126,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08501,"mean_force":0.04465,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.46333,-0.01969,0.04631]}],"total_contact_groups":11},"final_pose_error":0.01637,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.47067,0.01818,0.00418],"final_tcp_position":[0.47193,-0.01996,0.21],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":2.00581,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":474.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1892.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.47471,-0.01814,0.15824],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.13225,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":328.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1312.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47145,-0.01983,0.05464],"tcp_start":[0.47471,-0.01814,0.15824],"tcp_to_object_dist_end":0.02901,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47609,-0.02007,0.02582],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28848,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13694,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11777.0,"raw_peak_contact_force":0.17004,"tcp_end":[0.4633,-0.01969,0.04628],"tcp_start":[0.47145,-0.01983,0.05464],"tcp_to_object_dist_end":0.02413,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47859,-0.02046,0.18291],"object_pos_start":[0.47609,-0.02007,0.02582],"object_to_goal_dist_end":0.23598,"object_to_goal_dist_start":0.28848,"object_z_max":0.18271,"peak_contact_force":0.0811,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40158.0,"raw_peak_contact_force":0.41979,"tcp_end":[0.47193,-0.01996,0.21],"tcp_start":[0.4633,-0.01969,0.04628],"tcp_to_object_dist_end":0.0279,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47067,0.01818,0.00418],"object_pos_start":[0.47859,-0.02046,0.18291],"object_to_goal_dist_end":0.28331,"object_to_goal_dist_start":0.23598,"object_z_max":0.18305,"peak_contact_force":0.15563,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2863.0,"raw_peak_contact_force":2.00581,"tcp_end":[0.46727,-0.01984,0.23558],"tcp_start":[0.47193,-0.01996,0.21],"tcp_to_object_dist_end":0.23453,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67273,"average_solve_count":110.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.25654,"approach_1.speed":0.04982,"grasp_1.grip_force":26.95931},"optimized_scores":{"best_composite_score":0.28742,"best_fitness_score":0.52742,"best_task_score":0.12994},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":103.0,"contact_point_centroid":[0.4391,-0.0356,-0.01027],"force_p95":1.58471,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.84868,"mean_force":0.71295,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.44996,-0.02576,0.22717]},{"body_a":"world","body_b":"grasp_target","contact_count":130.0,"contact_point_centroid":[0.45627,-0.02527,-0.00113],"force_p95":0.22187,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41107,"mean_force":0.05246,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44535,-0.02556,0.04895]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19625.0,"contact_point_centroid":[0.44833,-0.04475,0.12722],"force_p95":0.07972,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28005,"mean_force":0.05222,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44833,-0.0257,0.12581]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19268.0,"contact_point_centroid":[0.44952,-0.00663,0.12293],"force_p95":0.09194,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26952,"mean_force":0.0538,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.44812,-0.02569,0.12275]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1040.0,"contact_point_centroid":[0.45217,-0.0447,0.20817],"force_p95":0.10479,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18921,"mean_force":0.05487,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.45319,-0.02589,0.2087]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02637,-0.00206],"force_p95":0.14089,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18015,"mean_force":0.12741,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.4477,-0.02563,0.04818]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":758.0,"contact_point_centroid":[0.45398,-0.00728,0.20558],"force_p95":0.10213,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1756,"mean_force":0.06545,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.45318,-0.02589,0.20866]},{"body_a":"world","body_b":"grasp_target","contact_count":744.0,"contact_point_centroid":[0.45856,-0.02632,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12328,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48288,-0.00951,0.28077]},{"body_a":"world","body_b":"grasp_target","contact_count":2592.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45868,-0.02311,0.15724]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5482.0,"contact_point_centroid":[0.44795,-0.0064,0.04824],"force_p95":0.06724,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11952,"mean_force":0.04045,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44656,-0.02559,0.04707]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5103.0,"contact_point_centroid":[0.44673,-0.04488,0.05001],"force_p95":0.07241,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07849,"mean_force":0.04301,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.44656,-0.02559,0.04707]}],"total_contact_groups":11},"final_pose_error":0.01583,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.45547,-0.02291,0.01527],"final_tcp_position":[0.45445,-0.02594,0.21047],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":15.31037,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":187.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":15.31037,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":744.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.46496,-0.02048,0.26115],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.23529,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":648.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2592.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45453,-0.02582,0.05491],"tcp_start":[0.46496,-0.02048,0.26115],"tcp_to_object_dist_end":0.02917,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45851,-0.02609,0.02577],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30358,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14083,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12385.0,"raw_peak_contact_force":0.18015,"tcp_end":[0.44653,-0.02559,0.04704],"tcp_start":[0.45453,-0.02582,0.05491],"tcp_to_object_dist_end":0.02442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45999,-0.02687,0.18133],"object_pos_start":[0.45851,-0.02609,0.02577],"object_to_goal_dist_end":0.29788,"object_to_goal_dist_start":0.30358,"object_z_max":0.18115,"peak_contact_force":0.1089,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":39023.0,"raw_peak_contact_force":0.41107,"tcp_end":[0.45445,-0.02594,0.21047],"tcp_start":[0.44653,-0.02559,0.04704],"tcp_to_object_dist_end":0.02967,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45547,-0.02291,0.01527],"object_pos_start":[0.45999,-0.02687,0.18133],"object_to_goal_dist_end":0.3061,"object_to_goal_dist_start":0.29788,"object_z_max":0.18147,"peak_contact_force":0.31699,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1901.0,"raw_peak_contact_force":1.84868,"tcp_end":[0.44987,-0.02576,0.2365],"tcp_start":[0.45445,-0.02594,0.21047],"tcp_to_object_dist_end":0.22131,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.25457,"approach_1.speed":0.09866,"grasp_1.grip_force":13.86882},"optimized_scores":{"best_composite_score":0.31645,"best_fitness_score":0.55645,"best_task_score":0.18318},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":150.0,"contact_point_centroid":[0.53017,0.00049,-0.00902],"force_p95":1.43275,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.52226,"mean_force":0.49918,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.53454,0.00075,0.21869]},{"body_a":"world","body_b":"grasp_target","contact_count":145.0,"contact_point_centroid":[0.54155,0.00034,-0.00112],"force_p95":0.33156,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.48489,"mean_force":0.07552,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.52876,0.00081,0.04533]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20243.0,"contact_point_centroid":[0.53307,0.01993,0.12197],"force_p95":0.07394,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31668,"mean_force":0.05073,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53231,0.0008,0.11942]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19893.0,"contact_point_centroid":[0.53295,-0.01835,0.12275],"force_p95":0.07484,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30078,"mean_force":0.0514,"phase_index":3.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.53237,0.0008,0.12037]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54431,0.00116,-0.00204],"force_p95":0.13396,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16629,"mean_force":0.12589,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53134,0.00087,0.04513]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1173.0,"contact_point_centroid":[0.53937,0.01998,0.20348],"force_p95":0.075,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16325,"mean_force":0.04528,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.53816,0.00082,0.20197]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1173.0,"contact_point_centroid":[0.53882,-0.01833,0.20297],"force_p95":0.07521,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.15798,"mean_force":0.04529,"phase_index":4.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.53816,0.00082,0.20197]},{"body_a":"world","body_b":"grasp_target","contact_count":972.0,"contact_point_centroid":[0.54431,0.00113,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12313,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51645,0.00045,0.2767]},{"body_a":"world","body_b":"grasp_target","contact_count":2404.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5354,0.00095,0.15404]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5602.0,"contact_point_centroid":[0.5301,-0.0184,0.04723],"force_p95":0.06421,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08261,"mean_force":0.03927,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53009,0.00084,0.04364]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5337.0,"contact_point_centroid":[0.52992,0.02014,0.04769],"force_p95":0.06387,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08063,"mean_force":0.04145,"phase_index":2.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.53009,0.00084,0.04364]}],"total_contact_groups":11},"final_pose_error":0.02215,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.5369,0.0008,0.02431],"final_tcp_position":[0.53945,0.00084,0.2042],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":1.52226,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":244.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":972.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53444,0.00091,0.2556],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":601.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2404.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.53878,0.00102,0.05409],"tcp_start":[0.53444,0.00091,0.2556],"tcp_to_object_dist_end":0.02861,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":49.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54422,0.0009,0.02584],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25042,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13379,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12739.0,"raw_peak_contact_force":0.16629,"tcp_end":[0.53006,0.00085,0.04361],"tcp_start":[0.53878,0.00102,0.05409],"tcp_to_object_dist_end":0.02272,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54709,0.00099,0.17999],"object_pos_start":[0.54422,0.0009,0.02584],"object_to_goal_dist_end":0.18684,"object_to_goal_dist_start":0.25042,"object_z_max":0.1798,"peak_contact_force":0.07877,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40281.0,"raw_peak_contact_force":0.48489,"tcp_end":[0.53945,0.00084,0.2042],"tcp_start":[0.53006,0.00085,0.04361],"tcp_to_object_dist_end":0.02539,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.5369,0.0008,0.02431],"object_pos_start":[0.54709,0.00099,0.17999],"object_to_goal_dist_end":0.25459,"object_to_goal_dist_start":0.18684,"object_z_max":0.18013,"peak_contact_force":0.13493,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2496.0,"raw_peak_contact_force":1.52226,"tcp_end":[0.53447,0.00075,0.22799],"tcp_start":[0.53945,0.00084,0.2042],"tcp_to_object_dist_end":0.20369,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```