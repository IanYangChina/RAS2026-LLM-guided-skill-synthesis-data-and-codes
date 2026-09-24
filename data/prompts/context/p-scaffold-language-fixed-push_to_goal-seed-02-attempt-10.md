## Search State

- **Seed**: 2
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5971 | 0.76 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5975 | 0.76 | ✅ accepted |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.2573 | 0.42 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5784 | 0.71 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5817 | 0.73 | ❌ rejected |

**Proposal policy**: task_score is 0.76 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: push_to_goal
- Frozen realised-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`
- Frozen object start: [0.47139345610991795, -0.0241810627903052, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.47139345610991795, -0.0241810627903052, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: push_box
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.05, 0.05, 0.05]
    mass_kg: 0.1
  - name: goal_marker
    role: target_marker
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.4714, -0.0242, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.47139345610991795, -0.0241810627903052, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0286, -0.1258, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.08, 0.00) | distance | — |
| contact | object | (0.00, 0.03, 0.00) | distance | — |
| push | goal | (0.00, 0.03, 0.00) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.597) — your mutation base

```yaml
skill: push_to_goal
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
- id: contact_1
  type: contact
  generator: impedance_motion
  control: admittance_control
  termination: contact_detected
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: 0.597
- **task_score** (E): 0.759
- **fitness_score**: 0.807  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2776 |
| contact_1 | 1.00 | 1.00 | 0.0490 |
| push_1 | 1.00 | 1.00 | 0.1417 |
| retract_1 | 0.00 | 1.00 | 0.1679 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.488, 0.059, 0.033) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.488, 0.059, 0.033)→(0.487, 0.011, 0.021) | (0.492, -0.018, 0.025)→(0.493, -0.026, 0.025) | 0.139→0.132 | 1.00 / 2.333 | 3.039 | 13.657 |
| push_1 | push | 1.00 / step_budget | (0.487, 0.011, 0.021)→(0.499, -0.125, 0.023) | (0.493, -0.026, 0.025)→(0.496, -0.150, 0.027) | 0.132→0.036 | 1.00 / 2.667 | 43.959 | 88.648 |
| retract_1 | retract | 0.00 / step_budget | (0.499, -0.125, 0.023)→(0.496, 0.015, 0.116) | (0.496, -0.150, 0.027)→(0.492, -0.148, 0.025) | 0.036→0.034 | 1.00 / 4.000 | 0.245 | 27.067 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.459
- goal_progress: 0.841
- terminal_score: 0.841
- phase_score: 0.853
- phase_breakdown.approach_score: 0.821
- phase_breakdown.push_score: 0.857
- phase_breakdown.contact_score: 0.869

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.848
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.841
- **Median Q (composite search score)**: 0.585
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.186


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `27920116be2b9a598fe307ae470bb0295293d051bb1ef513a0996a4d851f2459`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1a1e2536715050e6c37d8aed13e4ecd62004f6234f1413b07d7b475a233f55c9`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47139,-0.02418,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80723,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13937,"approach_1.speed":0.07271,"push_1.push_distance":0.10145},"optimized_scores":{"best_composite_score":0.63846,"best_fitness_score":0.84846,"best_task_score":0.84105},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1161.0,"contact_point_centroid":[0.48543,-0.11409,-0.0001],"force_p95":56.8437,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":71.09596,"mean_force":14.38534,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48162,-0.06718,0.01964]},{"body_a":"attachment","body_b":"push_box","contact_count":724.0,"contact_point_centroid":[0.48811,-0.06842,0.03436],"force_p95":40.98901,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.74506,"mean_force":15.85945,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47964,-0.05677,0.01978]},{"body_a":"push_box","body_b":"link7","contact_count":301.0,"contact_point_centroid":[0.50038,-0.04255,0.05123],"force_p95":38.96292,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.99658,"mean_force":29.16814,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47244,-0.01849,0.02047]},{"body_a":"attachment","body_b":"push_box","contact_count":86.0,"contact_point_centroid":[0.47441,-0.00287,0.03476],"force_p95":10.54339,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.31427,"mean_force":4.01643,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4669,0.009,0.02208]},{"body_a":"world","body_b":"push_box","contact_count":1904.0,"contact_point_centroid":[0.47139,-0.02542,-1e-05],"force_p95":1.20211,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.07789,"mean_force":0.43168,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46618,0.03057,0.0262]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.49143,-0.13735,0.02121],"force_p95":1.06388,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.08565,"mean_force":0.86793,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49433,-0.12582,0.01983]},{"body_a":"world","body_b":"push_box","contact_count":3989.0,"contact_point_centroid":[0.48345,-0.16208,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.93122,"mean_force":0.24601,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49209,-0.05806,0.07061]},{"body_a":"world","body_b":"push_box","contact_count":3528.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48365,0.02609,0.16646]}],"total_contact_groups":8},"final_pose_error":0.14055,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48344,-0.1621,0.02499],"final_tcp_position":[0.49374,0.01422,0.11422],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":71.09596,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":882.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3528.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.46887,0.05265,0.03399],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":524.0,"n_steps_budget":600.0,"object_pos_end":[0.47276,-0.03173,0.02498],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12137,"object_to_goal_dist_start":0.12903,"object_z_max":0.02512,"peak_contact_force":1.48736,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1990.0,"raw_peak_contact_force":13.31427,"tcp_end":[0.46714,0.00517,0.02144],"tcp_start":[0.46887,0.05265,0.03399],"tcp_to_object_dist_end":0.03749,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.48406,-0.16113,0.02509],"object_pos_start":[0.47276,-0.03173,0.02498],"object_to_goal_dist_end":0.01944,"object_to_goal_dist_start":0.12137,"object_z_max":0.03173,"peak_contact_force":0.43227,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2186.0,"raw_peak_contact_force":71.09596,"tcp_end":[0.49434,-0.12577,0.01984],"tcp_start":[0.46714,0.00517,0.02144],"tcp_to_object_dist_end":0.03719,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48344,-0.1621,0.02499],"object_pos_start":[0.48406,-0.16113,0.02509],"object_to_goal_dist_end":0.02051,"object_to_goal_dist_start":0.01944,"object_z_max":0.02509,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3991.0,"raw_peak_contact_force":1.08565,"tcp_end":[0.49374,0.01422,0.11422],"tcp_start":[0.49434,-0.12577,0.01984],"tcp_to_object_dist_end":0.19788,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e864853e179d3df1b19d9aaa17e18a5fe8c66fe7533fc0dd3a88a693de7416e7`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30645,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.14202,"approach_1.speed":0.05856,"push_1.push_distance":0.09455},"optimized_scores":{"best_composite_score":0.56786,"best_fitness_score":0.77786,"best_task_score":0.67336},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1373.0,"contact_point_centroid":[0.46134,-0.11444,-9e-05],"force_p95":41.00488,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.73462,"mean_force":8.16962,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47323,-0.07545,0.01958]},{"body_a":"attachment","body_b":"push_box","contact_count":639.0,"contact_point_centroid":[0.47475,-0.06908,0.03491],"force_p95":30.29365,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.70841,"mean_force":12.23328,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46657,-0.05753,0.01974]},{"body_a":"push_box","body_b":"link7","contact_count":277.0,"contact_point_centroid":[0.4813,-0.04638,0.05082],"force_p95":26.37108,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.04447,"mean_force":18.94839,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45404,-0.02309,0.02024]},{"body_a":"attachment","body_b":"push_box","contact_count":79.0,"contact_point_centroid":[0.45217,-0.01019,0.03178],"force_p95":10.72058,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.77808,"mean_force":4.32719,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44607,0.00169,0.02247]},{"body_a":"world","body_b":"push_box","contact_count":1929.0,"contact_point_centroid":[0.45038,-0.03252,-1e-05],"force_p95":1.46819,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.1683,"mean_force":0.42459,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44582,0.02308,0.02668]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.48744,-0.13654,0.02264],"force_p95":7.19345,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.19345,"mean_force":7.19345,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49336,-0.12649,0.01986]},{"body_a":"world","body_b":"push_box","contact_count":3988.0,"contact_point_centroid":[0.45811,-0.14717,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.07028,"mean_force":0.24768,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49133,-0.05949,0.07016]},{"body_a":"world","body_b":"push_box","contact_count":3696.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47372,0.02261,0.16667]}],"total_contact_groups":8},"final_pose_error":0.14325,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45814,-0.14719,0.02499],"final_tcp_position":[0.49319,0.01168,0.11337],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":55.73462,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":924.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3696.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.44889,0.04564,0.03442],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.45157,-0.03892,0.02507],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12118,"object_to_goal_dist_start":0.12843,"object_z_max":0.02515,"peak_contact_force":7.6292,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2008.0,"raw_peak_contact_force":15.77808,"tcp_end":[0.44622,-0.00217,0.0218],"tcp_start":[0.44889,0.04564,0.03442],"tcp_to_object_dist_end":0.03727,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.45855,-0.14671,0.02499],"object_pos_start":[0.45157,-0.03892,0.02507],"object_to_goal_dist_end":0.04158,"object_to_goal_dist_start":0.12118,"object_z_max":0.03218,"peak_contact_force":2.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2289.0,"raw_peak_contact_force":55.73462,"tcp_end":[0.49336,-0.12649,0.01986],"tcp_start":[0.44622,-0.00217,0.0218],"tcp_to_object_dist_end":0.04058,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45814,-0.14719,0.02499],"object_pos_start":[0.45855,-0.14671,0.02499],"object_to_goal_dist_end":0.04195,"object_to_goal_dist_start":0.04158,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3989.0,"raw_peak_contact_force":7.19345,"tcp_end":[0.49319,0.01168,0.11337],"tcp_start":[0.49336,-0.12649,0.01986],"tcp_to_object_dist_end":0.18515,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `c820cf29ab3e34ea9695cb40d5aba5de55f3ad951ee91f0df578ae7146ee7727`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80864,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.21596,"approach_1.speed":0.0875,"push_1.push_distance":0.13483},"optimized_scores":{"best_composite_score":0.58491,"best_fitness_score":0.79491,"best_task_score":0.76155},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":982.0,"contact_point_centroid":[0.56165,-0.05913,0.05487],"force_p95":130.70516,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":139.11366,"mean_force":87.06342,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52771,-0.04676,0.02416]},{"body_a":"world","body_b":"push_box","contact_count":1921.0,"contact_point_centroid":[0.55788,-0.09275,-0.00037],"force_p95":99.74789,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":112.12629,"mean_force":56.87204,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52751,-0.04778,0.02427]},{"body_a":"attachment","body_b":"push_box","contact_count":984.0,"contact_point_centroid":[0.54709,-0.0541,0.05384],"force_p95":89.08124,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":96.89097,"mean_force":59.15756,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52776,-0.0466,0.02415]},{"body_a":"push_box","body_b":"link7","contact_count":42.0,"contact_point_centroid":[0.55186,-0.12491,0.05717],"force_p95":52.80347,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":72.92152,"mean_force":20.18447,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50885,-0.12076,0.03108]},{"body_a":"world","body_b":"push_box","contact_count":3601.0,"contact_point_centroid":[0.53658,-0.13463,-2e-05],"force_p95":0.46324,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":70.20819,"mean_force":0.43646,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50367,-0.04797,0.08251]},{"body_a":"attachment","body_b":"push_box","contact_count":92.0,"contact_point_centroid":[0.52982,-0.11644,0.05967],"force_p95":33.37325,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.72964,"mean_force":7.24584,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50725,-0.11351,0.03588]},{"body_a":"attachment","body_b":"push_box","contact_count":91.0,"contact_point_centroid":[0.55369,0.02254,0.03744],"force_p95":10.35611,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.87964,"mean_force":3.11342,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5476,0.03448,0.02025]},{"body_a":"world","body_b":"push_box","contact_count":1882.0,"contact_point_centroid":[0.55325,-0.00042,-1e-05],"force_p95":1.01845,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.37026,"mean_force":0.40189,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54519,0.056,0.02334]},{"body_a":"world","body_b":"push_box","contact_count":3860.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52231,0.03845,0.16443]}],"total_contact_groups":9},"final_pose_error":0.13457,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53484,-0.13421,0.02499],"final_tcp_position":[0.5014,0.01901,0.11921],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":139.11366,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":965.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3860.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54659,0.07723,0.03107],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":529.0,"n_steps_budget":600.0,"object_pos_end":[0.55447,-0.00634,0.02517],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15364,"object_to_goal_dist_start":0.16043,"object_z_max":0.02518,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1973.0,"raw_peak_contact_force":11.87964,"tcp_end":[0.54816,0.03041,0.01978],"tcp_start":[0.54659,0.07723,0.03107],"tcp_to_object_dist_end":0.03767,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54683,-0.14166,0.03103],"object_pos_start":[0.55447,-0.00634,0.02517],"object_to_goal_dist_end":0.04795,"object_to_goal_dist_start":0.15364,"object_z_max":0.03113,"peak_contact_force":129.44515,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3887.0,"raw_peak_contact_force":139.11366,"tcp_end":[0.51014,-0.12306,0.02963],"tcp_start":[0.54816,0.03041,0.01978],"tcp_to_object_dist_end":0.04117,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53484,-0.13421,0.02499],"object_pos_start":[0.54683,-0.14166,0.03103],"object_to_goal_dist_end":0.03825,"object_to_goal_dist_start":0.04795,"object_z_max":0.03352,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3735.0,"raw_peak_contact_force":72.92152,"tcp_end":[0.5014,0.01901,0.11921],"tcp_start":[0.51014,-0.12306,0.02963],"tcp_to_object_dist_end":0.18295,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```