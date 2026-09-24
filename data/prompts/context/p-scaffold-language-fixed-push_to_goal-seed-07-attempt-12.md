## Search State

- **Seed**: 7
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2628 | 0.66 | ❌ rejected |
| 11 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | -0.2942 | 0.02 | ❌ rejected |
| 10 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2629 | 0.68 | ❌ rejected |
| 9 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2670 | 0.68 | ❌ rejected |
| 8 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2775 | 0.69 | ❌ rejected |

**Proposal policy**: task_score is 0.66 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`
- Frozen object start: [0.51501145599256, 0.047665656116349056, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.51501145599256, 0.047665656116349056, 0.025)
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
  frozen_object_start: [0.515, 0.0477, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.51501145599256, 0.047665656116349056, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.015, -0.1977, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752

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

## Current Skill (Q=0.263) — your mutation base

```yaml
skill: push_to_goal
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
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: admittance_control
  termination: contact_detected
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.263
- **task_score** (E): 0.664
- **fitness_score**: 0.623  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2852 |
| contact_1 | 1.00 | 1.00 | 0.0540 |
| push_1 | 1.00 | 1.00 | 0.1211 |
| retract_1 | 0.00 | 1.00 | 0.1353 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.105, 0.039) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.508, 0.105, 0.039)→(0.508, 0.055, 0.021) | (0.513, 0.027, 0.025)→(0.515, 0.018, 0.025) | 0.180→0.172 | 1.00 / 2.000 | 1.577 | 11.346 |
| push_1 | push | 1.00 / step_budget | (0.508, 0.055, 0.021)→(0.502, -0.064, 0.024) | (0.515, 0.018, 0.025)→(0.511, -0.099, 0.029) | 0.172→0.063 | 1.00 / 3.000 | 52.933 | 83.836 |
| retract_1 | retract | 0.00 / step_budget | (0.502, -0.064, 0.024)→(0.497, 0.053, 0.090) | (0.511, -0.099, 0.029)→(0.509, -0.095, 0.025) | 0.063→0.063 | 1.00 / 4.000 | 0.245 | 44.304 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.856
- lateral_force_integral: None
- approach_alignment: 0.486
- goal_progress: 0.756
- terminal_score: 0.756
- phase_score: 0.805
- phase_breakdown.push_score: 0.768
- phase_breakdown.approach_score: 0.820
- phase_breakdown.contact_score: 0.858

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.785
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.756
- **Median Q (composite search score)**: 0.200
- **K-run variance**: 0.0135
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.471


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `75e2389a1a667086aa2b9c0de482ff37adf5571150b90a83772692baadf8b52e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `154c216c563de6b8ee153943e5b668ca6d0c7dfd9253696b060f91a67dca06ec`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74713,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08648,"contact_1.speed":0.03687,"push_1.push_depth":0.08363,"push_1.push_distance":0.02683,"push_1.push_speed":0.07131,"retract_1.speed":0.09603},"optimized_scores":{"best_composite_score":0.16271,"best_fitness_score":0.52271,"best_task_score":0.58033},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1636.0,"contact_point_centroid":[0.52376,-0.04075,-0.00023],"force_p95":51.3439,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":71.47587,"mean_force":35.94407,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50467,0.01459,0.0224]},{"body_a":"push_box","body_b":"link7","contact_count":887.0,"contact_point_centroid":[0.53186,0.00117,0.05465],"force_p95":56.83665,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.10138,"mean_force":49.05118,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5048,0.01783,0.02216]},{"body_a":"attachment","body_b":"push_box","contact_count":897.0,"contact_point_centroid":[0.52434,0.00828,0.05321],"force_p95":53.39646,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.49481,"mean_force":40.46277,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50486,0.01846,0.02214]},{"body_a":"push_box","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.53093,-0.05696,0.05513],"force_p95":46.78676,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.80829,"mean_force":21.87342,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50049,-0.03366,0.0246]},{"body_a":"attachment","body_b":"push_box","contact_count":41.0,"contact_point_centroid":[0.52092,-0.04056,0.05588],"force_p95":37.17366,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.21277,"mean_force":9.01334,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49959,-0.03075,0.02546]},{"body_a":"world","body_b":"push_box","contact_count":3869.0,"contact_point_centroid":[0.50926,-0.06793,-2e-05],"force_p95":0.24563,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.11643,"mean_force":0.29365,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49694,0.03495,0.06711]},{"body_a":"attachment","body_b":"push_box","contact_count":166.0,"contact_point_centroid":[0.51622,0.06815,0.03611],"force_p95":8.70811,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.09328,"mean_force":4.0508,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50998,0.07999,0.02242]},{"body_a":"world","body_b":"push_box","contact_count":2917.0,"contact_point_centroid":[0.51524,0.04581,-1e-05],"force_p95":2.49652,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.51854,"mean_force":0.47958,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50815,0.10044,0.02937]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50346,0.07592,0.18046]}],"total_contact_groups":9},"final_pose_error":0.06552,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50898,-0.06729,0.02499],"final_tcp_position":[0.4968,0.09811,0.11012],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":71.47587,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5098,0.12494,0.04203],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0793,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":811.0,"n_steps_budget":930.0,"object_pos_end":[0.51697,0.0382,0.025],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.18897,"object_to_goal_dist_start":0.19823,"object_z_max":0.02508,"peak_contact_force":1.59337,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3083.0,"raw_peak_contact_force":10.09328,"tcp_end":[0.51049,0.07509,0.02083],"tcp_start":[0.5098,0.12494,0.04203],"tcp_to_object_dist_end":0.03768,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":900.0,"n_steps_budget":1000.0,"object_pos_end":[0.5114,-0.07205,0.02941],"object_pos_start":[0.51697,0.0382,0.025],"object_to_goal_dist_end":0.0789,"object_to_goal_dist_start":0.18897,"object_z_max":0.02942,"peak_contact_force":54.29537,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3420.0,"raw_peak_contact_force":71.47587,"tcp_end":[0.5011,-0.0346,0.0243],"tcp_start":[0.51049,0.07509,0.02083],"tcp_to_object_dist_end":0.03918,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50898,-0.06729,0.02499],"object_pos_start":[0.5114,-0.07205,0.02941],"object_to_goal_dist_end":0.08319,"object_to_goal_dist_start":0.0789,"object_z_max":0.02941,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3930.0,"raw_peak_contact_force":47.80829,"tcp_end":[0.4968,0.09811,0.11012],"tcp_start":[0.5011,-0.0346,0.0243],"tcp_to_object_dist_end":0.18642,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4d55d9375783bea830660bf0a13dfc76a97a0d4f5645e7ebcc1ef7143776d0b7`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24891,"average_solve_count":229.0,"average_success_count":229.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09077,"contact_1.speed":0.04964,"push_1.push_depth":0.09922,"push_1.push_distance":0.03449,"push_1.push_speed":0.03889,"retract_1.speed":0.01613},"optimized_scores":{"best_composite_score":0.20005,"best_fitness_score":0.56005,"best_task_score":0.65545},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1350.0,"contact_point_centroid":[0.49067,-0.03296,-0.0001],"force_p95":46.63481,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.86655,"mean_force":12.06725,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48497,0.01484,0.01974]},{"body_a":"attachment","body_b":"push_box","contact_count":850.0,"contact_point_centroid":[0.49248,0.01387,0.03525],"force_p95":33.91934,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.84315,"mean_force":13.06023,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48336,0.02521,0.01981]},{"body_a":"push_box","body_b":"link7","contact_count":376.0,"contact_point_centroid":[0.50627,0.03676,0.05152],"force_p95":33.92108,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.07657,"mean_force":23.0829,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47814,0.05993,0.02021]},{"body_a":"attachment","body_b":"push_box","contact_count":107.0,"contact_point_centroid":[0.478,0.07939,0.02894],"force_p95":13.31029,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.2595,"mean_force":5.72735,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47462,0.0912,0.02339]},{"body_a":"world","body_b":"push_box","contact_count":2214.0,"contact_point_centroid":[0.47951,0.05744,-1e-05],"force_p95":3.10158,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.65521,"mean_force":0.52269,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4736,0.11098,0.03073]},{"body_a":"world","body_b":"push_box","contact_count":3996.0,"contact_point_centroid":[0.48707,-0.07898,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59871,"mean_force":0.24573,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49224,0.00823,0.0497]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4851,0.08067,0.18133]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.49269,-0.05395,0.02116],"force_p95":0.22768,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.22768,"mean_force":0.22768,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49468,-0.04217,0.02009]}],"total_contact_groups":8},"final_pose_error":0.11732,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48707,-0.07898,0.02499],"final_tcp_position":[0.49361,0.05512,0.08129],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":54.86655,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.47584,0.13481,0.04323],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07856,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":596.0,"n_steps_budget":690.0,"object_pos_end":[0.48141,0.05017,0.02505],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20103,"object_to_goal_dist_start":0.2095,"object_z_max":0.02507,"peak_contact_force":1.50539,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2321.0,"raw_peak_contact_force":14.2595,"tcp_end":[0.47496,0.0868,0.02184],"tcp_start":[0.47584,0.13481,0.04323],"tcp_to_object_dist_end":0.03733,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":938.0,"n_steps_budget":1000.0,"object_pos_end":[0.48724,-0.07834,0.02504],"object_pos_start":[0.48141,0.05017,0.02505],"object_to_goal_dist_end":0.07279,"object_to_goal_dist_start":0.20103,"object_z_max":0.02915,"peak_contact_force":0.40207,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2576.0,"raw_peak_contact_force":54.86655,"tcp_end":[0.49468,-0.04217,0.02009],"tcp_start":[0.47496,0.0868,0.02184],"tcp_to_object_dist_end":0.03726,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48707,-0.07898,0.02499],"object_pos_start":[0.48724,-0.07834,0.02504],"object_to_goal_dist_end":0.07218,"object_to_goal_dist_start":0.07279,"object_z_max":0.02504,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3997.0,"raw_peak_contact_force":0.59871,"tcp_end":[0.49361,0.05512,0.08129],"tcp_start":[0.49468,-0.04217,0.02009],"tcp_to_object_dist_end":0.14559,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0a9238470f4497c7aa88b149b7cee960f9853513db10bf496723f5ea1d3a6043`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32258,"average_solve_count":217.0,"average_success_count":217.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06563,"contact_1.speed":0.03748,"push_1.push_depth":0.09996,"push_1.push_distance":0.08565,"push_1.push_speed":0.07532,"retract_1.speed":0.01645},"optimized_scores":{"best_composite_score":0.42549,"best_fitness_score":0.78549,"best_task_score":0.75589},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":993.0,"contact_point_centroid":[0.55565,-0.07509,0.05402],"force_p95":107.81901,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":125.16416,"mean_force":73.44422,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52269,-0.05799,0.02318]},{"body_a":"attachment","body_b":"push_box","contact_count":996.0,"contact_point_centroid":[0.5419,-0.06657,0.05343],"force_p95":85.57847,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":90.59033,"mean_force":50.05356,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52275,-0.0578,0.02317]},{"body_a":"push_box","body_b":"link7","contact_count":61.0,"contact_point_centroid":[0.54917,-0.12412,0.05591],"force_p95":78.80242,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.50523,"mean_force":31.55719,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50813,-0.11177,0.02926]},{"body_a":"world","body_b":"push_box","contact_count":1913.0,"contact_point_centroid":[0.54982,-0.10979,-0.00035],"force_p95":70.15471,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.0814,"mean_force":48.51954,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52231,-0.05972,0.02338]},{"body_a":"world","body_b":"push_box","contact_count":3649.0,"contact_point_centroid":[0.53054,-0.13778,-3e-05],"force_p95":0.29197,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":74.01271,"mean_force":0.56654,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50296,-0.04736,0.05483]},{"body_a":"attachment","body_b":"push_box","contact_count":74.0,"contact_point_centroid":[0.53181,-0.11488,0.06011],"force_p95":59.33869,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.0194,"mean_force":20.82577,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50762,-0.10967,0.02962]},{"body_a":"attachment","body_b":"push_box","contact_count":149.0,"contact_point_centroid":[0.54606,-0.0049,0.03828],"force_p95":7.41149,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.68529,"mean_force":2.78063,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53913,0.00698,0.02042]},{"body_a":"world","body_b":"push_box","contact_count":3048.0,"contact_point_centroid":[0.54454,-0.02747,-1e-05],"force_p95":1.44445,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.96458,"mean_force":0.3884,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53668,0.03053,0.02384]},{"body_a":"world","body_b":"push_box","contact_count":3944.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51722,0.04384,0.1705]}],"total_contact_groups":9},"final_pose_error":0.16019,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52984,-0.13776,0.02499],"final_tcp_position":[0.50118,0.00621,0.07941],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":125.16416,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":986.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3944.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53808,0.05612,0.03245],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":852.0,"n_steps_budget":960.0,"object_pos_end":[0.54717,-0.03441,0.0252],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.12484,"object_to_goal_dist_start":0.13211,"object_z_max":0.02521,"peak_contact_force":1.63142,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3197.0,"raw_peak_contact_force":9.68529,"tcp_end":[0.53966,0.00237,0.01981],"tcp_start":[0.53808,0.05612,0.03245],"tcp_to_object_dist_end":0.03792,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53576,-0.14538,0.03108],"object_pos_start":[0.54717,-0.03441,0.0252],"object_to_goal_dist_end":0.03656,"object_to_goal_dist_start":0.12484,"object_z_max":0.03106,"peak_contact_force":104.10125,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3902.0,"raw_peak_contact_force":125.16416,"tcp_end":[0.50929,-0.11622,0.0284],"tcp_start":[0.53966,0.00237,0.01981],"tcp_to_object_dist_end":0.03947,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52984,-0.13776,0.02499],"object_pos_start":[0.53576,-0.14538,0.03108],"object_to_goal_dist_end":0.03225,"object_to_goal_dist_start":0.03656,"object_z_max":0.03475,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3784.0,"raw_peak_contact_force":84.50523,"tcp_end":[0.50118,0.00621,0.07941],"tcp_start":[0.50929,-0.11622,0.0284],"tcp_to_object_dist_end":0.15656,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```